import * as React from "react"

const Card = ({ children, className = "" }) => {
  return (
    <section className={`dashboard-card ${className}`.trim()}>
      {children}
    </section>
  )
}

export default Card
