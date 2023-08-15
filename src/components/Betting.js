import * as React from "react"
import { americanOdds } from "../utils/display"
import Container from "./elements/Container"
import SectionTitle from "./elements/SectionTitle"
import TabNav from "./elements/TabNav"

const Betting = ({ forecasts, week, teamLabels }) => {
  const [selectedBet, setSelectedBet] = React.useState('championship')
  const validOdds = forecasts[selectedBet][week].filter(x => americanOdds(x.prob))

  return (
    <Container size={24}>
      <SectionTitle>Betting Odds</SectionTitle>

      <Container top="0">
        <TabNav
          options={[
            { display: 'Playoffs', value: 'playoffs' },
            { display: 'Championship', value: 'championship' },
            { display: 'Punishment', value: 'punishment' },
          ]}
          selected={selectedBet}
          setSelected={setSelectedBet}
        />
      </Container>

      <Container>
        {/* <div className="center">{titleMap[selectedBet]}</div> */}
        <table className="x3-table" style={{ maxWidth: '200px' }}>
          <tbody>
            {
              validOdds.map(x => (
                <tr key={x.team}>
                  <td>{teamLabels[x.team]}</td>
                  <td style={{ textAlign: 'center' }}>{americanOdds(x.prob)}</td>
                </tr>
              ))
            }
          </tbody>
        </table>
        {
          validOdds.length === 0 && (
            <Container size={32}>
              <div className="center">
                <i>No bets available</i>
              </div>
            </Container>
          )
        }
      </Container>

    </Container>
  )
}

export default Betting
