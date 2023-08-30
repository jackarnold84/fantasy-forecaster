import { Link } from "gatsby"
import * as React from "react"
import Layout from "../components/Layout"

const NotFoundPage = () => {
  const [isReady, setIsReady] = React.useState(null)
  React.useEffect(() => {
    setTimeout(() => { setIsReady(true) }, 1000)
  }, [])

  return (
    <Layout>
      {isReady &&
        <div className="center">
          <h2 className="x3-b16">
            <i className="bi bi-x-circle x3-r8" />
            Page Not Found
          </h2>
          <Link to="/" className="x3-link">
            <div>
              <span className="x3-l8">Return Home</span>
            </div>
          </Link>
        </div>
      }
    </Layout>
  )
}

export default NotFoundPage

export const Head = () => <title>Not found</title>
