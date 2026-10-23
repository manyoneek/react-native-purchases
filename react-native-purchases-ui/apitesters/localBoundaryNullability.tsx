import type { PaywallCallbacks } from '../src/index';

const callback: NonNullable<PaywallCallbacks['onPurchaseCompleted']> = ({ storeTransaction }) => {
  // @ts-expect-error A transaction may be absent.
  void storeTransaction.transactionIdentifier;
};
void callback;
