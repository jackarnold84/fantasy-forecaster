import * as React from "react"
import Container from "./elements/Container"
import SectionTitle from "./elements/SectionTitle"

const Standings = ({ standings, teamLabels }) => {
  return (
    <Container size={16}>
      <SectionTitle>Standings</SectionTitle>

      <Container>
        <table className="x3-table x3-bordered">
          <tbody>
            <tr className="th-border">
              <th aria-label="rank" />
              <th aria-label="space" />
              <th>Team</th>
              <th>Wins</th>
              <th>Avg</th>
            </tr>
            {
              standings.league.map(x => (
                <tr key={x.rank}>
                  <td>{x.rank}</td>
                  <td />
                  <td>{teamLabels[x.team]}</td>
                  <td>{x.wins}</td>
                  <td>{x.avg.toFixed(1)}</td>
                </tr>
              ))
            }
          </tbody>
        </table>
      </Container>
    </Container>
  )
}

export default Standings
