#!/usr/bin/env python3
"""Compile unmodified production boundary code; no stores, network or accounts.

Usage: python3 build-fixtures.py /path/to/purchases-hybrid-common
Only unavailable framework declarations are shimmed. Error serialization and
event forwarding come from actual production files, not copied test logic.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

here = Path(__file__).resolve().parent
repo = here.parents[1]
common = Path(sys.argv[1]).resolve()

def run(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)

with tempfile.TemporaryDirectory(prefix="rc-boundary-") as tmp:
    work = Path(tmp)
    # A declaration-only dependency substitute. This branch must never execute:
    # our NSError supplies readable_error_code, as the native SDK normally does.
    (work / "RevenueCat.swift").write_text('''
public struct ErrorCode {
    public static let errorDomain = "RevenueCat.ErrorCode"
    public init?(rawValue: Int) { fatalError("Unexpected dependency stub execution") }
    public var errorUserInfo: [String: Any] { fatalError("Unexpected dependency stub execution") }
}
''')
    source_path = "ios/PurchasesHybridCommon/PurchasesHybridCommon/ErrorContainer.swift"
    source = subprocess.check_output(["git", "-C", str(common), "show", "19.11.0:" + source_path])
    (work / "ErrorContainer.swift").write_bytes(source)
    (work / "main.swift").write_text('''
import Foundation
let error = NSError(domain: "RevenueCat.ErrorCode", code: 10,
    userInfo: [NSLocalizedDescriptionKey: "Local network-error fixture",
               "readable_error_code": "NetworkError"])
let container = ErrorContainer(error: error, extraPayload: [:])
let data = try JSONSerialization.data(withJSONObject: container.info, options: [.sortedKeys])
FileHandle.standardOutput.write(data)
''')
    run("xcrun", "swiftc", "-emit-module", "-emit-library", "-module-name", "RevenueCat",
        str(work / "RevenueCat.swift"), "-emit-module-path", str(work / "RevenueCat.swiftmodule"), "-o", str(work / "libRevenueCat.dylib"))
    run("xcrun", "swiftc", "-I", str(work), "-L", str(work), "-lRevenueCat",
        "-Xlinker", "-rpath", "-Xlinker", str(work),
        str(work / "ErrorContainer.swift"), str(work / "main.swift"), "-o", str(work / "serialize-error"))
    error = subprocess.check_output([str(work / "serialize-error")])
    (work / "error.json").write_bytes(error)

    (work / "module.modulemap").write_text('''
module PurchasesHybridCommonUI { header "HybridDeclarations.h" export * }
module RevenueCatUI { header "UIDeclarations.h" export * }
''')
    (work / "UIDeclarations.h").write_text("#import <Foundation/Foundation.h>\n")
    (work / "HybridDeclarations.h").write_text('''
#import <Foundation/Foundation.h>
@class RCPaywallViewController;
@protocol RCPaywallViewControllerDelegateWrapper <NSObject>
@optional
- (void)paywallViewController:(RCPaywallViewController *)controller didFailPurchasingWithErrorDictionary:(NSDictionary *)error;
- (void)paywallViewController:(RCPaywallViewController *)controller didFailRestoringWithErrorDictionary:(NSDictionary *)error;
- (void)paywallViewController:(RCPaywallViewController *)controller didFinishPurchasingWithCustomerInfoDictionary:(NSDictionary *)info transactionDictionary:(NSDictionary *)transaction;
@end
@interface PaywallProxy : NSObject
+ (void)resumePurchasePackageInitiatedWithRequestId:(NSString *)requestId shouldProceed:(BOOL)shouldProceed;
@end
''')
    forwarder = repo / "ios/RNPaywallEventForwarder.m"
    run("xcrun", "clang", "-fobjc-arc", "-fblocks", "-fmodules", "-I", str(work),
        "-I", str(repo / "ios"), "-framework", "Foundation", str(forwarder),
        str(here / "forward-events.m"), "-o", str(work / "forward-events"))
    events = subprocess.check_output([str(work / "forward-events"), str(work / "error.json")])
    (here / "events.json").write_bytes(events + b"\n")
    metadata = {
        "reactNativeCommit": subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip(),
        "hybridCommonTag": "19.11.0",
        "hybridCommonCommit": subprocess.check_output(["git", "-C", str(common), "rev-parse", "19.11.0^{commit}"], text=True).strip(),
        "errorContainerSHA256": hashlib.sha256(source).hexdigest(),
        "eventForwarderSHA256": hashlib.sha256(forwarder.read_bytes()).hexdigest(),
        "limitations": "macOS Foundation host execution; declaration-only SDK/UI shims; no UIKit, React Native runtime, StoreKit or service execution",
    }
    (here / "provenance.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(events.decode())
    print(json.dumps(metadata, indent=2))
