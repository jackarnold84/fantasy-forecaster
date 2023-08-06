export const capitalize = s => s && s[0].toUpperCase() + s.slice(1)

export const round = (x, pos = 0) => {
  return parseFloat(x.toFixed(pos))
}

export const percent = (x) => {
  if (x === 0 || x >= 100) {
    return `${x.toFixed(0)}%`
  }
  return `${x.toFixed(1)}%`
}

export const positionDisplay = (p) => {
  switch (p) {
    case 'OVR':
      return 'Overall Team'
    case 'QB':
      return 'Quarterbacks'
    case 'RB':
      return 'Running Backs'
    case 'WR':
      return 'Wide Recievers'
    case 'TE':
      return 'Tight Ends'
    case 'B':
      return 'Batters'
    case 'SP':
      return 'Starting Pitchers'
    case 'RP':
      return 'Relief Pitchers'
    case 'P':
      return 'Pitchers'
    default:
      return ''
  }
}
