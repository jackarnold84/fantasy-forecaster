import * as React from "react"
import Layout from "../components/Layout"
import NotFound from "../components/NotFound"

const NotFoundPage = () => {
  return (
    <Layout>
      <NotFound />
    </Layout>
  )
}

export default NotFoundPage

export const Head = () => <title>Not found</title>
