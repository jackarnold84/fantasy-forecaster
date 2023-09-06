import * as React from "react"
import output from '../../data/output.json'
import Layout from "../components/Layout"
import NotFound from "../components/NotFound"
import Report from "../components/Report"

const LeaguePage = ({ location }) => {
  const urlParams = new Proxy(new URLSearchParams(location.search), {
    get: (searchParams, prop) => searchParams.get(prop),
  });
  const sportTag = urlParams.sport
  const leagueTag = urlParams.tag
  const isValid = sportTag in output && leagueTag in output[sportTag]

  return (
    <Layout>
      {isValid ? (
        <Report
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
