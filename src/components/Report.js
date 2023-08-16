import * as React from "react"
import output from "../../data/output.json"
import { capitalize } from "../utils/display"
import Betting from "./Betting"
import Forecasts from "./Forecasts"
import ScheduleStrength from "./ScheduleStrength"
import Standings from "./Standings"
import TeamRatings from "./TeamRatings"
import TimeForecasts from "./TimeForecasts"
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
    <Container top={2}>
      <div className="center">
        <Container top={2}>
          <h4 className="medium-weight x3-b4">{year}</h4>
          <h2>
            {leagueName} Fantasy {sport}
          </h2>
        </Container>
        <Container size={24}>
          <h4>
            Week {week} Report
          </h4>
        </Container>
      </div>

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

      <Betting
        forecasts={leageData.league.forecasts}
        week={week}
        teamLabels={teamLabels}
      />

      <ScheduleStrength
        expectedWins={leageData.league.expectedWins}
        sos={leageData.league.sos}
        teamLabels={teamLabels}
      />

      <TimeForecasts
        forecasts={leageData.league.forecasts}
        teamLabels={teamLabels}
      />

    </Container>
  )
}

export default Report
