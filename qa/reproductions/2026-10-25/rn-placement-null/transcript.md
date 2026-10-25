# Captioned explainer

Actual October 25 simulator footage and explanatory title cards. No voice narration.

## intro

A successful placement lookup can break a null guard

React Native Purchases / iOS
Placement configured as “No Offering”
October 25, 2026 / upstream bde1095e

## before

BEFORE / real iOS app

The Test Store request succeeds.
The placement resolves undefined.

A consumer checking offering !== null
tries to read offering.identifier
and throws TypeError.

## cause

ROOT CAUSE

The iOS bridge resolves a nil offering.
React Native delivers that as undefined.
The TypeScript wrapper forwards it unchanged.

Its public return type promises an offering or null.

## fix

THE FIX

Await the native result and return offering ?? null.
Existing offerings and rejected promises are preserved.

No public API signature change or consumer migration.
Native error propagation is a separate fix: PR #2054.

## fixed

AFTER / same real iOS app

Same source and dependency baseline.
Only null normalization changes.

The placement resolves null.
The same consumer shows “No offering”.

## verified

CHECKED ON CURRENT SOURCE

Real app: 1 failure + 1 pass → 2 passes
Focused Jest regression: 1 failure + 4 passes → 5 passes
All 279 SDK tests, build and lint pass with the fix.

Synthetic Test Store users. No purchases.
Android app behavior was not tested.