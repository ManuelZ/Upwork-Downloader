import React from "react";
import ClassSelector from "./ClassSelector";
import Moment from "react-moment";

const Job = ({ id, details, handler }) => {
  return (
    <div className="flex flex-row w-full rounded shadow-lg text-left mb-5 min-h-50">
      <div className="w-1/6">
        <ClassSelector
          id={id}
          clickHandler={handler}
          selectedOption={details.class}
        />
      </div>

      <div className="flex flex-col w-5/6 px-6 py-4">
        <div className="flex flex-row justify-between">
          <div className="font-bold text-xl mb-2">{details.title}</div>
          <div className="text-sm text-gray-600 mb-2">
            <Moment fromNow>{details.date_created}</Moment>
          </div>
        </div>
        <div className="py-4 break-normal">{details.snippet}</div>
      </div>
    </div>
  );
};

function areEqual(prevProps, nextProps) {
  return prevProps.details.class === nextProps.details.class;
}

export default React.memo(Job, areEqual);
