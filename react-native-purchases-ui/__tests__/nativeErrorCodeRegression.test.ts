import type { ReactElement } from 'react';
import { PURCHASES_ERROR_CODE } from '@revenuecat/purchases-typescript-internal';

// Fixtures are emitted by compiled production ErrorContainer.swift (19.11.0)
// and RNPaywallEventForwarder.m. See native-boundary/build-fixtures.py.
const nativeEvents = require('./native-boundary/events.json');
type Listener = (body: unknown) => void;
const mockListeners = new Map<string, Set<Listener>>();
let resolvePresentation: (result: string) => void = () => {};
const mockRNPaywalls = {
  presentPaywall: jest.fn((..._args: unknown[]) => new Promise<string>(resolve => {
    resolvePresentation = resolve;
  })),
};

jest.mock('react-native', () => ({
  NativeModules: { RNPaywalls: mockRNPaywalls, RNCustomerCenter: {} },
  NativeEventEmitter: class {
    addListener(name: string, listener: Listener) {
      if (!mockListeners.has(name)) mockListeners.set(name, new Set());
      mockListeners.get(name)!.add(listener);
      return { remove: () => mockListeners.get(name)!.delete(listener) };
    }
  },
  Platform: { OS: 'ios' },
  UIManager: { getViewManagerConfig: () => ({}) },
  requireNativeComponent: (name: string) => name,
  View: 'View', ScrollView: 'ScrollView',
}));
jest.mock('../src/preview/nativeModules', () => ({ previewNativeModuleRNPaywalls: {}, previewNativeModuleRNCustomerCenter: {} }));
jest.mock('../src/preview/previewComponents', () => ({ PreviewPaywall: () => null, PreviewCustomerCenter: () => null }));

import RevenueCatUI, { type PaywallCallbacks } from '../src/index';

// Both functions are production React function components without hooks. Invoke
// them to obtain actual native event-handler props; do not reimplement routing.
function embeddedNativeProps(callbacks: PaywallCallbacks): Record<string, (event: unknown) => void> {
  const publicElement = RevenueCatUI.Paywall(callbacks) as ReactElement;
  const internalComponent = publicElement.type as (props: unknown) => ReactElement;
  return internalComponent(publicElement.props).props;
}

beforeEach(() => {
  mockListeners.clear();
  jest.clearAllMocks();
});

describe('native UI boundary regression: error codes', () => {
  it.each(['onPurchaseError', 'onRestoreError'] as const)(
    'embedded %s delivers the public string NETWORK_ERROR code', callbackName => {
      const callback = jest.fn();
      const props = embeddedNativeProps({ [callbackName]: callback });
      props[callbackName]!({ nativeEvent: nativeEvents[callbackName] });
      expect(callback).toHaveBeenCalledTimes(1);
      expect(callback.mock.calls[0][0].error.code).toBe(PURCHASES_ERROR_CODE.NETWORK_ERROR);
    });

  it.each(['onPurchaseError', 'onRestoreError'] as const)(
    'presented %s delivers the public string NETWORK_ERROR code', async callbackName => {
      const callback = jest.fn();
      const presented = RevenueCatUI.presentPaywall({ callbacks: { [callbackName]: callback } });
      const args = mockRNPaywalls.presentPaywall.mock.calls[0]!;
      const presentationId = args[args.length - 2];
      mockListeners.get('Paywalls-' + callbackName)!.forEach(listener => {
        listener({ ...nativeEvents[callbackName], presentationId });
      });
      resolvePresentation('CANCELLED');
      await presented;
      expect(callback).toHaveBeenCalledTimes(1);
      expect(callback.mock.calls[0][0].error.code).toBe(PURCHASES_ERROR_CODE.NETWORK_ERROR);
    });
});
