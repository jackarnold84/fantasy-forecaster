import * as React from "react"

const TeamLabel = ({ meta }) => {
  return (
    <span>
      <img
        src={meta.img}
        width={18}
        height={18}
        alt={meta.team}
        style={{ verticalAlign: 'bottom', paddingRight: '10px' }}
      />
      {meta.name}
    </span>
  )
}

export default TeamLabel
