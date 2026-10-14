# Actual-app reproduction evidence — 2026-10-14

These are the same apps run before and after the proposed fixes, not recreated mock UIs. Original sources in the archive reproduce the defects; proposed patches and guarded consumer are included separately. Configure your own **public Test Store key** in `react-native-app/qa-config.json` or `flutter-app/lib/config.dart` before running. The key used during capture is deliberately omitted from this public archive.

Native captures: iOS27.1 simulator, actual native paywall/Test Store failure and successful custom purchase. Web captures: real Flutter/JavaScript SDK, real Test Store initialization, then Chrome Offline for attribute failures. Only synthetic users; no production charges or real customer accounts.

Each `*-fixed` video/image shows the result with the proposed fixes. The app validation applied both independent fixes for its SDK together. Each PR additionally runs its regression in isolation against the unchanged baseline and its own patch. Native app pins the reviewed React Native commit dffdb082054c9d9d71287e72a6565c422485a3d8 / shared19.11.0; newer main's dependency bump was not app-tested. Flutter pins 2b4b1976cfd08607c0384f5d619672e99e762c32 / shared19.12.0.

Native video: app display cropped/resized; final recorded frame held six seconds for readability. Original screenshots are XCTest attachments; fixed native PNGs are extracted result frames. Web video: actual Chrome screencast frames. No fabricated results. No Android, physical device, Wasm or real-store verification.

Final fixed native run: two XCTest cases passed, command exit0. An original recorded run passed both assertions but stalled in runner shutdown and was terminated; a prior clean original run completed. Flutter focused regression: original4pass/10fail, fixed14pass. See per-finding reports and preserved logs for limits.
