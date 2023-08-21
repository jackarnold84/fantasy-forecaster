export const capitalize = s => s && s[0].toUpperCase() + s.slice(1)

export const percent = (x) => {
  if (x === 0 || x >= 100) {
    return `${x.toFixed(0)}%`
  }
  return `${x.toFixed(1)}%`
}

export const ordinal_suffix = (i) => {
  var j = i % 10
  var k = i % 100
  if (j === 1 && k !== 11) {
    return i + "st"
  }
  if (j === 2 && k !== 12) {
    return i + "nd"
  }
  if (j === 3 && k !== 13) {
    return i + "rd"
  }
  return i + "th"
}

export const americanOdds = (dec) => {
  let x = dec
  let a = undefined;
  if (x >= 0.999 || x <= 0) {
    return undefined
  }

  // with vig
  if (x > 0.85) {
    x *= Math.max(1.316 - 0.314 * x, 1.01)
  } else {
    x *= 1.05
  }

  // convert to odds
  if (x >= 1.00) x = 100000
  else if (x >= 0.5) a = 100 * x / (1 - x)
  else if (x <= 0.5) a = 100 / x - 100

  // round
  const rnd = x < 0.5 ? Math.floor : Math.ceil
  const sign = x < 0.5 ? '+' : '-'
  if (a < 400) a = 10 * rnd(a / 10)
  else if (a < 1000) a = 50 * rnd(a / 50)
  else if (a < 4000) a = 100 * rnd(a / 100)
  else if (a < 10000) a = 500 * rnd(a / 500)
  else if (a < 40000) a = 1000 * rnd(a / 1000)
  else if (a < 90000) a = 10000 * rnd(a / 10000)
  else a = 100000

  return `${sign}${a}`
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
