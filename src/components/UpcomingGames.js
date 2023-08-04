import * as React from "react"
import Container from "./elements/Container"
import SectionTitle from "./elements/SectionTitle"
import WeekNav from "./elements/WeekNav"

const ColoredCell = ({ value }) => {
  const opacity = (value / 90).toFixed(2)
  return (
    <td style={{ backgroundColor: `rgb(83, 185, 255, ${opacity})` }}>
      {value}
    </td>
  )
}

const UpcomingGames = ({ matchupImportance, teamLabels, week }) => {
  const [selectedWeek, setSelectedWeek] = React.useState(week)
  const isPlayoffs = selectedWeek > 0 && !matchupImportance[selectedWeek]

  return (
    <Container size={24}>
      <SectionTitle>Upcoming Games</SectionTitle>

      <Container>
        <WeekNav
          min={1}
          max={week}
          week={selectedWeek}
          setWeek={setSelectedWeek}
        />
      </Container>

      <Container>
        {isPlayoffs ? (
          <div className="center">Playoffs In Progress</div>
        ) : (
          <table className="x3-table x3-bordered" style={{ maxWidth: '400px', tableLayout: 'fixed' }}>
            <tbody>
              <tr className="th-border">
                <th aria-label="away">Matchup</th>
                <th aria-label="vs" width="40px" />
                <th aria-label="home" />
                <th width="80px">Importance</th>
              </tr>
              {
                matchupImportance[selectedWeek].map(x => (
                  <tr key={x.home}>
                    <td>{teamLabels[x.away]}</td>
                    <td>vs</td>
                    <td>{teamLabels[x.home]}</td>
                    <ColoredCell value={x.importance} />
                  </tr>
                ))
              }
            </tbody>
          </table>
        )}
      </Container>
    </Container>
  )
}

export default UpcomingGames
