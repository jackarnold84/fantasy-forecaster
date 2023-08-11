import { Link } from "gatsby"
import * as React from "react"
import '../styles/global.css'
import '../styles/icons.css'
import { palette } from "../utils/palette"
import Container from "./elements/Container"

const Layout = ({ children }) => {
  return (
    <div>
      <div>
        <Link to="/" className="plain">
          <div className="x3-container center" style={{ backgroundColor: palette.green }}>
            <h2 className="white-text">Fantasy Forecaster</h2>
          </div>
        </Link>
      </div>

      <div className="auto" style={{ maxWidth: '600px' }}>
        <Container size={32}>
          {children}
        </Container>
      </div>

    </div>
  )
}

export default Layout
