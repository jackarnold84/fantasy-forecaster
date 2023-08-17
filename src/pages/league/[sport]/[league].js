import * as React from "react"
import output from '../../../../data/output.json'
import Layout from "../../../components/Layout"
import Report from "../../../components/Report"
import NotFoundPage from "../../404"

const LeaguePage = (props) => {
  const sportTag = props.params.sport;
  const leagueTag = props.params.league;
  const isValid = sportTag in output && leagueTag in output[sportTag];
  const [isReady, setIsReady] = React.useState(null)
  React.useEffect(() => { setIsReady(true) }, [])

  if (!isReady) {
    return <Layout />
  } else if (!isValid) {
    return <NotFoundPage />
  }

  return (
    <Layout>
      <Report
        sportTag={sportTag}
        leagueTag={leagueTag}
      />
    </Layout>
  )
}

export default LeaguePage

export const Head = () => <title>Fantasy Forecaster</title>
