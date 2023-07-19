import * as React from "react"

const TabNav = ({ options, selected, setSelected }) => {
  return (
    <div className="x3-row center text">
      <span className="tab-holder">
        {options.map(x => (
          <button
            className={`tab-btn ${x.value === selected && 'tab-btn-selected'}`}
            onClick={() => setSelected(x.value)}
          >
            {x.display}
          </button>
        ))}
      </span>
    </div>
  )
}

export default TabNav
