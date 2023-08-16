import * as React from "react"
import { palette } from "../utils/palette"
import Container from "./elements/Container"
import SectionTitle from "./elements/SectionTitle"
import Subtext from "./elements/Subtext"
import TabNav from "./elements/TabNav"

const ColoredText = ({ value }) => {
  const color = value >= 1.0 ? palette.green : value <= -1.0 ? palette.red : 'black'
  return (
    <td style={{ color }}>
      {value >= 0 ? `+${value}` : value}
    </td>
  )
}

const ScheduleStrength = ({ expectedWins, sos, teamLabels }) => {
  const [selectedView, setSelectedView] = React.useState('wins')
  const viewOptions = [
    { display: 'Expected Wins', value: 'wins' },
    { display: 'Points Against', value: 'points' },
  ]

  return (
    <Container size={24}>
      <SectionTitle>Strength of Schedule</SectionTitle>

      <Container top="0">
        <TabNav
          options={viewOptions}
          selected={selectedView}
          setSelected={setSelectedView}
        />
      </Container>

      {selectedView === 'wins' &&
        <Container>
          <table className="x3-table x3-bordered">
            <tbody>
              <tr className="th-border">
                <th>Team</th>
                <th>Expected</th>
                <th>Actual</th>
                <th>Difference</th>
              </tr>
              {
                expectedWins.map(x => (
                  <tr key={x.team}>
                    <td>{teamLabels[x.team]}</td>
                    <td>{x.expected.toFixed(1)}</td>
                    <td>{x.actual}</td>
                    <ColoredText value={x.diff.toFixed(1)} />
                  </tr>
                ))
              }
            </tbody>
          </table>
          <Subtext>
            Shows expected number of wins if the schedule was re-randomized
          </Subtext>
        </Container>
      }

      {selectedView === 'points' &&
        <Container>
          <table className="x3-table x3-bordered">
            <tbody>
              <tr className="th-border">
                <th>Team</th>
                <th>Current</th>
                <th>Future</th>
              </tr>
              {
                sos.map(x => (
                  <tr key={x.team}>
                    <td>{teamLabels[x.team]}</td>
                    <td>{x.current.toFixed(1)}</td>
                    <td>{x.future > 0 ? x.future.toFixed(1) : '--'}</td>
                  </tr>
                ))
              }
            </tbody>
          </table>
          <Subtext>
            Shows average points against and expected points against
            for the remainder of the season
          </Subtext>
        </Container>
      }

    </Container>
  )
}

export default ScheduleStrength
