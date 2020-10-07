import React from "react";
import Checkbox from "react-simple-checkbox";

const Filter = ({ classes, onToggleFilter }) => (
  <div className="p-4">
    <div className="border-b">
      <div className="uppercase text-gray-500 font-bold">
        Filter by class label
      </div>
      <div className="flex pt-2 pb-4 justify-center">
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
    </div>
  </div>
);

export default Filter;
