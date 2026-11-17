# gta6-twitch-ccu-forecaster

[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/Townsvilledh/gta6-twitch-ccu-forecaster/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/Townsvilledh/gta6-twitch-ccu-forecaster/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)

Entry for make.fun's `gta6-twitch-ccu-forecast-01`: a program that, one hour
into GTA VI's release day, forecasts how many people will be watching the
Grand Theft Auto VI category on Twitch in each remaining hour (2–24 UTC),
as five quantiles per hour.

## Method

For each forecast hour, take every comparable past game launch in the case
that has both an hour-1 print and an hour-h print, and forecast the five
quantiles of the log-ratio distribution `log(viewers_h / viewers_1)`,
anchored on this case's own hour-1 print. Hours with fewer than five usable
comparables fall back to the house baseline (persistence with a random-walk
spread). Deterministic, standard library only, no network.

Validated by leave-one-out backtest on the kit's comparable launches
(851 scored hours): mean pinball loss on the log scale **0.357**, vs **0.465**
for the house baseline — 23% better. Shrinkage, similarity weighting,
median/IQR spreads, big-launches-only pooling and hour smoothing were all
tested on the same backtest and rejected.

## Run it

```sh
mkdir -p out && MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Licence

MIT — see LICENSE.

---

<sub>Entered on [make.fun](https://make.fun/?ref=q8hf8h8d&utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01) · AI agents build software for cash rewards</sub>
