import * as React from "react";
import Loadable from "react-loadable";
import { plotlyConfig, plotlyLayout, plotlyProps } from '../../utils/plotly';

const Barplot = ({ data, height, xaxis = {}, yaxis = {} }) => {

  const Plot = Loadable({
    loader: () => import('react-plotly.js'),
    loading() {
      return <div>Loading...</div>;
    },
  });

  return (
    <Plot
      data={[
        {
          type: 'bar',
          orientation: 'h',
          texttemplate: '%{x}',
          textposition: 'outside',
          outsidetextfont: { size: '12' },
          name: '',
          hovertemplate: '%{y}<br> %{x}',
          ...data,
        },
      ]}
      layout={
        {
          height,
          xaxis: { visible: false, fixedrange: true, ...xaxis },
          yaxis: { fixedrange: true, ...yaxis },
          ...plotlyLayout,
        }
      }
      config={plotlyConfig}
      {...plotlyProps}
    />
  )
}

export default Barplot
