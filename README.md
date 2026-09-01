# Fantasy Forecaster

Fantasy Forecaster collects public ESPN fantasy-league data, simulates the
remainder of each season, and publishes the resulting league data through an
API consumed by the GitHub Pages UI.

<https://jackarnold84.github.io/fantasy-forecaster/>

## Architecture

```
EventBridge schedule / manual invocation
                |
                v
 FantasyForecasterModelZip (Python Lambda)
   ESPN JSON API -> S3 CSV data -> simulation -> DynamoDB results
                |                                  |
                +----------------------------------+
                                                   v
                                  FantasyForecasterApi -> GitHub Pages UI
```

The model uses the `espn-api` Python package and ESPN's JSON endpoints. It no
longer uses Chrome, ChromeDriver, Selenium, or HTML parsing. It supports public
football, baseball, and basketball head-to-head points/category leagues.
Rotisserie leagues are not supported because the model requires matchups.

## Model updates

An invocation normally performs one complete update:

1. Fetch league members, schedule, and rosters from ESPN.
2. Fetch players, current stats, projections, injuries, and ownership data.
3. Fetch draft results when the requested week is `0`.
4. Run the simulation and write results to DynamoDB.

ESPN source data is stored as CSVs in S3; the model and API continue to use the
existing paths and schemas. ESPN requests have timeouts, retries, and response
validation, but ESPN's endpoints are unofficial—enable S3 versioning so a
known-good dataset can be recovered if ESPN changes a response.

Sleeper leagues are different: they use existing shared player data, so their
default update skips collection and only runs the simulation.

### Invocation payload

Pass a direct payload, or place the same object under `detail` in an EventBridge
scheduled event. `sport` and `league` are required and must exist in the S3
configuration.

```json
{
  "sport": "football-2026",
  "league": "purdue",
  "week": 5,
  "iter": 10000,
  "action": "fetch"
}
```

| Field | Required | Meaning |
| --- | --- | --- |
| `sport` | Yes | Configured sport-season key, such as `football-2026`. |
| `league` | Yes | Configured league key. |
| `week` | No | Week to update/simulate; defaults to the configured current week. Use `0` for preseason, which also collects the draft. |
| `iter` | No | Simulation iteration override; otherwise the league configuration is used. |
| `action` | No | Omit for the default full update. Use `fetch` for collection only or `sim` for simulation only. |

The scheduled events in [template.yaml](template.yaml) omit `action`, so every
scheduled run performs the complete default update.

## Local development and tests

Prerequisites: Python 3.13, Docker, AWS SAM CLI, and AWS CLI.

Build and validate the Lambda:

```sh
sam validate --lint
sam build --use-container
```

Run the default update locally without writing to S3:

```sh
sam local invoke FantasyForecasterModelZip \
  --event model/events/test.json \
  --env-vars model/events/environment.json
```

`model/events/environment.json` uses production data for reads and mock storage
for writes. In SAM, mock files are written to `/tmp/.mock-db` inside the
container; when running Python directly, the default is `.mock-db/`.

Run the collector and handler contract tests:

```sh
PYTHONPATH=model python3 -m unittest discover -s model -p 'test*.py' -v
```

To test a fetch-only or simulation-only invocation, set `action` to `fetch` or
`sim` in a copy of `model/events/test.json`.

## Deployment

The model is a Python zip Lambda defined in [template.yaml](template.yaml).

```sh
sam deploy
```

The zip Lambda is named `FantasyForecasterModelZip` so CloudFormation can create
it while removing the legacy image Lambda (`FantasyForecasterModel`) in the same
deployment. This replaces the old schedules with the combined-update schedules.

The stack creates the DynamoDB table and API Lambda. Configure the S3 bucket
name in [model/db/db.py](model/db/db.py), and grant the Lambda access through
the template policy.

## League configuration

Store `config.json` in the model S3 bucket. Each league needs its ESPN league
ID, season shape, and simulation parameters; `weeks` maps sport-season keys to
their current-week dates, while `aliases` normalizes manager names.

```json
{
  "leagues": {
    "football-2026": {
      "myleague": {
        "name": "My League",
        "league_id": "123456789",
        "teams": 10,
        "playoff_teams": 4,
        "regular_season_weeks": 14,
        "total_weeks": 18,
        "weeks_per_playoff_matchup": 2,
        "n_iter": 10000,
        "model_params": {"score_mean": 122, "score_sd": 25, "team_sd": 9}
      }
    }
  },
  "weeks": {"football-2026": {"1": "2026-09-08"}},
  "aliases": {"Full Manager Name": "Short Name"}
}
```

For a new ESPN league, make it publicly viewable, add its URL's `leagueId` to
this configuration, then add a default-action schedule for it in
[template.yaml](template.yaml).

## UI

The UI is a Gatsby site configured through [src/config.json](src/config.json).

```sh
npm start
npm run build
npm run deploy
```
