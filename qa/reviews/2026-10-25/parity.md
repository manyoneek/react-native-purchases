# Contract comparison — October 25, 2026

| Implementation | Pinned revision | No Offering behavior / applicability |
|---|---|---|
| React Native 10.15.1 | `bde1095e84113c07569c0aab6858171768cb9aaf` | `Promise<PurchasesOffering \| null>` forwards native output. Actual iOS app returns undefined; the proposed wrapper normalization returns null. |
| React Native browser adapter | same revision | `src/browser/nativeModule.ts` explicitly returns null when no offering exists. Existing browser tests ran as part of the core suite; no separate browser app was run today. |
| Shared iOS/Android | `ed23f3f08d1abe97d0ebe591b708bb984f8c2ced` | iOS `getCurrentOffering` completes with an optional dictionary; Android `getCurrentOfferingForPlacement` calls the nullable-result callback with null. Shared iOS 19.15.1 is the native app's resolved dependency. |
| Native iOS | `c4f9551c86168cea9ced4b69dd56d177a2114574` | `Offerings.currentOffering(forPlacement:)` returns nil for an explicitly empty placement and uses fallback only for an absent placement key. The real app resolves RevenueCat 5.98.0. |
| Native Android | `517a51e43484ce7edd27808ca79b15c64b944eda` | `Offerings.getCurrentOfferingForPlacement` preserves explicit empty placements as null; fallback is for absent keys. Source comparison only for this flow. |
| KMP | `1de077dc284d5c98e57ba5c6e991d470f32ba228` | `Offerings.getCurrentOfferingForPlacement` delegates to a nullable function. Semantic equivalent exists; no missing API report. Source-only comparison. |

The null fix preserves public declarations, existing offering object identity, and Promise rejection. It requires no consumer migration. Native iOS error propagation remains the distinct upstream PR #2054.

Android virtual-currency spending is marked `@InternalRevenueCatAPI`; iOS exposes it through `@_spi(Internal)` with IAM required. Its absence from the ordinary React Native public surface is not a verified public parity gap. Android's per-user request queue was tested directly on the JVM. Backend spending and Android app integration were not executed.
