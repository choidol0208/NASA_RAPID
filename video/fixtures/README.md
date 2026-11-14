# Test fixtures

Six grayscale overlay strips (580 x 56 px, lossless PNG) cut from NASA's PSI-25 BASS-II videos (DOI 10.60555/4qc4-de67, CC0-1.0) by `video/tools/make_fixtures.py`, exactly as `read_overlay.py` sees them: only the text strip of the frame (rows 30-85, columns 140-719), nothing else of the picture.

| File | Clip | Second | What it shows |
|---|---|---|---|
| `O9_t576.png` | PSI-25_Raw Data_BASS_GMT177_SAMPLE_209_TEST_O9.mp4 | 576 | FUEL -2, AIR 10, FAN 198 (frame caught while the display was changing), RAD 0.3, clock 15:33:17 |
| `M17_t202.png` | PSI-25_Raw Data_BASS_GMT196_SAMPLE_166_TEST_M17.mp4 | 202 | FUEL -1, AIR 9, FAN 69, RAD 1.9, clock 15:15:33 |
| `O19_t1009.png` | PSI-25_Raw Data_BASS_GMT213_SAMPLE_213_TEST_O19.mp4 | 1009 | FUEL -2, AIR 39, FAN 123, RAD 0.2, clock 17:05:47 |
| `P25_t608.png` | PSI-25_Raw Data_BASS_GMT189_SAMPLE_217_TEST_P25.mp4 | 608 | FUEL -2, AIR 0, FAN 41, RAD 0.9, clock 17:57:50 |
| `P5_t945.png` | PSI-25_Raw Data_BASS_GMT195_SAMPLE_202_TEST_P5.mp4 | 945 | blue screen, no overlay |
| `P22b_t430.png` | PSI-25_Raw Data_BASS_GMT189_SAMPLE_200_TEST_P22b.mp4 | 430 | top of colour bars, no overlay |

The values in the last column are by-eye readings recorded in the pilot's second review (hard cases), audit file `sceptic_overlay_compare.csv` in the pilot folder, which is not shipped and not part of the repository. "By eye" means that an AI assistant (Claude) looked at each frame image and wrote the numbers down before it saw the reader's values. No person has checked a frame. Cut by code that an AI assistant (Claude) wrote; not a NASA data file.
