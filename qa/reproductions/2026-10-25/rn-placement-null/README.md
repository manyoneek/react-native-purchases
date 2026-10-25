# No Offering reproduction

Requirements: Xcode with an iOS simulator, Node 22+, Corepack, CocoaPods. Set `DEVELOPER_DIR` if needed. Export `RC_TEST_STORE_API_KEY` with the dedicated Test Store public SDK key; run `python3 prepare.py before` or `python3 prepare.py fixed`.

Open `app/ios/RCBugReporter.xcworkspace`, choose `QAReproduction`, and run. Tap **No offering case**. Before: the successful lookup returns undefined and the null-guarded consumer throws. After: it returns null and the same consumer shows “No offering”. Relaunch and tap **Online control**; both versions return the default offering.

This app uses the existing `sdk_bug_reporter_none_20261018` placement set to **No Offering**, and `qa_network_error_control` selecting the default offering. Project **SDK Bug Reporter** (`proj602cc762`), app **Test Store** (`app4ca00b430f`): https://app.revenuecat.com/projects/602cc762/apps/app4ca00b430f. For another Test Store project, create equivalent placements and update the identifiers in App.tsx. Users are synthetic and unique per run. No purchases.

Automated app tests: `RCBugReporterUITests/ReproductionTests/testNoOffering` and `testOnlineControl`. Run them with xcodebuild test using the workspace/scheme above and an installed simulator. `commands.json` contains exact observed invocations. SDK tests: `corepack yarn test --runInBand placementNullContract`; all five pass with the fix and one fails before it. These Jest boundary mocks supplement the actual app reproduction.

The app retains the separate network-error button from the original client. That defect is handled by upstream PR #2054; this fix does not change native error propagation. Public declarations are unchanged. Historical introducing-code tests remain dated October 20; no historical full app run is claimed.
