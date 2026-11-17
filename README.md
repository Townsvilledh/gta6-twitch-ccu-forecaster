# GTA VI Twitch CCU forecaster

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

## Run

```sh
mkdir -p out && MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Licence

MIT — see LICENSE.
