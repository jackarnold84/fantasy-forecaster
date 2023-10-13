import * as React from "react"
import output from "../../data/output.json"
import { capitalize } from "../utils/display"
import Container from "./elements/Container"
import PlayerImage from "./elements/PlayerImage"
import TabNav from "./elements/TabNav"
import WeekNav from "./elements/WeekNav"

const PlayerReport = ({ sportTag, leagueTag }) => {

  const leagueData = output[sportTag][leagueTag]
  const sport = capitalize(leagueData.meta.sport)
  const week = parseInt(leagueData.meta.week)
  const players = leagueData.players

  const [selectedWeek, setSelectedWeek] = React.useState(week)
  const [selectedPosition, setSelectedPosition] = React.useState('ALL')

  let positionOptions = []
  if (sport === 'Football') {
    positionOptions = ['QB', 'RB', 'WR', 'TE', 'DST', 'K']
  } else {
    positionOptions = Object.values(players).map(p => p.group)
    positionOptions.sort()
    positionOptions = [...new Set(positionOptions)]
  }
  positionOptions = ['ALL', ...positionOptions]
  positionOptions = positionOptions.map(p => ({ display: p, value: p }))

  let playerList = Object.values(players).filter(
    p => selectedPosition === 'ALL' || selectedPosition === p.group
  )
  playerList.sort((a, b) => b.ratings[selectedWeek] - a.ratings[selectedWeek])
  playerList = playerList.slice(0, 50)

  return (
    <Container top={2}>
      <div className="center">
        <Container top={2}>
          <h2>Player Ratings</h2>
        </Container>
      </div>

      <Container>
        <WeekNav
          min={0}
          max={week}
          week={selectedWeek}
          setWeek={setSelectedWeek}
        />
      </Container>

      <Container top="0">
        <TabNav
          options={positionOptions}
          selected={selectedPosition}
          setSelected={setSelectedPosition}
        />
      </Container>

      <Container>
        <table className="x3-table x3-tvert tight-table" style={{ maxWidth: '290px', }}>
          <tbody>
            {playerList.map((p, i) => (
              <tr key={p.id}>
                <td style={{ fontSize: '12px' }}>{i + 1}</td>
                <td>
                  <PlayerImage
                    name={p.name}
                    pos={p.pos}
                    img={p.img}
                  />
                </td>
                <td>{p.name}</td>
                <td>{(p.ratings[selectedWeek] || 0).toFixed(1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Container>

    </Container>
  )
}

export default PlayerReport
