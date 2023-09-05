import * as React from "react"

const PlayerImage = ({ name, pos, img }) => {
  return (
    <span className="tooltip" style={{ minWidth: '46px' }}>
      <img
        src={img}
        height={30}
        alt={name}
        style={{ verticalAlign: 'top', padding: '0px 2px' }}
      />
      <div className="tooltiptext">
        <span className="bold">{pos}</span>
        {' '}
        {name}
      </div>
    </span>
  )
}

export default PlayerImage
