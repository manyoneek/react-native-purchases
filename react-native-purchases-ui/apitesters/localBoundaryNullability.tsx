import type { PaywallCallbacks } from '../src/index';

// A native nil transaction must be represented in the public callback type.
// On the affected commit this fails with "Unused '@ts-expect-error' directive":
// TypeScript permits dereferencing a value that can be undefined at runtime.
const callback: NonNullable<PaywallCallbacks['onPurchaseCompleted']> = ({ storeTransaction }) => {
  // @ts-expect-error The public type should require a null/undefined guard.
  void storeTransaction.transactionIdentifier;
};
void callback;
