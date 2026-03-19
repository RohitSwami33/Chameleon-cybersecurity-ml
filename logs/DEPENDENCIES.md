# Chameleon — Runtime Dependency Log
# Format: <EC-ID>: <package> (<version or constraint>) — <reason / install command>
# Universal Contract — Rule 5
# Created: 2026-03-19T18:53:50+05:30

## Base Dependencies (already present in requirements.txt)
> See Backend/requirements.txt for the full baseline.

## New Dependencies Introduced per EC

| EC | Package | Constraint | Notes |
|---|---|---|---|
| *(none yet)* | — | — | — |

EC-014 | redis[asyncio]>=4.0 | pip install redis[asyncio] | REDIS_URL env var required 
EC-038/039 | cachetools>=5.0 | pip install cachetools 
