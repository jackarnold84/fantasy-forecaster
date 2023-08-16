import * as React from "react"
import Container from "./Container"

const SectionTitle = ({ children }) => {
  return (
    <Container top="0">
      <h3 className="center">{children}</h3>
    </Container>
  )
}

export default SectionTitle
