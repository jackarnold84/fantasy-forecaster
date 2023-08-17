import * as React from "react"
import leagueArchive from "../../data/leagueArchive.json"
import output from "../../data/output.json"
import Layout from "../components/Layout"
import Container from "../components/elements/Container"
import baseball from "../images/sports/baseball.png"
import basketball from "../images/sports/basketball.png"
import football from "../images/sports/football.png"
import { capitalize } from "../utils/display"

const iconMap = {
  baseball,
  football,
  basketball,
}

const NavRow = ({ text, sport, path }) => (
  <a href={path} className="x3-link-plain">
    <div className="nav-table-row">
      <img src={iconMap[sport]} alt={sport} height={20} className="nav-table-img" />
      <span className="x3-l8">{text}</span>
    </div>
  </a>
)

const leagueList = Object.values(output).map(sport => (
  Object.values(sport).map(league => league.meta)
)).flat();

const IndexPage = () => {
  return (
    <Layout>
      <Container>
        <div className="auto" style={{ maxWidth: '500px' }}>
          <h4 className="x3-row center nav-table-row">
            Select League:
          </h4>
          {leagueList.map(league => (
            <NavRow
              text={`${league.name} Fantasy ${capitalize(league.sport)} (${league.year})`}
              sport={league.sport}
              path={`league/${league.tag}`}
              key={league.tag}
            />
          ))}
        </div>
      </Container>

      <Container top={56}>
        <div className="auto" style={{ maxWidth: '500px' }}>
          <h4 className="x3-row center nav-table-row">
            Archived Leagues:
          </h4>
          {leagueArchive.leagues.map(league => (
            <NavRow
              text={league.name}
              sport={league.sport}
              path={league.link}
              key={league.name}
            />
          ))}
        </div>
      </Container>

    </Layout>
  )
}

export default IndexPage

export const Head = () => <title>Fantasy Forecaster</title>
