# TrackSide Live Phase 3

This coursework extends the Phase 2 race-session prototype with a session minimum and cached standings. Fictional inputs are used throughout. The Flask dashboard is a separate demonstration.

## Report and measured evidence

- [Four-page APA report with title and references](reports/TrackSide_Live_Phase_3.docx)
- [Summary metrics](phase3_results/summary.csv)
- [All 50 raw timing samples](phase3_results/raw_timings.csv)
- [Execution environment](phase3_results/environment.json)
- [Performance graph](phase3_results/phase3_performance.png)
- [20-test execution log](phase3_test_results.txt)

## Run from the repository root

Python 3.10 or later is required for the existing type annotations. The sessions, tests, and benchmark use the standard library.

```bash
python3 coursework/phase3_optimized.py
python3 -m unittest discover -s coursework -v
python3 coursework/benchmark_phase3.py
```

The benchmark replaces the files in coursework/phase3_results. Retain a copy of the supplied measurements before reproducing on a different computer.

To regenerate the graph, install matplotlib in your chosen virtual environment and run:

```bash
python3 -m pip install matplotlib
python3 coursework/plot_phase3.py
```

## Changes and contract

OptimizedRaceSession preserves Phase 2's register_driver, find_driver, record_lap, fastest_lap, and rankings interfaces and their returned values for finite numeric lap inputs. Driver IDs must be nonblank strings, as in Phase 2. Both classes reject unknown drivers, invalid times, and duplicate registrations.

A cached (time, driver ID) tuple replaces the all-observation min-heap. The AVL tree stores each driver's best lap, and its existing dictionary supplies the current best in expected constant time. Equal and slower laps leave standings unchanged. New bests invalidate the cached ranking tuple. Each rankings call returns a fresh list to protect internal state.

The optimized object discards individual lap history. A system requiring lap audits, retractions, or corrections must store those events separately and define how best laps are recomputed. This reduction in retained information is a material part of the memory benefit.

## Complexity

For D drivers and L valid lap observations:

| Operation | Phase 2 | Phase 3 |
| --- | --- | --- |
| Driver lookup | Expected O(1) | Expected O(1) |
| Equal or slower lap | O(log L) worst-case heap insertion | Expected O(1) |
| First or faster lap | O(log L + log D) | Expected O(1) lookup plus O(log D) tree update |
| Fastest lap | O(1) | O(1) |
| First rankings read after a best changes | O(D) | O(D) |
| Unchanged rankings read | O(D) traversal | O(D) list copy |
| Retained session state | O(D + L) | O(D), including cached ranking tuple |

The read cache reduces measured traversal overhead without changing the full-list output complexity. No deletion/correction/concurrency API is added.

## Measurement design

The baseline is the original Phase 2 source from commit 76fdb1a2d46c5cf97004c5778847146f621ef5a8. Its source and Phase 1 dependencies are unchanged.

Five configurations combine 100, 1,000, or 10,000 drivers and 1,000 through 500,000 laps. Each input uses a deterministic seed, round-robin driver IDs, and quantized random times. Every driver appears. Timing includes session construction, registration, and lap recording but excludes prebuilt inputs and independently sorted references.

Each configuration has five timing trials per version, alternating order. The first ranking read is timed separately, followed by 100 reads with no intervening changes. Every final result is checked against the independent reference. Raw samples and median/minimum/maximum summaries are retained.

One separate tracemalloc run per configuration measures retained and peak additional Python allocations through the first ranking read. Existing input records are excluded. These are not whole-process RSS figures or total system memory. The instrumented memory runs are excluded from timing comparisons.

The saved results were generated in the assistant execution environment, CPython 3.12.14 on Linux x86_64. They were not generated on the student's Mac.

## Findings and limitations

At 10,000 drivers / 100,000 laps, median ingestion changed from 450.55 to 427.47 ms (5.1% lower), with overlapping trial ranges. Peak traced allocations changed from 8.03 to 2.08 MiB. One hundred unchanged ranking reads changed from 122.24 to 1.95 ms.

At 1,000 drivers / 500,000 laps, median ingestion changed from 360.76 to 176.21 ms (51.2% lower). Peak traced allocations changed from 30.881 to 0.219 MiB (99.3% lower), reflecting discarded history and bounded standings state.

All 20 discovered tests passed, including 9 existing tests, 5 inherited Phase 2 contract tests, and 6 additional Phase 3 tests. Checks cover reference parity, AVL invariants, ties, improving update orders, cache invalidation, caller mutation, invalid inputs, and a 100,000-lap stress stream.

These measurements represent one environment and workload. The unchanged-read experiment deliberately exercises cache reuse. Constant improvement invalidates the cache, so first-read and update-heavy costs remain relevant. Production readiness still requires durable events, timing-feed integration, concurrency design, corrections, process-level memory measurement, and broader workloads.
