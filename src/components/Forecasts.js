import * as React from "react"
import Barplot from "./elements/Barplot"
import Container from "./elements/Container"
import SectionTitle from "./elements/SectionTitle"
import TabNav from "./elements/TabNav"
import WeekNav from "./elements/WeekNav"

const Forecasts = ({ forecasts, week }) => {
  const [selectedWeek, setSelectedWeek] = React.useState(week)
  const [selectedForecast, setSelectedForecast] = React.useState('playoffs')

  const colorMap = {
    playoffs: '#1287A8',
    championship: '#6F7E47',
    punishment: '#AD2A1A',
  }

  const titleMap = {
    playoffs: 'Make Playoffs',
    championship: 'Win Championship',
    punishment: 'League Punishment',
  }

  const x = forecasts[selectedForecast][selectedWeek].map(x => x.prob * 100).reverse()
  const y = forecasts[selectedForecast][selectedWeek].map(y => y.team).reverse()
  const xMax = Math.max(...x)

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
            x, y,
            marker: { color: colorMap[selectedForecast] },
          }}
          height={350}
          xaxis={{ ticksuffix: '%', range: [0, xMax * 1.2] }}
        />
      </Container>
    </Container>
  )
}

export default Forecasts
