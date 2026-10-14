import type { ReactElement } from 'react';

// Fixtures are emitted by compiled production ErrorContainer.swift (19.11.0)
// and RNPaywallEventForwarder.m. See native-boundary/build-fixtures.py.
const nativeEvents = require('./native-boundary/events.json');
type Listener = (body: unknown) => void;
const mockListeners = new Map<string, Set<Listener>>();
const mockRNPaywalls = {};

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

describe('native UI boundary characterization: nullable transaction', () => {
  it('preserves the transaction when the native callback supplies it', () => {
    const callback = jest.fn();
    embeddedNativeProps({ onPurchaseCompleted: callback }).onPurchaseCompleted!({
      nativeEvent: nativeEvents.completedWithTransaction,
    });
    expect(callback.mock.calls[0][0].storeTransaction.transactionIdentifier).toBe('local-transaction');
  });

  it('delivers undefined for a native nil transaction', () => {
    const callback = jest.fn();
    embeddedNativeProps({ onPurchaseCompleted: callback }).onPurchaseCompleted!({
      nativeEvent: nativeEvents.completedWithoutTransaction,
    });
    expect(callback).toHaveBeenCalledTimes(1);
    expect(callback.mock.calls[0][0].storeTransaction).toBeUndefined();
    expect(callback.mock.calls[0][0].customerInfo.originalAppUserId).toBe('local-fixture');
  });

  it('reproduces the crash in an unguarded consumer accepted by the public callback type', () => {
    const consumer: NonNullable<PaywallCallbacks['onPurchaseCompleted']> = ({ storeTransaction }) => {
      // @ts-expect-error Deliberately unsafe consumer: the corrected API must reject it.
      void storeTransaction.transactionIdentifier;
    };
    expect(() => embeddedNativeProps({ onPurchaseCompleted: consumer }).onPurchaseCompleted!({
      nativeEvent: nativeEvents.completedWithoutTransaction,
    })).toThrow(TypeError);
  });
});
