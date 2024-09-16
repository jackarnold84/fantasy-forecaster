import { Link } from "gatsby";
import * as React from "react";
import { FaArchive, FaBaseballBall, FaBasketballBall, FaFootballBall } from "react-icons/fa";
import Layout from "../components/Layout";
import Container from "../components/elements/Container";
import config from "../config.json";
import { capitalize } from "../utils/display";

const getIcon = (IconComponent) => <IconComponent size={20} style={{ verticalAlign: 'bottom' }} />;

const iconMap = {
  baseball: getIcon(FaBaseballBall),
  football: getIcon(FaFootballBall),
  basketball: getIcon(FaBasketballBall),
  archive: getIcon(FaArchive),
}

const NavRow = ({ text, sport, path, isExternal }) => {
  const content = (
    <div className="nav-table-row">
      {iconMap[sport]}
      <span className="x3-l8">{text}</span>
    </div>
  );

  return isExternal ? (
    <a href={path} className="x3-link-plain" target="_blank" rel="noopener noreferrer">
      {content}
    </a>
  ) : (
    <Link to={path} className="x3-link-plain">
      {content}
    </Link>
  );
}

const leagueList = config.leagues;
const leagueArchive = config.archivedLeagues;

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
              path={`league/?sport=${league.sport}-${league.year}&tag=${league.tag}`}
              key={`${league.sport}-${league.year}-${league.tag}`}
              isExternal={false}
            />
          ))}
        </div>
      </Container>

      <Container top={56}>
        <div className="auto" style={{ maxWidth: '500px' }}>
          <h4 className="x3-row center nav-table-row">
            Archived Leagues:
          </h4>
          {leagueArchive.map(league => (
            <NavRow
              text={league.name}
              sport="archive"
              path={league.link}
              key={league.name}
              isExternal={true}
            />
          ))}
        </div>
      </Container>
    </Layout>
  )
}

export default IndexPage

export const Head = () => <title>Fantasy Forecaster</title>
