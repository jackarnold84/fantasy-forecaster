import * as React from "react"
import { palette } from "../utils/palette"
import Barplot from "./elements/Barplot"
import Container from "./elements/Container"
import SectionTitle from "./elements/SectionTitle"
import TabNav from "./elements/TabNav"
import WeekNav from "./elements/WeekNav"

const colorMap = {
  playoffs: palette.orange,
  championship: palette.green,
  punishment: palette.red,
}

const titleMap = {
  playoffs: 'Make Playoffs',
  championship: 'Win Championship',
  punishment: 'League Punishment',
}

const formatPercent = (value) => {
  if (value === 0) return '0%'
  if (value === 100) return '100%'
  if (value >= 99 || value < 10) return `${value.toFixed(1)}%`
  return `${value.toFixed(0)}%`
}

const Forecasts = ({ forecasts, week }) => {
  const [selectedWeek, setSelectedWeek] = React.useState(week)
  const [selectedForecast, setSelectedForecast] = React.useState('playoffs')

  const x = forecasts[selectedForecast][selectedWeek].map(x => x.prob * 100).reverse()
  const y = forecasts[selectedForecast][selectedWeek].map(y => y.team).reverse()
  const xMax = Math.max(...x)
  const text = x.map(formatPercent)
  const textposition = x.map(value => value < xMax * 0.16 ? 'outside' : 'inside')

  return (
    <Container size={24}>
      <SectionTitle>Forecasts</SectionTitle>

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
          options={[
            { display: 'Playoffs', value: 'playoffs' },
            { display: 'Championship', value: 'championship' },
            { display: 'Punishment', value: 'punishment' },
          ]}
          selected={selectedForecast}
          setSelected={setSelectedForecast}
        />
      </Container>

      <Container width={500}>
        <div className="center">{titleMap[selectedForecast]}</div>

        <Barplot
          data={{
            x, y, text, textposition,
            marker: { color: colorMap[selectedForecast] },
            hovertemplate: '%{y}<br> %{x:.1f}%',
          }}
          height={350}
          xaxis={{ ticksuffix: '%', range: [0, xMax * 1.2] }}
        />
      </Container>
    </Container>
  )
}

export default Forecasts
