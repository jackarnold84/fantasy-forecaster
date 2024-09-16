import styled from "styled-components";

const Container = styled.div.attrs(({
  size = 8, top, bottom, width, centered = false, flex = false,
}) => ({
  size,
  top: top !== undefined ? top : size,
  bottom: bottom !== undefined ? bottom : size,
  width,
  centered: centered ? "true" : "false",
  flex: flex ? "true" : "false",
}))`
  margin: auto;
  padding-top: ${props => props.top}px;
  padding-bottom: ${props => props.bottom}px;
  ${({ width }) => width && `
    max-width: ${width}px;
  `}
  ${({ centered }) => centered === "true" && `
    text-align: center;
    justify-content: center;
  `}
  ${({ flex }) => flex === "true" && `
    display: flex;
  `}
`;

export default Container;