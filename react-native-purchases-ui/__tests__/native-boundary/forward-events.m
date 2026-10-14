#import <Foundation/Foundation.h>
#import "RNPaywallEventForwarder.h"

@implementation PaywallProxy
+ (void)resumePurchasePackageInitiatedWithRequestId:(NSString *)requestId shouldProceed:(BOOL)shouldProceed {
    [NSException raise:@"UnexpectedStubCall" format:@"Not part of this fixture"];
}
@end

int main(int argc, const char * argv[]) {
    @autoreleasepool {
        NSData *errorData = [NSData dataWithContentsOfFile:[NSString stringWithUTF8String:argv[1]]];
        NSDictionary *error = [NSJSONSerialization JSONObjectWithData:errorData options:0 error:nil];
        NSMutableDictionary *events = [NSMutableDictionary new];
        RNPaywallEventForwarder *forwarder = [[RNPaywallEventForwarder alloc]
            initWithEmitter:^(NSString *name, NSDictionary *body) { events[name] = body; }
            jsResumesPurchase:^BOOL { return YES; }];
        [forwarder paywallViewController:nil didFailPurchasingWithErrorDictionary:error];
        [forwarder paywallViewController:nil didFailRestoringWithErrorDictionary:error];
        NSDictionary *info = @{@"originalAppUserId": @"local-fixture"};
        NSDictionary *transaction = @{@"transactionIdentifier": @"local-transaction", @"productIdentifier": @"local-product", @"purchaseDate": @"2026-10-13T00:00:00Z"};
        [forwarder paywallViewController:nil didFinishPurchasingWithCustomerInfoDictionary:info transactionDictionary:transaction];
        events[@"completedWithTransaction"] = events[@"onPurchaseCompleted"];
        // PHC's delegate permits nil; native custom purchase logic produces it.
        [forwarder paywallViewController:nil didFinishPurchasingWithCustomerInfoDictionary:info transactionDictionary:nil];
        events[@"completedWithoutTransaction"] = events[@"onPurchaseCompleted"];
        [events removeObjectForKey:@"onPurchaseCompleted"];
        NSData *json = [NSJSONSerialization dataWithJSONObject:events options:NSJSONWritingSortedKeys error:nil];
        [[NSFileHandle fileHandleWithStandardOutput] writeData:json];
    }
    return 0;
}
