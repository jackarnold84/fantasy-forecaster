import { Link } from "gatsby"
import * as React from "react"
import { FaExclamationTriangle } from "react-icons/fa"
import { ImSpinner2 } from "react-icons/im"
import styled, { keyframes } from "styled-components"
import Container from "../components/elements/Container"
import GameReport from "../components/GameReport"
import Layout from "../components/Layout"
import PlayerReport from "../components/PlayerReport"
import Report from "../components/Report"

const API_ENDPOINT = 'https://xjnwsfwba3.execute-api.us-east-2.amazonaws.com/Prod/fantasy-forecaster/data';

const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const StyledSpinner = styled(ImSpinner2)`
  animation: ${spin} 1s linear infinite;
`;

const HomeLink = styled(Link)`
  color: #0066cc;
  text-decoration: underline;
  font-size: 16px;
  &:hover {
    color: #0073e6;
  }
`;

const LeaguePage = ({ location }) => {
  const urlParams = new Proxy(new URLSearchParams(location.search), {
    get: (searchParams, prop) => searchParams.get(prop),
  });
  const sportTag = urlParams.sport
  const leagueTag = urlParams.tag
  const view = urlParams.view

  const [leagueData, setLeagueData] = React.useState(null);
  const [isError, setIsError] = React.useState(false);

  React.useEffect(() => {
    const fetchData = async () => {
      try {
        const url = `${API_ENDPOINT}?sport=${sportTag}&tag=${leagueTag}`;
        console.log("fetching data from:", url);
        const response = await fetch(url);
        if (!response.ok) {
          setIsError(true);
          const responseJson = await response.json();
          console.error("api bad response:", JSON.stringify(responseJson, null, 2));
          return;
        }
        const responseJson = await response.json();
        const data = responseJson.data;
        setLeagueData(data);
      } catch (err) {
        console.error("api error occurred:", err);
        setIsError(true);
      }
    };

    fetchData();
  }, [sportTag, leagueTag]);

  if (isError) {
    return (
      <Layout>
        <Container centered>
          <FaExclamationTriangle size={36} />
          <Container top={8} bottom={20}>
            <h3>An unexpected error occurred</h3>
          </Container>
          <HomeLink to="/">Return Home</HomeLink>
        </Container>
      </Layout>
    );
  }

  if (!leagueData) {
    return (
      <Layout>
        <Container centered size={16}>
          <StyledSpinner size={24} />
        </Container>
      </Layout>
    );
  }

  let SelectedReport;
  switch ((view || '').toLowerCase()) {
    case 'players':
      const hasPlayerData = leagueData.players && Object.keys(leagueData.players).length > 0;
      SelectedReport = hasPlayerData ? PlayerReport : Report
      break
    case 'games':
      SelectedReport = GameReport
      break
    default:
      SelectedReport = Report
  }

  return (
    <Layout>
      <SelectedReport
        leagueData={leagueData}
      />
    </Layout>
  )
}

export default LeaguePage

export const Head = () => <title>Fantasy Forecaster</title>
