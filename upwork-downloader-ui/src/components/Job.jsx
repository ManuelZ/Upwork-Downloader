import React from "react";
import ClassSelector from "./ClassSelector";

const Job = ({ details, handler }) => {
  return (
    <div className="flex flex-row w-full rounded shadow-lg text-left mb-5 min-h-50">
      <div className="w-1/6">
        <ClassSelector id={details.id} handler={handler} />
      </div>

      <div className="flex flex-col w-5/6 px-6 py-4">
        <div className="font-bold text-xl mb-2">{details.title}</div>
        <div className="py-4 break-normal">{details.snippet}</div>
      </div>
    </div>
  );
};

export default Job;
