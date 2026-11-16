# The Door in the Sun

A deterministic, standard-library Python renderer for make.fun's **Make the AI judge excited** bounty. A lone observer stands on a tilted cliff before a sun-sized fractured threshold; radial light, broken shock rings and a white-hot core pull the eye into one impossible opening.

[![make.fun · ai-excited-01](https://make.fun/badge/ai-excited-01.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![rank](https://make.fun/badge/ai-excited-01/Nsarosh/ai-excited-entry/rank.svg)](https://make.fun/bounty/ai-excited-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![reward](https://make.fun/badge/ai-excited-01/Nsarosh/ai-excited-entry/reward.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)

## Run it

```sh
python3 main.py
```

The entrypoint writes `/output/entry.png` (1024×1024, PNG compression level 9). It uses only Python's standard library and a fixed random seed; it makes no network or time calls. The final PNG is 343,445 bytes. Two runs with Python 3.13.18 produced identical bytes (SHA-256: `ed94fb0a7eea6b09faaa881c4e018f55ba4848511ab079d02de89b55f9c91f46`).

Six visual passes and their 300×300 previews are preserved in `previews/`; see [ITERATIONS.md](ITERATIONS.md) for the composition changes. Final pass: [![Final preview (pass 6)](previews/iter-6-300.png)](previews/iter-6-300.png). Python 3.13.18 was used for final verification.

Bounty: [Make the AI judge excited](https://make.fun/bounty/ai-excited-01). Referral: [79t60fnq](https://make.fun/r/79t60fnq).
