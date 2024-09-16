import { Link } from "gatsby"
import * as React from "react"
import { BiLogoGithub } from "react-icons/bi"
import logoWhite from "../images/iconWhite.png"
import '../styles/global.css'
import { palette } from "../utils/palette"
import Container from "./elements/Container"

const Layout = ({ children }) => {
  return (
    <div>
      <div>
        <Link to="/" className="plain">
          <div className="x3-container center" style={{ backgroundColor: palette.green }}>
            <h2 className="white-text bold">
              <span>
                <img
                  src={logoWhite}
                  height={32}
                  alt={'logo'}
                  style={{ verticalAlign: 'top', paddingRight: '10px' }}
                />
                Fantasy Forecaster
              </span>
            </h2>
          </div>
        </Link>
      </div>

      <div className="auto" style={{ maxWidth: '600px', minHeight: 'calc(100vh - 112px)' }}>
        <Container size={16}>
          {children}
        </Container>
      </div>

      <div className="x3-row center" style={{ backgroundColor: palette.green }}>
        <div className="white-text subtext">
          <span className="x3-r16">
            Created by Jack Arnold
          </span>
          <a
            href="https://github.com/jackarnold84/fantasy-forecaster"
            className="x3-link-plain-white"
          >
            <BiLogoGithub size={16} style={{ verticalAlign: 'bottom' }} />
            <span className="x3-l4">
              Github
            </span>
          </a>
        </div>
      </div>
    </div>
  )
}

export default Layout
