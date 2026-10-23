# Captioned explainer

Actual October 23 simulator footage interleaved with explanatory title cards. No voice narration.

## intro

Placement failures disappear
React Native Purchases / iOS

A real connection error resolves
as undefined instead of rejecting.

October 23, 2026 / upstream bde1095e

## before

BEFORE / live iOS app

The app points the SDK at a
closed local port.

getOfferings rejects with code 33.
The placement call resolves
undefined and bypasses catch.

## cause

ROOT CAUSE

The iOS placement completion receives
both an offering and an error.

It ignores the error and always calls resolve.
The SDK already has an error-aware helper.

## fix

THE FIX

Route the completion through the existing
getResponseCompletionBlockWithResolve helper.

Native errors now reject the JavaScript promise.
Public API signatures stay unchanged.

## fixed

AFTER / same live iOS app

Same source baseline and dependencies.
Only the native bridge fix changes.

The placement request now rejects
with code 33. The app catches it.

## control

SUCCESS CONTROL

The real Test Store lookup still works.
Synthetic user / no purchases.

App tests: 1 fail + 1 pass -> 2 pass
Native tests: 1 fail + 3 pass -> 4 pass
