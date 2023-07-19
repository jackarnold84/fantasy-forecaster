export const capitalize = s => s && s[0].toUpperCase() + s.slice(1)

export const percent = (x) => {
    if (x === 0 || x >= 100) {
        return `${x.toFixed(0)}%`
    }
    return `${x.toFixed(1)}%`
}
