import * as React from "react"
import output from '../../data/output.json'
import Layout from "../components/Layout"
import { capitalize } from "../utils/display"

const leagueList = Object.values(output).map(sport => (
  Object.values(sport).map(league => league.meta)
)).flat();

const NavRow = ({ text, icon, path }) => (
  <a href={path} className="x3-link-plain">
    <div className="nav-table-row">
      <i className={icon} />
      <span className="x3-l8">{text}</span>
    </div>
  </a>
)

const IndexPage = () => {
  return (
    <Layout>
      <div className="auto" style={{ maxWidth: '500px' }}>
        <div className="x3-row center semibold nav-table-row">
          Select League:
        </div>
        {leagueList.map(league => (
          <NavRow
            text={`${league.name} Fantasy ${capitalize(league.sport)} (${league.year})`}
            icon="bi-people-fill"
            path={`league/${league.tag}`}
            key={league.tag}
          />
        ))}
      </div>
    </Layout>
  )
}

export default IndexPage

export const Head = () => <title>Fantasy Forecaster</title>
