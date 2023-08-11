import * as React from "react"
import { positionDisplay, round } from "../utils/display"
import { positionPalette } from "../utils/palette"
import Barplot from "./elements/Barplot"
import Container from "./elements/Container"
import SectionTitle from "./elements/SectionTitle"
import TabNav from "./elements/TabNav"
import WeekNav from "./elements/WeekNav"

const TeamRatings = ({ ratings, week }) => {
  const [selectedWeek, setSelectedWeek] = React.useState(week)
  const [selectedPosition, setSelectedPosition] = React.useState('OVR')

  const positionOptions = Object.keys(ratings[0]).map(p => (
    { display: p, value: p }
  ))

  const x = ratings[selectedWeek][selectedPosition].map(x => round(x.rating)).reverse()
  const y = ratings[selectedWeek][selectedPosition].map(y => y.team).reverse()
  const xMax = Math.max(...x)
  const xMin = Math.min(...x)
  const baseline = Math.max(Math.min(xMin - 10, 50), 0)

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

      <Container width={500}>
        <div className="center">{positionDisplay(selectedPosition)}</div>

        <Barplot
          data={{
            x, y,
            marker: { color: positionPalette[selectedPosition] }
          }}
          height={300}
          xaxis={{ range: [baseline, xMax * 1.1] }}
        />
      </Container>
    </Container>
  )
}

export default TeamRatings
