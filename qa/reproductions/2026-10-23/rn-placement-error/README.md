# Placement error reproduction

Source-built React Native Purchases on iOS. This is the same app used for the October 23 evidence.

Requirements: Xcode with an iOS simulator, Node 22+, Corepack, CocoaPods. Set `DEVELOPER_DIR` if needed. Export `RC_TEST_STORE_API_KEY` with the dedicated Test Store public SDK key, then run `python3 prepare.py before` or `python3 prepare.py fixed`. The SDK snapshot includes the fixed method and permanent native tests; prepare.py switches only the production native method.

Open `app/ios/RCBugReporter.xcworkspace`, choose `QAReproduction`, and run. Tap **Network error case**: getOfferings rejects with code 33; before the fix the placement lookup resolves undefined, after the fix it rejects with the same code. Relaunch and tap **Online control** to see a real successful lookup. No purchases are made. Users are synthetic and unique per launch.

Project: SDK Bug Reporter (`proj602cc762`). App: Test Store (`app4ca00b430f`). Dashboard: https://app.revenuecat.com/projects/602cc762/apps/app4ca00b430f. The existing `qa_network_error_control` placement selects the default offering.

Automated app tests: `RCBugReporterUITests/ReproductionTests/testNetworkError` and `testOnlineControl`. Use the surrounding evidence's commands.json for the exact xcodebuild invocations and installed simulator identifier. The normal SDK `RNPurchases-Unit-UnitTests` scheme tests compiled bridge behavior. The separate successful-null-result fix is not included.

The evidence retains the dependency lockfiles resolved for this run. The Test Store key is deliberately supplied locally; never use a production key.
