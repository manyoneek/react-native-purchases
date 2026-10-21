# Native XCTest regression

Tested October 21, 2026. Upstream: `c656a4274c6203c1c7d73c7a345307d2c1966a64`. Updated PR head: `97be2623bd866aeba580bfcd111fb22d8e27c769`.

The same six XCTest cases run against the compiled `RNPurchases` CocoaPod and real shared SDK types. OCMock replaces only the shared SDK's response provider. The test target uses CocoaPods' UnitTests test spec; it is selected by the example app's Podfile and runs in the existing CircleCI iOS job.

- Unfixed production method: three error tests fail, three success controls pass.
- Fixed production method: all six tests pass.
- Assertions check reject/resolve counts, error code, message, underlying error and context, successful offering values, absent results, and placement identifier forwarding.
- Existing JavaScript suite: 272 tests pass. TypeScript build passes.

The before run leaves the new test files and test wiring in place and restores only `ios/RNPurchases.m` from upstream. The fixed run restores the patch. See commands.json for the exact local commands and the compressed logs for execution output.

From the repository root, after yarn installation and `pod install` in `examples/purchaseTesterTypescript/ios`:

```sh
xcodebuild test \
  -workspace examples/purchaseTesterTypescript/ios/PurchaseTester.xcworkspace \
  -scheme RNPurchases-Unit-UnitTests \
  -destination 'platform=iOS Simulator,name=iPhone 16' \
  -configuration Release CODE_SIGNING_ALLOWED=NO
```

Select an installed simulator for local execution. Verification used Xcode27.1 RC and an iOS27.1 simulator. CircleCI execution itself has not been verified by this local run.

The Python extraction harness is no longer in the PR. Earlier harness results remain historical evidence in the parent directory; these XCTest results supersede that harness as the permanent regression coverage. The app integration evidence in the parent directory still applies: the production fix is unchanged by the test-only commit.
