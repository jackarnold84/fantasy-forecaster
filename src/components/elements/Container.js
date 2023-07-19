import * as React from "react"

const Container = ({ size, top, bottom, children }) => {
  const defaultPad = size || 8
  const paddingTop = top || defaultPad
  const paddingBottom = bottom || defaultPad
  const padding = { paddingTop: `${paddingTop}px`, paddingBottom: `${paddingBottom}px` }

  return (
    <div style={padding}>
      {children}
    </div>
  )
}

export default Container
