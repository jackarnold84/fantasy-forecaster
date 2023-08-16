import * as React from "react"

const Container = ({ size, top, bottom, width, children }) => {
  const defaultPad = size || 8
  const paddingTop = top || defaultPad
  const paddingBottom = bottom || defaultPad
  const padding = { paddingTop: `${paddingTop}px`, paddingBottom: `${paddingBottom}px` }
  const maxWidth = width ? `${width}px` : '100%'

  return (
    <div className="auto" style={{ maxWidth, ...padding }}>
      {children}
    </div>
  )
}

export default Container
