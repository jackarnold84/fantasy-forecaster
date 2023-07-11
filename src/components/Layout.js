import { Link } from "gatsby"
import * as React from "react"
import '../styles/global.css'
import '../styles/icons.css'

const Layout = ({ children }) => {
  return (
    <div>
      <div>
        <Link to="/" className="plain">
          <div className="x3-container center" style={{ backgroundColor: 'black' }}>
            <h2 className="white-text">Fantasy Forecaster</h2>
          </div>
        </Link>
      </div>

      <div className="x3-container auto" style={{maxWidth: '600px'}}>
        {children}
      </div>
    </div>
  )
}

export default Layout
