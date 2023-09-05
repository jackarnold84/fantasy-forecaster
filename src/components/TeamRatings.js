import * as React from "react"
import { scalePalette } from "../utils/palette"
import Container from "./elements/Container"
import PlayerImage from "./elements/PlayerImage"
import SectionTitle from "./elements/SectionTitle"
import TabNav from "./elements/TabNav"
import WeekNav from "./elements/WeekNav"

const RatingCircle = ({ value }) => {
  const v = parseFloat(value.toFixed(0))
  let scale = 0
  if (v >= 90) scale = 8
  else if (v >= 85) scale = 7
  else if (v >= 80) scale = 6
  else if (v >= 75) scale = 5
  else if (v >= 70) scale = 4
  else if (v >= 65) scale = 3
  else if (v >= 60) scale = 2
  else if (v >= 55) scale = 1
  return (
    <div className="rating-circle" style={{ borderColor: scalePalette[scale] }}>
      {value.toFixed(0)}
    </div>
  )
}

const TeamRatings = ({ ratings, rosters, players, week }) => {
  const [selectedWeek, setSelectedWeek] = React.useState(week)
  const [selectedPosition, setSelectedPosition] = React.useState('OVR')

  const positionOptions = Object.keys(ratings[0]).map(p => (
    { display: p, value: p }
  )).filter(p => (
    !['K', 'DST'].includes(p.value)
  ))
  const selectedRatings = ratings[selectedWeek][selectedPosition]
  const selectedRosters = rosters[selectedWeek]

  return (
    <Container size={24}>
      <SectionTitle>Team Ratings</SectionTitle>

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
            {selectedRatings.map(x => {
              const fullRoster = selectedRosters[x.team]
              const filteredRoster = fullRoster.filter(
                x => selectedPosition === 'OVR' || players[x]?.group === selectedPosition
              )

              return (
                <tr key={x.team}>
                  <td width="52px">
                    <RatingCircle value={x.rating} />
                  </td>
                  <td>{x.team}</td>
                  <td width="140px">
                    {filteredRoster.slice(0, 3).map(p => (
                      <PlayerImage
                        name={players[p].name}
                        pos={players[p].pos}
                        img={players[p].img}
                        key={p}
                      />
                    ))}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </Container>
    </Container>
  )
}

export default TeamRatings
