---
from: pm
to: data
opened: 2026-11-14 14:31 KST
needed_by: 17:00
closed: false
---
# Saffire raw telemetry files hold sensor time series the tables lack

## What I need

*AI-generated (Claude Code), pm role. Low priority; decline freely if it does not fit before your 17:30 freeze.*

A look at the PSI file listings (no download) shows that the Saffire investigations carry numeric raw data next to the videos, which BASS-II does not:

- PSI-99: `Raw Data/PSI-99_Raw Data_Saffire-II Telemetry Data.xlsx` (41.5 MB), `Saffire Sensor Data Sample 1.xlsx` (13.8 MB) and per-sample "TM Graphs" documents.
- PSI-98: `Saffire-I Telemetry Data Good Process Version.xlsx` (2.8 MB), `Saffire-I Sample 1 Sensor Data Complete TM graphs.xlsx` (25.1 MB).
- PSI-100: `Saffire-III Telemetry Data.xlsx` (8.7 MB), `Saffire-III 1 Hz Telemetry Data.xlsx` (21.3 MB), `Saffire_Data_Table2017.161.00.42.03-EU.csv` (5.2 MB), `Raw telemetry file.csv` (1.7 MB).

What I ask, in this order:
1. One sentence for everyone's wording: is it right to say "no solid-fuel test has a pressure value in the PSI experimental tables; for Saffire I to III the raw telemetry files in PSI may hold it"? pm and ui currently say only the first half.
2. If you have time: open one telemetry file and say in your status which quantities it logs (pressure, oxygen, carbon dioxide, temperatures, radiometers) and at what rate. Whether to read values from it into a separate, clearly named layer is your call; pm does not need it today.

## Why

The human lead asked whether what a video shows already exists as numeric raw data. For BASS-II it does not (NASA's ReadMe says fan voltage, duct flow speed and radiometer are "on the video display"; the raw data are videos, still photos and proof sheets). For Saffire it apparently does, so nobody should spend effort reading it from video, and the statement about pressure should be scoped to the tables.

## Until then

pm keeps every statement about pressure scoped to "the PSI experimental tables" and runs its video pilot on BASS-II only.
