# Fantasy Forecaster
## Version 2

Predict ESPN fantasy league outcomes by simulation

https://jackarnold84.github.io/fantasy-forecaster/

## UI

- develop locally
  - `npm start`
- build locally
  - `npm build`
- serve on local network
  - `npm run serve` 
- deploy to github pages
  - `npm run deploy`
  - see gatsby-config.js for options

## Simulation Model

The [model](model/) fetches player and league data from ESPN and runs simulations. It is designed to be hosted on AWS and deployed using [template.yaml](template.yaml).

- prerequisites
  - Docker
  - AWS CLI
  - AWS SAM CLI
  - AWS account

- Set up an S3 bucket to hold fetched data
  - update [db.py](model/db/db.py) with the bucket name
  - add a [config file](#config-file)
- All other necessary resources will be created by the sam template
- Set up new league
  - ensure league is viewable to public on ESPN (LM setting)
  - go to ESPN to find leagueID (visable in URL)
  - add config information to your [config file](#config-file)
- Trigger lambda
  - actions: fetchDraft --> fetchLeague --> fetchPlayers --> sim
  - see [events/](model/events/) for how to trigger these actions
  - add scheduled events to the lambda for automatic updates

### Config File
Add a file `config.json` to the S3 bucket with the following format:

```json
{
    "leagues": {
        "football-2024": {
            "myleague": {
                "name": "My League Name",
                "league_tag": "myleague",
                "sport_tag": "football-2024",
                "league_id": "123456789", // ESPN leagueID
                "player_metrics": true,
                "teams": 10,
                "playoff_teams": 4,
                "divisions": false,
                "tiebreaker": "points",
                "weeks_per_playoff_matchup": 2,
                "total_weeks": 18,
                "regular_season_weeks": 14,
                "n_iter": 10000,
                "model_params": {
                    "score_mean": 122,
                    "score_sd": 25,
                    "team_sd": 9
                }
            }
        },
        // ...
    },
    "weeks": {
        "football-2024": {
            "2": "2024-09-10",
            "3": "2024-09-17",
            // ...
        }
    },
    "aliases": {
        "John Smith": "John",
        "Jack Arnold": "Jack",
        // ...
    }
}
```
