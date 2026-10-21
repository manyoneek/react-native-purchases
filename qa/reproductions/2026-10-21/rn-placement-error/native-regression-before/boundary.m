#import <Foundation/Foundation.h>
typedef void (^RCTPromiseResolveBlock)(id);
typedef void (^RCTPromiseRejectBlock)(NSString *,NSString *,NSError *);
#define RCT_EXPORT_METHOD(method) - (void)method
@interface NSString (Mapping)
@property(readonly) NSString *mappingNSNullToNil;
@end
@implementation NSString (Mapping)
- (NSString *)mappingNSNullToNil {return self;}
@end
@interface RCErrorContainer : NSObject
@property NSInteger code;
@property NSString *message;
@property NSDictionary *info;
@property NSError *error;
@end
@implementation RCErrorContainer
@end
static NSDictionary *providerValue;
static RCErrorContainer *providerError;
@interface RCCommonFunctionality : NSObject
+ (void)getCurrentOfferingForPlacement:(NSString *)placement completionBlock:(void (^)(NSDictionary *,RCErrorContainer *))block;
@end
@implementation RCCommonFunctionality
+ (void)getCurrentOfferingForPlacement:(NSString *)placement completionBlock:(void (^)(NSDictionary *,RCErrorContainer *))block {block(providerValue,providerError);}
@end
@interface RNPurchases : NSObject
@end
@implementation RNPurchases
RCT_EXPORT_METHOD(getCurrentOfferingForPlacement:(NSString *)placementIdentifier
                  resolve:(RCTPromiseResolveBlock)resolve
                  reject:(RCTPromiseRejectBlock)reject) {

    [RCCommonFunctionality getCurrentOfferingForPlacement:placementIdentifier.mappingNSNullToNil completionBlock:^(NSDictionary *offeringObject, RCErrorContainer *error) {
        resolve(offeringObject);
    }];
}
- (void)rejectPromiseWithBlock:(RCTPromiseRejectBlock)reject error:(RCErrorContainer *)error {
    // React Native forwards only the NSError's userInfo to the JS layer, never the error
    // container's info dictionary, so the payload has to travel inside userInfo.
    NSMutableDictionary *userInfo = [error.error.userInfo mutableCopy];
    [userInfo addEntriesFromDictionary:error.info];
    NSError *errorWithInfo = [NSError errorWithDomain:error.error.domain
                                                 code:error.error.code
                                             userInfo:userInfo];

    reject([NSString stringWithFormat:@"%ld", (long) error.code], error.message, errorWithInfo);
}
- (void (^)(NSDictionary *, RCErrorContainer *))getResponseCompletionBlockWithResolve:(RCTPromiseResolveBlock)resolve
                                                                               reject:(RCTPromiseRejectBlock)reject {
    return ^(NSDictionary *_Nullable responseDictionary, RCErrorContainer *_Nullable error) {
        if (error) {
            [self rejectPromiseWithBlock:reject error:error];
        } else if (responseDictionary) {
            resolve([NSDictionary dictionaryWithDictionary:responseDictionary]);
        } else {
            resolve(nil);
        }
    };
}
@end
int main() { @autoreleasepool {
 NSMutableArray *rows=[NSMutableArray array]; int failed=0;
 for (NSDictionary *c in @[
  @{ @"name":@"network-error", @"code":@10 },
  @{ @"name":@"configuration-error", @"code":@23 },
  @{ @"name":@"invalid-credentials", @"code":@11 },
  @{ @"name":@"no-offering", @"value":[NSNull null] },
  @{ @"name":@"empty-dictionary-control", @"value":@{} },
  @{ @"name":@"present-offering", @"value":@{@"identifier":@"default"} }
 ]) {
  providerValue=nil;providerError=nil;
  if(c[@"code"]) {
   providerError=[RCErrorContainer new]; providerError.code=[c[@"code"] integerValue];providerError.message=@"Test native error";
   providerError.info=@{@"underlyingErrorMessage":@"Test underlying failure"};
   providerError.error=[NSError errorWithDomain:@"RCPurchasesErrorDomain" code:providerError.code userInfo:providerError.info];
  } else if(c[@"value"] != [NSNull null]) { providerValue=c[@"value"]; }
  __block int resolved=0,rejected=0; __block id actualValue=nil; __block NSString *actualCode=nil;
  [[RNPurchases new] getCurrentOfferingForPlacement:@"qa" resolve:^(id value){resolved++;actualValue=value;} reject:^(NSString *code,NSString *message,NSError *error){rejected++;actualCode=code;}];
  BOOL ok=c[@"code"] ? (rejected==1 && resolved==0 && [actualCode isEqual:[c[@"code"] stringValue]]) : (resolved==1 && rejected==0 && [(actualValue?:[NSNull null]) isEqual:c[@"value"]]);
  if(!ok)failed++;
  [rows addObject:@{@"case":c[@"name"],@"passed":@(ok),@"resolveCalls":@(resolved),@"rejectCalls":@(rejected),@"value":actualValue?:[NSNull null],@"code":actualCode?:[NSNull null]}];
 }
 NSData *json=[NSJSONSerialization dataWithJSONObject:rows options:NSJSONWritingPrettyPrinted error:nil];puts([[NSString alloc]initWithData:json encoding:NSUTF8StringEncoding].UTF8String);
 return failed?1:0;
} }
