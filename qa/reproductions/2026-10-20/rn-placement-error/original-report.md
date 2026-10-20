# iOS placement lookup resolves successfully when the native SDK reports an error

**Affected:** [RevenueCat/react-native-purchases](https://github.com/RevenueCat/react-native-purchases), 10.15.0, commit `cd5de3d7d78ae9b8b8655b3ae2432953be72e85d`, iOS. Reproduced with React Native 0.87.1 / Hermes / new architecture, PurchasesHybridCommon 19.12.0, RevenueCat iOS 5.95.0, on an iOS 27.1 simulator.

**Reproduction client:** the included `app/` native React Native app. It uses only project **SDK Bug Reporter** (`proj602cc762`), its [Test Store app `app4ca00b430f`](https://app.revenuecat.com/projects/602cc762/apps/app4ca00b430f), and generated synthetic users. No purchases or backend configuration changes were made.

## Reproduce

1. Launch the app and select **Network error case**. The app calls `Purchases.setProxyURL('http://127.0.0.1:1')` before configuration to produce a real connection refusal; no proxy/server, mocked transport or callback injection is involved.
2. Configure the dedicated Test Store SDK key with a fresh synthetic user.
3. Call `getOfferings()`, then `getCurrentOfferingForPlacement('qa_network_error_control')`.

**Expected:** both calls reject with the native error. **Actual:** `getOfferings()` rejects with code `33` (`API_ENDPOINT_BLOCKED`); placement lookup resolves successfully with `undefined`, losing the error. The same app's online control successfully fetches customer info, offerings and the default placement result.

**Impact:** callers cannot distinguish a failed offerings request from absence of an offering and do not enter their error/retry path.

## Cause and suggested solution

`ios/RNPurchases.m` ignores the `RCErrorContainer *error` argument and unconditionally calls `resolve(offeringObject)`. Route this callback through the existing `getResponseCompletionBlockWithResolve:reject:` helper. Patch: `fixes/native-error.patch`. The separate null-result issue requires its own fix.

## Tests and evidence

- `python3 native-regression.py WORKTREE before`: actual extracted Objective-C bridge/helper bodies, **3 passing controls / 3 failing error cases**. Applying the native patch makes **6/6 pass**.
- `python3 reproduce.py before`: native UI regression fails; `python3 reproduce.py native-fixed`: this error test passes, while the separate No Offering test still fails. `python3 reproduce.py fixed`: **3/3 UI tests pass**.
- Before: `evidence/before-network-error.png`, `evidence/before-network-error.mp4`. After: `evidence/fixed-network-error.png`, `evidence/fixed-network-error.mp4`.
- Actual app command/results and observations: `verification/app-two-before-tests.json`, `verification/app-native-fixed-verified-tests.json`, `verification/app-all-fixed-tests.json`, and corresponding logs. Host regressions explicitly use callback-provider/dependency shims; app evidence does not.

## Introduced in

Present since placement support was introduced. The earliest feature implementation is `91c21caea7228a4bf8cd8682d0dd5141618f11bd` in [PR #925](https://github.com/RevenueCat/react-native-purchases/pull/925); it entered the default branch in `a3d1f06386a6726a83c9cc89372b885a157c16ed` through [PR #938](https://github.com/RevenueCat/react-native-purchases/pull/938) on **2024-03-13**. First affected stable source tag: **7.24.0**, released **2024-03-14**. Both introducing parents lack the placement method, so this is a defect present from feature introduction, not a regression from a working placement implementation.

Historical host execution of the actual feature and default-branch introducing Objective-C method bodies reproduces all three swallowed-error cases; three success controls pass. The pinned shared implementation already supplied an error separately from the offering. Evidence: `history/`, `native-boundary/`. No complete historical mobile app was built.

**Limitations:** current native reproduction covers a real blocked-endpoint error. Configuration/credential errors were exercised only in the host boundary regression. No Android, physical device, live-store or production purchase testing. All fixes remain local and production source was restored.

## Latest upstream recheck — 2026-10-20

**still-reproduces** at `cd5de3d7d78ae9b8b8655b3ae2432953be72e85d`. Actual current Objective-C methods: 3 error cases resolve incorrectly; 3 success controls pass. Callback-provider shim.

Verification: Local regression revalidation; no new full mobile-app, backend, Android or physical-device execution. Evidence: `revalidation/2026-10-20/native-boundary/latest/summary.json`.
