import * as React from "react"
import output from "../../data/output.json"
import { capitalize } from "../utils/display"
import Forecasts from "./Forecasts"
import Standings from "./Standings"
import TeamRatings from "./TeamRatings"
import UpcomingGames from "./UpcomingGames"
import Container from "./elements/Container"
import TeamLabel from "./elements/TeamLabel"

const Report = ({ sportTag, leagueTag }) => {

  const leageData = output[sportTag][leagueTag]
  const leagueName = leageData.meta.name
  const sport = capitalize(leageData.meta.sport)
  const year = leageData.meta.year
  const week = parseInt(leageData.meta.week)

  const teamLabels = Object.fromEntries(
    Object.values(leageData.teams.metadata).map(meta => (
      [
        meta.name,
        <TeamLabel meta={meta} />
      ]
    ))
  )

  return (
    <Container>
      <Container top="0">
        <h2 className="center">
          {leagueName} Fantasy {sport} ({year})
        </h2>
        <p className="center">
          Week {week} Report
        </p>
      </Container>

      <Standings
        standings={leageData.league.standings}
        teamLabels={teamLabels}
      />

      <UpcomingGames
        matchupImportance={leageData.league.matchupImportance}
        teamLabels={teamLabels}
        week={week}
      />

      <Forecasts
        forecasts={leageData.league.forecasts}
        week={week}
      />

      <TeamRatings
        ratings={leageData.teams.ratings}
        week={week}
      />

    </Container>
  )
}

export default Report
