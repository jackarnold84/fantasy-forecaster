import * as React from "react"

const TeamLabel = ({ meta }) => {
  return (
    <span>
      <img
        src={meta.img}
        height={18}
        alt={meta.team}
        style={{ verticalAlign: 'top', paddingRight: '10px' }}
      />
      {meta.name}
    </span>
  )
}

export default TeamLabel
