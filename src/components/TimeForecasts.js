import * as React from "react"
import { plotPalette } from "../utils/palette"
import Container from "./elements/Container"
import LinePlot from "./elements/Lineplot"
import SectionTitle from "./elements/SectionTitle"
import TabNav from "./elements/TabNav"

const titleMap = {
  playoffs: 'Make Playoffs',
  championship: 'Win Championship',
  punishment: 'League Punishment',
}

const TimeForecasts = ({ forecasts, teamLabels }) => {
  const [selectedForecast, setSelectedForecast] = React.useState('playoffs')
  const [selectedTeam, setSelectedTeam] = React.useState('all')

  const teams = Object.keys(teamLabels).sort()
  const allForecasts = forecasts[selectedForecast].flat()
  const forecastByTeam = teams.map((t, i) => {
    const filtered = allForecasts.filter(x => x.team === t)
    return {
      name: t,
      x: filtered.map(x => x.week),
      y: filtered.map(x => x.prob * 100),
      marker: { color: plotPalette[i] },
      visible: selectedTeam === 'all' || selectedTeam === t || 'legendonly',
    }
  })
  const yMax = Math.max(...allForecasts.map(x => x.prob * 100))

  return (
    <Container size={24}>
      <SectionTitle>Forecasts Over Time</SectionTitle>

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

      <Container width={150}>
        <select className="x3-select" onChange={(e) => setSelectedTeam(e.target.value)}>
          <option value={'all'}>All Teams</option>
          {teams.map(t => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
      </Container>

      <Container width={500}>
        <div className="center">{titleMap[selectedForecast]}</div>

        <LinePlot
          data={forecastByTeam}
          height={350}
          yaxis={{ ticksuffix: '%', range: [-4, yMax + 4] }}
        />
      </Container>
    </Container>
  )
}

export default TimeForecasts
