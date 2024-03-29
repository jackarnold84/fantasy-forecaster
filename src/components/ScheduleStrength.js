import * as React from "react"
import { ordinal_suffix } from "../utils/display"
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

const OrdinalText = ({ value, max }) => {
  const color = value === max ? palette.green : value === 1 ? palette.red : 'black'
  const text = value > 0 ? ordinal_suffix(value) : '--'
  return (
    <td style={{ color }}>
      {text}
    </td>
  )
}

const ScheduleStrength = ({ expectedWins, sos, teamLabels, isPreseason }) => {
  const [selectedView, setSelectedView] = React.useState(isPreseason ? 'points' : 'wins')
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
                <th>Future SOS</th>
              </tr>
              {
                sos.map(x => (
                  <tr key={x.team}>
                    <td>{teamLabels[x.team]}</td>
                    <td>{x.current.toFixed(1)}</td>
                    <OrdinalText value={x.future} max={sos.length} />
                  </tr>
                ))
              }
            </tbody>
          </table>
          <Subtext>
            Shows average points against and strength of schedule rank
            for the remainder of the season (1st is hardest)
          </Subtext>
        </Container>
      }

    </Container>
  )
}

export default ScheduleStrength
