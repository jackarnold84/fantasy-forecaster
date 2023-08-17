import * as React from "react"

const Container = ({ size, top, bottom, width, children, style }) => {
  const defaultPad = size || 8
  const paddingTop = top || defaultPad
  const paddingBottom = bottom || defaultPad
  const padding = { paddingTop: `${paddingTop}px`, paddingBottom: `${paddingBottom}px` }
  const maxWidth = width ? `${width}px` : '100%'
  const customStyle = style || {}

  return (
    <div className="auto" style={{ maxWidth, ...padding, ...customStyle }}>
      {children}
    </div>
  )
}

export default Container
