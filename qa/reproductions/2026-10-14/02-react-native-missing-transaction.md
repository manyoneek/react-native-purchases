# React Native iOS: purchase completion declares a transaction that can be absent

- **Finding:** RC-RN-20261013-002 (existing finding; upgraded app verification).
- **Repository / commit:** RevenueCat/react-native-purchases, `dffdb082054c9d9d71287e72a6565c422485a3d8` (10.13.0).
- **Platform:** React Native 0.87.1, iOS 27.1 simulator, Purchases iOS 5.95.0 / hybrid-common 19.11.0.

## Expected / actual
The callback declaration requires `storeTransaction: PurchasesStoreTransaction`, allowing a strict-TypeScript consumer to read `.transactionIdentifier` without a guard. The native custom-purchase completion path legitimately has no transaction. The actual callback supplies `undefined`; the type-accepted consumer throws `TypeError` after a successful purchase and active entitlement.

## Reproduce
Build `react-native-app` using the README. Choose **2. Missing transaction**, tap **Subscribe**, then **Test valid purchase**. Custom purchase logic calls the real `Purchases.purchasePackage`, receives success, then returns `PURCHASE_LOGIC_RESULT.SUCCESS`. The native paywall invokes the actual completion callback. The result screen shows entitlement active=true, transaction undefined, and the caught consumer exception.

## Tests and evidence
`npx tsc --noEmit` accepts the original unsafe consumer. The `QAReproduction` XCTest suite's second characterization test asserts the absent transaction, active entitlement and TypeError. Screenshots/video and test logs are included.
Earlier targeted nullability regression failed before the declaration correction and passed afterward; broader repository API-fixture assumptions were not all resolved.

## Suggested fix / impact
Declare `storeTransaction` optional in both completion callback declarations and require consumers to guard it. Do not manufacture a transaction. Patch: `fixes/nullability-diagnostic-fix.patch` (or combined patch).
A successful purchase can trigger an exception in code accepted by the published TypeScript API.

## Verification limits
Actual execution covers full-screen custom-purchase completion on the iOS simulator and dedicated Test Store. No claim about Android, footer runtime behavior, physical devices or real-store transactions. The app catches the exception to keep the observed result visible; an uncaught application crash was not asserted.

## Proposed-fix app validation
The same two actual Test Store flows were rerun with the proposed normalization and optional declaration plus guarded consumer. Both updated XCTest assertions passed; `xcodebuild` exited 0. The error callback reports string code and strict equality true; the custom-purchase flow retains an active entitlement and safely handles the absent transaction. See `native-fixed-recorded-test.log` and `*-fixed` evidence.
