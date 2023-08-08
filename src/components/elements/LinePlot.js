import * as React from "react";
import Loadable from "react-loadable";
import { plotlyConfig, plotlyLayout, plotlyProps } from '../../utils/plotly';

const LinePlot = ({ data, height, xaxis = {}, yaxis = {} }) => {

  const Plot = Loadable({
    loader: () => import('react-plotly.js'),
    loading() {
      return <div>Loading...</div>;
    },
  });

  return (
    <Plot
      data={data.map(d => (
        {
          type: 'scatter',
          hovertemplate: 'Week %{x}<br> %{y}',
          ...d,
        }
      ))}
      layout={
        {
          height,
          xaxis: { fixedrange: true, ...xaxis, label: 'week' },
          yaxis: { fixedrange: true, ...yaxis },
          legend: { orientation: 'h', y: -0.2 },
          ...plotlyLayout,
        }
      }
      config={plotlyConfig}
      {...plotlyProps}
    />
  )
}

export default LinePlot
