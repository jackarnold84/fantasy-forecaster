import { Link } from "gatsby"
import * as React from "react"
import Layout from "../components/Layout"

const NotFoundPage = () => {
  return (
    <Layout>
      <div className="center">
        <h2 className="x3-b16">Page Not Found</h2>
        <Link to="/" className="x3-link-plain">
          <div>
            <i className="bi bi-arrow-return-left" />
            <span className="x3-l8">Return Home</span>
          </div>
        </Link>
      </div>
    </Layout>
  )
}

export default NotFoundPage

export const Head = () => <title>Not found</title>
