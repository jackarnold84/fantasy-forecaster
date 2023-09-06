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

- prereq
  - download latest stable [chromedriver](https://googlechromelabs.github.io/chrome-for-testing/#stable)
  - create a file `model/credentials.py` with contents
  - `path_to_chromedriver = '<path-to-chromedriver.exe>'`
- set up new league
  - ensure league is viewable to public on ESPN (LM setting)
  - add config information to `model/config.py`
  - go to ESPN to find leagueID
- fetch data from ESPN
  - `run.py fetch <sport> <league> <upcoming-week>`
- run simulation
  - `run.py sim <sport> <league> <upcoming-week>`
