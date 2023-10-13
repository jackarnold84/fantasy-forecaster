import * as React from "react"
import output from '../../data/output.json'
import GameReport from "../components/GameReport"
import Layout from "../components/Layout"
import NotFound from "../components/NotFound"
import PlayerReport from "../components/PlayerReport"
import Report from "../components/Report"

const LeaguePage = ({ location }) => {
  const urlParams = new Proxy(new URLSearchParams(location.search), {
    get: (searchParams, prop) => searchParams.get(prop),
  });
  const sportTag = urlParams.sport
  const leagueTag = urlParams.tag
  const view = urlParams.view
  const isValid = sportTag in output && leagueTag in output[sportTag]

  let SelectedReport;
  switch ((view || '').toLowerCase()) {
    case 'players':
      SelectedReport = PlayerReport
      break
    case 'games':
      SelectedReport = GameReport
      break
    default:
      SelectedReport = Report
  }

  return (
    <Layout>
      {isValid ? (
        <SelectedReport
          sportTag={sportTag}
          leagueTag={leagueTag}
        />
      ) : (
        <NotFound />
      )}
    </Layout>
  )
}

export default LeaguePage

export const Head = () => <title>Fantasy Forecaster</title>
