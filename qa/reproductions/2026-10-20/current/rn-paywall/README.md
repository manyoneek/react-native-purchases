# Current app/client verification

Upstream: `RevenueCat/react-native-purchases` at `c656a4274c6203c1c7d73c7a345307d2c1966a64`. Captured October 20, 2026. Native SDK dependencies: PurchasesHybridCommon 19.14.0 / RevenueCat iOS 5.96.0.

Both XCTest flows verify the defects before and corrected behavior after. The transaction case requires the shown consumer guard; its type declaration alone does not change runtime.

[Runnable source and build instructions](source.zip). Extract to a fresh directory and follow its README. Before/fixed captures, exact commands, resolved dependency locks, results and test logs are included here. Historical introducing-commit execution remains separately labeled in the history files.
