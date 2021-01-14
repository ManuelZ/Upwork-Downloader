import React from "react";
import Plotly from "plotly.js-cartesian-dist";
import createPlotlyComponent from "react-plotly.js/factory";
const Plot = createPlotlyComponent(Plotly);

const ScoreDisplay = ({ Good, Maybe, Bad }) => {
  return (
    <div className="w-1/3 lg:w-1/6 px-4">
      <Plot
        className="w-full max-h-20"
        useResizeHandler={true}
        data={[
          {
            type: "bar",
            y: ["Bad", "Maybe", "Good"],
            x: [Bad, Maybe, Good],
            orientation: "h",
            hoverinfo: "skip",
          },
        ]}
        layout={{
          font: { size: 10 },
          autosize: true,
          margin: { l: 40, r: 0, t: 12, b: 12 },
          showlegend: false,
          paper_bgcolor: "#f9fafb",
          plot_bgcolor: "#f9fafb",
        }}
        config={{ displayModeBar: false }}
      />
    </div>
  );
};

export default ScoreDisplay;
