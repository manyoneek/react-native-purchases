const nativePlugin = {
  getCurrentOfferingForPlacement: jest.fn(),
  getCachedVirtualCurrencies: jest.fn(),
  trackCustomPaywallImpression: jest.fn(() => Promise.resolve()),
  redeemWebPurchase: jest.fn(),
};
jest.mock('@capacitor/core', () => ({ registerPlugin: () => nativePlugin }));
import { Purchases } from '../src/index';

describe('native result and option preservation', () => {
  beforeEach(() => jest.clearAllMocks());

  it('preserves a null placement result and the requested placement', async () => {
    nativePlugin.getCurrentOfferingForPlacement.mockResolvedValueOnce(null);
    await expect(Purchases.getCurrentOfferingForPlacement({ placementIdentifier: 'onboarding' })).resolves.toBeNull();
    expect(nativePlugin.getCurrentOfferingForPlacement).toHaveBeenCalledWith({ placementIdentifier: 'onboarding' });
  });

  it('preserves an empty currency cache without converting it to an empty balance', async () => {
    const result = { cachedVirtualCurrencies: null };
    nativePlugin.getCachedVirtualCurrencies.mockResolvedValueOnce(result);
    await expect(Purchases.getCachedVirtualCurrencies()).resolves.toBe(result);
  });

  it('preserves zero balances and result identity', async () => {
    const result = { cachedVirtualCurrencies: { all: { CREDIT: { balance: 0, code: 'CREDIT', name: 'Credits', serverDescription: null } } } };
    nativePlugin.getCachedVirtualCurrencies.mockResolvedValueOnce(result);
    await expect(Purchases.getCachedVirtualCurrencies()).resolves.toBe(result);
  });

  it('normalizes a rejected native placement error without resolving it', async () => {
    nativePlugin.getCurrentOfferingForPlacement.mockRejectedValueOnce({ code: 10, message: 'Network unavailable' });
    await expect(Purchases.getCurrentOfferingForPlacement({ placementIdentifier: 'onboarding' })).rejects.toMatchObject({ code: '10', message: 'Network unavailable', userCancelled: false });
  });

  it('passes a custom impression without optional identifiers', async () => {
    await Purchases.trackCustomPaywallImpression();
    expect(nativePlugin.trackCustomPaywallImpression).toHaveBeenCalledWith({});
  });

  it('passes explicit offering and paywall identifiers', async () => {
    await Purchases.trackCustomPaywallImpression({ offeringId: 'offer', paywallId: 'paywall' });
    expect(nativePlugin.trackCustomPaywallImpression).toHaveBeenCalledWith({ offeringId: 'offer', paywallId: 'paywall' });
  });

  it('keeps successful redemption payload identity', async () => {
    const result = { result: 'SUCCESS', customerInfo: { originalAppUserId: 'synthetic' } };
    nativePlugin.redeemWebPurchase.mockResolvedValueOnce(result);
    await expect(Purchases.redeemWebPurchase({ webPurchaseRedemption: { redemptionLink: 'https://pay.rev.cat/redeem/example' } })).resolves.toBe(result);
  });

  it('normalizes redemption transport rejection separately from resolved errors', async () => {
    nativePlugin.redeemWebPurchase.mockRejectedValueOnce({ code: 10, message: 'Offline' });
    await expect(Purchases.redeemWebPurchase({ webPurchaseRedemption: { redemptionLink: 'https://pay.rev.cat/redeem/example' } })).rejects.toMatchObject({ code: '10', message: 'Offline' });
  });
});
