# RevenueCat review — October 23, 2026

No new confirmed defect or customer-relevant parity gap. Existing React Native issue [#2053](https://github.com/RevenueCat/react-native-purchases/issues/2053) / PR [#2054](https://github.com/RevenueCat/react-native-purchases/pull/2054) was refreshed on current upstream and its review feedback addressed.

## Scope and results

76 public repositories inventoried; all 76 local clones verified. Six direct manyoneek contribution forks synchronized, preserving non-default branches. SDK reviews used isolated worktrees.

- KMP `1de077dc284d5c98e57ba5c6e991d470f32ba228`: 29 existing model tests passed on iOS simulator. Four added placement contract checks also passed; 33 total. Reviewed placement delegation, nullable cache results, currency operations, and assigned ownership across both native mappings. These model tests do not constitute a full purchase app reproduction.
- Capacitor `ba38d294a900c8a50024e15a023c3e954b5060d5`: 20 existing Jest tests passed; eight added proxy contract checks passed, 28 total. Normal build passed. Checked null placements, currency cache misses/zero balances, impression options, and redemption errors. These are production-JS unit tests with a mocked native boundary, not a native app run.
- React Native baseline `bde1095e84113c07569c0aab6858171768cb9aaf`, fix `36c08946262d4779e87dacc598025db63debe153`: 274 core and 37 UI Jest tests passed; build and typecheck passed. Identical native XCTest cases: one failure/three passes before, four passes after. Same actual iOS app: one failure/one pass before, two passes after. Native bridge method is the sole production difference between app runs.

The React Native app uses RevenueCat 5.98.0, PurchasesHybridCommon 19.15.1, React Native 0.87.1, and a real URLSession refusal at a closed localhost port. The error is `API_ENDPOINT_BLOCKED_ERROR` (33); the separate unit test uses the documented `RCNetworkError` constant (10). The successful control receives a real dedicated Test Store offering. No purchases or real-customer accounts were used.

## Existing finding and review maintenance

PR #2054 now uses one native rejection test instead of three identical-path error-code cases. The three successful-result controls remain. Comments explain why the standalone test bundle needs Hermes and non-modular React header imports. Its current-upstream merge resolves the example's Podfile.lock with the same native versions as upstream, adding only test dependencies. The production diff remains the existing error-aware completion helper.

All twelve ledger findings' publication states were checked. Upstream error-normalization PR [#2048](https://github.com/RevenueCat/react-native-purchases/pull/2048) is now merged. Its current UI unit suite passes; no new full native paywall run was performed, and the duplicate issue stays closed. This is not a claim that a particular released version was independently verified.

Eight older migrations remain pending their own latest-source app evidence and regression requirements. Their historical captures and dates are preserved; this run does not promote them to current app verification. CLI issue #199 / PR #200 remain open; the CLI was not retested today.

## Setup limitations and preserved evidence

KMP's first build lacked its pinned iOS submodule. Gradle had generated content in that directory; it was preserved separately before submodule initialization. Android tests then stopped because no Android SDK is configured. The alternative iOS model target ran successfully. No Android execution is claimed.

The first explainer render failed because this FFmpeg build lacks drawtext; Pillow-rendered caption cards fixed the media step. The source-package check caught a generated JS bundle containing the dedicated Test Store key; that build artifact was excluded before publication. The portable source archive omits the key and verifies its included npm package against the lockfile's integrity value.

Fresh in-test screenshots, continuous simulator recordings, captioned explainer, runnable source, dependency locks, test summaries and commands are preserved under the matching evidence directory. Source/test changes are limited to the fix and maintainable regression wiring. Review-only KMP/Capacitor tests are preserved in this report's tests directory. Historical introduction evidence remains dated October 20–21 and was not rerun.

The existing schedule was not changed; nothing was merged or pushed to upstream branches.
