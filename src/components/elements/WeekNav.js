import * as React from "react";
import { BsFillCaretLeftFill, BsFillCaretRightFill } from "react-icons/bs";

const WeekNav = ({ min, max, week, setWeek }) => {
  return (
    <div className="center">
      <button
        className="nav-button"
        disabled={week <= min}
        onClick={() => { setWeek(week - 1) }}
      >
        <BsFillCaretLeftFill />
      </button>
      <span style={{ display: 'inline-block', minWidth: '72px' }}>
        {week === 0 ? 'Preseason' : `Week ${week}`}
      </span>
      <button
        className="nav-button"
        disabled={week >= max}
        onClick={() => { setWeek(week + 1) }}
      >
        <BsFillCaretRightFill />
      </button>
    </div>
  )
}

export default WeekNav
