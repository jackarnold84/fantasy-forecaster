import React from "react";
import { BsFillCaretLeftFill, BsFillCaretRightFill } from "react-icons/bs";
import { IoSwapHorizontal } from "react-icons/io5";
import styled from "styled-components";
import { palette } from "../utils/palette";
import Container from "./elements/Container";
import PlayerImage from "./elements/PlayerImage";
import SectionTitle from "./elements/SectionTitle";

const TradePaginationDot = styled.button`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: 0px solid #888;
  background: ${({ active }) => (active ? palette.blue : '#d4d4d4ff')};
  cursor: pointer;
  padding: 0;
`;

const BetaTag = styled.div`
  font-size: 11px;
  font-weight: 500;
  color: #767c81ff;
  letter-spacing: 1px;
`;

const TradeNavButton = ({ onClick, direction }) => (
  <button
    className="nav-button"
    onClick={onClick}
    style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}
    aria-label={direction === 'left' ? 'Previous trade' : 'Next trade'}
  >
    {direction === 'left' ? <BsFillCaretLeftFill size={16} /> : <BsFillCaretRightFill size={16} />}
  </button>
)

const TradeColumn = ({ side, data, players }) => {
  const isRight = side === 'right';
  return (
    <div style={{ flex: 1, padding: '0 12px', textAlign: isRight ? 'right' : 'left' }}>
      <div style={{ fontWeight: 600, marginBottom: '8px', textAlign: 'center' }}>{data.team}</div>
      <table className="x3-table" style={{ minHeight: '110px' }}>
        <tbody>
          {data.players.map(pid => {
            const p = players[pid];
            if (!p) return null;
            return (
              <tr key={pid}>
                {isRight ? (
                  <>
                    <td style={{ padding: '4px 4px', fontSize: '14px', textAlign: 'right', verticalAlign: 'middle' }}>
                      <span className="bold" style={{ marginRight: 4 }}>{p.pos}</span>
                      <span>{p.name}</span>
                    </td>
                    <td width="50" style={{ padding: '4px 2px', verticalAlign: 'middle' }}>
                      <PlayerImage name={p.name} pos={p.pos} img={p.img} />
                    </td>
                  </>
                ) : (
                  <>
                    <td width="50" style={{ padding: '4px 2px', verticalAlign: 'middle' }}>
                      <PlayerImage name={p.name} pos={p.pos} img={p.img} />
                    </td>
                    <td style={{ padding: '4px 4px', fontSize: '14px', verticalAlign: 'middle' }}>
                      <span className="bold" style={{ marginRight: 4 }}>{p.pos}</span>
                      <span>{p.name}</span>
                    </td>
                  </>
                )}
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

const TradeFinder = ({ tradeFinder = [], players = {} }) => {
  const [index, setIndex] = React.useState(0)

  const total = tradeFinder.length
  const current = total ? tradeFinder[index] : null

  const goLeft = () => setIndex(i => (i - 1 + total) % total)
  const goRight = () => setIndex(i => (i + 1) % total)

  return (
    <Container size={16} width={500} centered>
      <SectionTitle>Trade Suggestions</SectionTitle>
      <BetaTag>BETA</BetaTag>

      {current && (
        <Container size={16} style={{ display: 'flex', justifyContent: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', overflowX: 'hidden' }}>
            <TradeColumn side="left" data={current[0]} players={players} />
            <div style={{ width: '60px', textAlign: 'center', paddingTop: '30px' }}>
              <IoSwapHorizontal size={32} />
            </div>
            <TradeColumn side="right" data={current[1]} players={players} />
          </div>
        </Container>
      )}

      {total > 0 && (
        <Container top={8} style={{ display: 'flex', justifyContent: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <TradeNavButton direction="left" onClick={goLeft} />
            <div style={{ display: 'flex', gap: '6px' }}>
              {Array.from({ length: total }).map((_, i) => (
                <TradePaginationDot
                  key={i}
                  active={i === index}
                  onClick={() => setIndex(i)}
                  aria-label={`Go to trade ${i + 1}`}
                />
              ))}
            </div>
            <TradeNavButton direction="right" onClick={goRight} />
          </div>
        </Container>
      )}
    </Container>
  )
}

export default TradeFinder;
