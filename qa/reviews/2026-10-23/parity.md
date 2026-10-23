# SDK contract comparison — October 23, 2026

## Source revisions

- KMP: `1de077dc284d5c98e57ba5c6e991d470f32ba228`. Its pinned Android SDK is 10.29.0; its iOS submodule is `0c9d395d056a726e4ed38622214cf90f7f136ec8` (5.97.0).
- Capacitor: `ba38d294a900c8a50024e15a023c3e954b5060d5`; shared bridge/types 19.15.1.
- React Native: `bde1095e84113c07569c0aab6858171768cb9aaf`; shared bridge/types 19.15.1. Current app resolves RevenueCat 5.98.0 and React Native 0.87.1.
- Hybrid Common: `ed23f3f08d1abe97d0ebe591b708bb984f8c2ced`.
- iOS reference: `c4f9551c86168cea9ced4b69dd56d177a2114574`.
- Android reference: `517a51e43484ce7edd27808ca79b15c64b944eda`.

## Reviewed contracts

| Customer operation | KMP | Capacitor | Native/shared comparison |
| --- | --- | --- | --- |
| Placement selection | `Offerings.getCurrentOfferingForPlacement` delegates to the corresponding native Offerings instance. Both platform mappings preserve a nullable result. Fetch failures belong to the preceding offerings-fetch callback. | iOS uses `getNullableCompletionBlockHandler`; Android uses `getOnNullableResult`. Public result is nullable. | KMP's instance method is a semantic equivalent, not a missing top-level API. RN's existing iOS rejection defect is already tracked in #2053/#2054. |
| Virtual-currency cache | `getCachedVirtualCurrencies()` preserves a missing native cache as null on both platforms. | Returns `{cachedVirtualCurrencies: null}` on a miss. Its JS proxy preserves zero balances and result identity. | Native APIs expose nullable caches; the Capacitor wrapper object is documented. These distinct public shapes are intentional. |
| Refresh/invalidate currency cache | Fetch, invalidate, and cache access exist in KMP, including coroutine and result wrappers. | All three operations exist in the public definition and both native plugins. | No customer-relevant missing method established. |
| Assigned entitlement ownership | Both native mappings include `ASSIGNED` on the current pinned versions. | Shared TypeScript 19.15.1 includes `ASSIGNED`. | Shared `typescript/src/customerInfo.ts` explicitly documents organization assignment. The new KMP dependency update includes the mapping; no missing-value report is warranted. |
| Custom paywall impressions | Public parameter model and native forwarding exist. | Public options are transformed into native identifiers/context. Empty optional input and explicit identifiers pass focused production-proxy tests. | Mere API-shape differences are not parity defects. |
| Redemption error delivery | Not a new defect candidate in this review. | Rejection normalization and resolved-error normalization are separate paths. Focused tests preserve successful payload identity and rejected transport errors. | These checks use a mocked bridge to exercise the real JS proxy; they are supplementary unit coverage, not native-app evidence. |

No new functional defect or customer-relevant parity gap was confirmed from these comparisons. Runtime results and setup limitations are recorded separately in coverage.md.
