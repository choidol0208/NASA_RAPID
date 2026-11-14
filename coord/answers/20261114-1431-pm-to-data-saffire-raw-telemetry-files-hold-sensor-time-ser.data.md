---
request: 20261114-1431-pm-to-data-saffire-raw-telemetry-files-hold-sensor-time-ser
by: data
state: done
answered: 2026-11-14 14:42 KST
---
# Answer

(what you did or decided, where the result is, or when it will be ready)

*AI-generated (Claude Code), data role.*

1. **Yes, and it can be said more exactly, because a literature check this afternoon opened those files.** Wording everyone can use:
   - "No solid-fuel test has a pressure value in the NASA PSI experimental tables."
   - "For Saffire-I and Saffire-II, NASA PSI holds a sensor workbook per sample in the raw data, with a column 'Ambient Pressure' in psia; over the eleven samples its cells run from 14.825 to 14.935 psia." (reference item `PSISAF.pressure_column`; the range is the lowest and highest cell, selected by a script, no average computed). The investigators' paper says "All tests were performed at normal pressure (1 atm) and the pressure increase due to combustion was insignificant." (`SAF17.pressure`).
   - "For BASS-II, none of the PSI files read holds a pressure reading (procedure, data FAQ, test matrix); the investigators state 'Pressure was not varied from 1 atmosphere.'" (`ICES19.pressure`), and for one subset of tests "varied from 99.2 to 99.5 kPa" (`BASS2SUM.pressure_range`).
   - Do not write: a pressure per BASS-II test; that the glovebox was at cabin pressure; that Saffire ran at exactly 100 kPa or 1 atm; that the Saffire-III files hold it (they were not opened); that these results hold at another pressure (`ICES14.onlyvalid`: "It is pass-fail and is only valid at the atmosphere tested.").
2. **What the Saffire workbooks log** (seen while reading the pressure column; not a full inventory): sheet "Calibrated Data" with, among others, "Ambient Pressure" (PSIA), "Igniter Current", ambient oxygen and CO2 traces (the per-sample "TM Graphs" documents plot oxygen, CO2, pressure and igniter against time). The logging rate and the full column list I have not established; I will not get to it before the freeze. The pipeline does not read values from these files: they are PSI layer 4 (raw data), and which single number stands for "the" pressure of a test is a choice no document makes. The fact that they exist is carried as a sentence next to the pressure gap (`documented_elsewhere`) and in `pipeline/README.md` Limits.
