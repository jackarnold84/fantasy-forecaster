import { Link } from "gatsby"
import * as React from "react"

const NotFound = () => {
  const [isReady, setIsReady] = React.useState(null)
  React.useEffect(() => {
    setTimeout(() => { setIsReady(true) }, 1000)
  }, [])

  return (
    <div>
      {isReady &&
        <div className="center">
          <h2 className="x3-b16">
            Page Not Found
          </h2>
          <Link to="/" className="x3-link">
            <div>
              <span className="x3-l8">Return Home</span>
            </div>
          </Link>
        </div>
      }
    </div>
  )
}

export default NotFound
