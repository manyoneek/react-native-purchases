# iOS placement error propagation — October 21, 2026

Fresh verification on upstream `c656a4274c6203c1c7d73c7a345307d2c1966a64` and fix `0dddfd7f73e0dae0fbe445bf8b48e1526ce06c69`.

The same iOS simulator app ran with upstream JavaScript and the same dependency lock in both runs. Only the native placement error-propagation fix changed. The separate null-offering fix was not applied.

- App: one failed network-error assertion and one passing online control before; both pass with the fix.
- Extracted native implementation regression: three failures and three passing controls before; all six pass with the fix. Provider/dependency shims are used only in these supplementary host tests.
- Core JavaScript suite: 272 tests pass. Build and typecheck pass.

The screenshots were exported from XCTest attachments taken while the app was running and visually inspected. Tests used a real URLSession connection refusal at a closed localhost port and the dedicated Test Store for the successful control. No purchase, physical-device or Android testing.

[Runnable app source and instructions](https://github.com/manyoneek/react-native-purchases/blob/347427afb2537eeed630bf37eba35f810a1ac4c0/qa/reproductions/2026-10-20/current/rn-placement/source.zip). For this isolated fix, leave JavaScript at upstream and use only the `ios/RNPurchases.m` change from `0dddfd7f73e0`. Select `testNetworkError` and `testOnlineControl`; `commands.json` preserves the exact commands. `verify.py` records the local orchestration and requires adapting its workspace paths on another machine.
