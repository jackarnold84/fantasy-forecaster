import * as React from "react"
import Container from "./Container"

const Subtext = ({ children }) => {
  return (
    <Container top={16}>
      <div className="auto center subtext" style={{ maxWidth: '400px' }}>
        {children}
      </div>
    </Container>
  )
}

export default Subtext
