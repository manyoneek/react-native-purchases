# React Native iOS: native paywall errors violate the public string-code contract

- **Finding:** RC-RN-20261013-001 (existing finding; upgraded app verification).
- **Repository / commit:** RevenueCat/react-native-purchases, `dffdb082054c9d9d71287e72a6565c422485a3d8` (10.13.0).
- **Platform:** React Native 0.87.1, iOS 27.1 simulator, Purchases iOS 5.95.0 / hybrid-common 19.11.0.

## Expected / actual
`onPurchaseError` exposes `PurchasesError`, whose code is the public string-valued `PURCHASES_ERROR_CODE` enum. A native Test Store failed purchase delivers numeric `42`, while the matching public enum is string `"42"`; strict equality is false.

## Reproduce
Build `react-native-app` using the bundle README. Launch the app, choose **1. Error callback types**, tap **Subscribe**, then **Test failed purchase** in the native Test Store dialog. Read the real callback values on the result screen. No callback payload is injected.

## Tests and evidence
`xcodebuild ... -scheme QAReproduction ... test-without-building` (full commands in README) runs two UI characterization tests. The original app tests pass by asserting the defects: this test verifies `typeof=number` and strict equality false. See `rn-error-callback.png`, the matching video, and native test log.
Earlier implementation-level regression: four contract assertions failed before normalization; the temporary fix passed all 39 UI Jest tests. Existing core baseline: 268 passed.

## Suggested fix / impact
Normalize native numeric error codes to the public string enum before invoking JavaScript error callbacks. Apply the same conversion to full and footer purchase/restore handlers. Patch: `fixes/error-normalization-fix.patch` (or combined patch).
App code using the documented enum in a switch or strict comparison misses the error branch.

## Verification limits
The actual app covers the full-screen **purchase-error** callback and Test Store error 42. Restore, footer, Android, physical devices and production stores were not app-tested. Earlier focused handler tests cover additional callbacks. Dedicated synthetic Test Store only; no real charges.

## Proposed-fix app validation
The same two actual Test Store flows were rerun with the proposed normalization and optional declaration plus guarded consumer. Both updated XCTest assertions passed; `xcodebuild` exited 0. The error callback reports string code and strict equality true; the custom-purchase flow retains an active entitlement and safely handles the absent transaction. See `native-fixed-recorded-test.log` and `*-fixed` evidence.
