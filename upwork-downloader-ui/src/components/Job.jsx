import React from "react";
import ClassSelector from "./ClassSelector";

const Job = ({ details, handler }) => {
  return (
    <div className="w-full rounded overflow-hidden shadow-lg text-left mt-2">
      <ClassSelector handler={handler} />
      <div className="px-6 py-4">
        <div className="font-bold text-xl mb-2">{details.title}</div>
        <div className="py-4 break-normal">{details.snippet}</div>
      </div>
    </div>
  );
};

export default Job;
