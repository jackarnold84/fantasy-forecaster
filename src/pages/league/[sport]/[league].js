import { navigate } from "gatsby"
import * as React from "react"
import output from '../../../../data/output.json'
import Layout from "../../../components/Layout"
import Report from "../../../components/Report"

const LeaguePage = (props) => {
  const sportTag = props.params.sport;
  const leagueTag = props.params.league;

  // return home if league does not exist
  if (!(sportTag in output) || !(leagueTag in output[sportTag])) {
    navigate('/')
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
