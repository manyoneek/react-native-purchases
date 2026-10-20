# iOS “No Offering” placements return undefined despite the nullable contract

**Affected:** [RevenueCat/react-native-purchases](https://github.com/RevenueCat/react-native-purchases), 10.15.0, commit `cd5de3d7d78ae9b8b8655b3ae2432953be72e85d`, iOS. Reproduced with React Native 0.87.1 / Hermes / new architecture, PurchasesHybridCommon 19.12.0, RevenueCat iOS 5.95.0, on an iOS 27.1 simulator.

**Reproduction client:** the included `app/` native React Native app. It uses only project **SDK Bug Reporter** (`proj602cc762`), its [Test Store app `app4ca00b430f`](https://app.revenuecat.com/projects/602cc762/apps/app4ca00b430f), and generated synthetic users. No purchases or backend configuration changes were made.

## Reproduce

1. Launch the app and select **No offering case**. It configures a synthetic user, gets real customer info and fetches nonempty offerings.
2. Call `getCurrentOfferingForPlacement('sdk_bug_reporter_none_20261018')`. The project's existing [targeting rule](https://app.revenuecat.com/projects/602cc762/targeting/tvpeenTzcQ) explicitly assigns this placement **No Offering** and preserves the default offering.
3. Read the result using the declared contract:
   ```ts
   const label = offering !== null ? offering.identifier : 'No offering';
   ```

**Expected:** the returned value is `null`, as declared by `Promise<PurchasesOffering | null>`, and the consumer selects “No offering”. **Actual:** the value is `undefined`; strict equality with null is false, and the type-correct consumer throws `TypeError: Cannot read property 'identifier' of undefined`.

**Impact:** legitimate targeted no-paywall flows can crash code that handles the SDK's documented nullable result correctly.

## Cause and suggested solution

The iOS bridge resolves a nil offering, which arrives in JavaScript as undefined. The public wrapper returns it unchanged. Normalize a successful nullish result after awaiting the native call:

```ts
const offering = await RNPurchases.getCurrentOfferingForPlacement(placementIdentifier);
return offering ?? null;
```

This preserves errors as rejections and leaves present offerings unchanged. Patch: `fixes/null-result.patch`. Apply the independent native error patch as well to stop errors being mistaken for absent offerings.

## Tests and evidence

- `corepack yarn test --runInBand`: original core **272/272 pass**; with nine added regressions **280 pass / 1 fails**. With null normalization **281/281 pass**; `corepack yarn build` also passes.
- The native No Offering UI test fails on the affected SDK and also with the error-only fix. With both scoped fixes, **3/3 UI tests pass**, including the unchanged online default-offering control.
- `python3 reproduce.py before` / `python3 reproduce.py fixed` builds the actual packaged native app and executes those cases.
- Before: `evidence/before-no-offering.png`, `evidence/before-no-offering.mp4`. After: `evidence/fixed-no-offering.png`, `evidence/fixed-no-offering.mp4`.
- The JS regression injects only native transport output and is not itself an app reproduction. The separate simulator evidence uses the actual SDK, real dedicated Test Store response and existing targeting rule.

## Introduced in

Present since placement support was introduced. The earliest feature implementation is `91c21caea7228a4bf8cd8682d0dd5141618f11bd` in [PR #925](https://github.com/RevenueCat/react-native-purchases/pull/925); it entered the default branch in `a3d1f06386a6726a83c9cc89372b885a157c16ed` through [PR #938](https://github.com/RevenueCat/react-native-purchases/pull/938) on **2024-03-13**. First affected stable source tag: **7.24.0**, released **2024-03-14**. Both introducing parents lack the placement method, so this is a defect present from feature introduction, not a regression from a working placement implementation.

The initial public method already declared `PurchasesOffering | null`. Its iOS bridge passed nil unchanged. The actual React Native **0.73.5** resolver code (the introducing default-branch revision's development dependency) was compiled on macOS: nil produces an empty callback argument array, whereas `NSNull` produces `[null]`. Feeding those serialized arguments through Promise resolution and the actual historical RevenueCat public method reproduces undefined for nil and preserves the null control. This is historical boundary execution with dependency/transport shims, not a full historical app or a claim about every supported React Native version. Sources, dependency provenance and results are in `history/`.

**Limitations:** current full app reproduction is native iOS only; no Android, physical devices, web execution or purchases. All fixes remain local and production source was restored. The similar previously reported Capacitor defect has a different bridge implementation and fingerprint.

## Latest upstream recheck — 2026-10-20

**still-reproduces** at `cd5de3d7d78ae9b8b8655b3ae2432953be72e85d`. Actual current JS wrapper: null-normalization assertion fails, 8 controls pass. Same commit as this morning’s full native-app reproduction; that app was not rerun in this recheck.

Verification: Local regression revalidation; no new full mobile-app, backend, Android or physical-device execution. Evidence: `revalidation/2026-10-20/logs/react-native-purchases-placement-regression.log`.
