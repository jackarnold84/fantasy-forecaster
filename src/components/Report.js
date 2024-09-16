import * as React from "react";
import { capitalize, timeSince } from "../utils/display";
import Betting from "./Betting";
import Forecasts from "./Forecasts";
import ScheduleStrength from "./ScheduleStrength";
import Standings from "./Standings";
import TeamRatings from "./TeamRatings";
import TimeForecasts from "./TimeForecasts";
import UpcomingGames from "./UpcomingGames";
import Container from "./elements/Container";
import TeamLabel from "./elements/TeamLabel";

const Report = ({ leagueData }) => {
  const leagueName = leagueData.meta.name
  const sport = capitalize(leagueData.meta.sport)
  const year = leagueData.meta.year
  const week = parseInt(leagueData.meta.week)
  const updated = leagueData.meta.updated

  const teamLabels = Object.fromEntries(
    Object.values(leagueData.teams.metadata).map(meta => (
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

        <Container top={24} bottom={2}>
          <h3>
            Week {week} Report
          </h3>
        </Container>
        <Container bottom={16}>
          {updated && <div style={{ fontSize: "12px" }}>Updated {timeSince(updated)} ago</div>}
        </Container>

      </div>

      <Standings
        standings={leagueData.league.standings}
        teamLabels={teamLabels}
        isPreseason={week <= 1}
      />

      <UpcomingGames
        matchupImportance={leagueData.league.matchupImportance}
        teamLabels={teamLabels}
        week={week}
      />

      <Forecasts
        forecasts={leagueData.league.forecasts}
        week={week}
      />

      <TeamRatings
        ratings={leagueData.teams.ratings}
        rosters={leagueData.teams.roster.players}
        players={leagueData.players}
        week={week}
      />

      <Betting
        forecasts={leagueData.league.forecasts}
        week={week}
        teamLabels={teamLabels}
      />

      <ScheduleStrength
        expectedWins={leagueData.league.expectedWins}
        sos={leagueData.league.sos}
        teamLabels={teamLabels}
        isPreseason={week <= 1}
      />

      {
        week > 1 &&
        <TimeForecasts
          forecasts={leagueData.league.forecasts}
          teamLabels={teamLabels}
        />
      }

    </Container>
  )
}

export default Report
