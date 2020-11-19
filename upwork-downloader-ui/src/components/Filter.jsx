import React from "react";
import Checkbox from "react-simple-checkbox";

const Filter = ({ classes, onToggleFilter }) => (
  <>
    <div className="uppercase text-gray-500 font-bold text-center">
      Filter by job label
    </div>
    <div className="flex flex-col lg:flex-row pt-2 pb-4 justify-center">
      {classes.map((filter) => (
        <div key={filter.id} className="flex items-baseline mr-4 last:mr-0">
          <div data-testid={filter.id}>
            <Checkbox
              color="#a100ff"
              delay={-1000}
              checked={filter.active}
              size={2}
              tickSize={3}
              onChange={() => onToggleFilter(filter.id)}
            />
          </div>
          <div className="ml-1 text-gray-800 text-base">{filter.label}</div>
        </div>
      ))}
    </div>
  </>
);

export default Filter;
