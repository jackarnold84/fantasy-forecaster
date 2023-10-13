import * as React from "react"
import output from "../../data/output.json"
import UpcomingGames from "./UpcomingGames"
import Container from "./elements/Container"
import SectionTitle from "./elements/SectionTitle"
import TeamLabel from "./elements/TeamLabel"
import WeekNav from "./elements/WeekNav"

const GameReport = ({ sportTag, leagueTag }) => {

  const leagueData = output[sportTag][leagueTag]
  const week = parseInt(leagueData.meta.week)

  const teamLabels = Object.fromEntries(
    Object.values(leagueData.teams.metadata).map(meta => (
      [
        meta.name,
        <TeamLabel meta={meta} />
      ]
    ))
  )

  const [selectedWeek, setSelectedWeek] = React.useState(week)

  const proj = leagueData.teams.proj[selectedWeek]
  proj.sort((a, b) => b.proj[0] - a.proj[0])

  return (
    <Container top={2}>
      <div className="center">
        <Container top={2}>
          <h2>Game Report</h2>
          <h4>Week {week}</h4>
        </Container>
      </div>

      <UpcomingGames
        matchupImportance={leagueData.league.matchupImportance}
        teamLabels={teamLabels}
        week={week}
      />

      <Container>
        <SectionTitle>Team Projections</SectionTitle>
        <Container>
          <WeekNav
            min={1}
            max={week}
            week={selectedWeek}
            setWeek={setSelectedWeek}
          />
        </Container>
        <Container>
          <table className="x3-table x3-bordered" style={{ maxWidth: '240px', }}>
            <tbody>
              <tr className="th-border">
                <th aria-label="away">Team</th>
                <th aria-label="away">Proj</th>
              </tr>
              {proj.map(x => (
                <tr key={x.team}>
                  <td>{teamLabels[x.team]}</td>
                  <td>{x.proj[0].toFixed(1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Container>
      </Container>

    </Container>
  )
}

export default GameReport
