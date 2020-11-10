import React from "react";
import LabelSelector from "./LabelSelector";
import Moment from "react-moment";
import { CopyToClipboard } from "react-copy-to-clipboard";
import { FaRegCopy } from "react-icons/fa";

const Job = ({ id, details, handler }) => {
  let jobHeader = (
    <div className="flex flex-col lg:w-5/6 pb-2 border-b">
      <div className="flex flex-row justify-between">
        <div className="font-bold text-xl mb-2 ">
          <span className="text-justify">{details.title}</span>
          <CopyToClipboard text={`https://www.upwork.com/jobs/${id}`}>
            <button className="ml-4">
              <FaRegCopy size="0.8em" />
            </button>
          </CopyToClipboard>
        </div>
      </div>

      <div className="flex flex-row justify-between mt-1">
        <div className="text-sm">
          {details.job_type}
          {`${details.job_type === "Fixed" ? ` - $${details.budget}` : ""}`}
        </div>
        <div className="text-sm text-gray-600 text-right">
          <Moment fromNow>{details.date_created}</Moment>
        </div>
      </div>
    </div>
  );

  let horizontal_spacer = (
    <div className="flex justify-center justify-around lg:p-4 lg:w-1/6">
      <span className="text-sm"></span>
    </div>
  );

  return (
    <div className="flex flex-col w-full rounded shadow-lg text-left px-1 lg:px-4 mb-5 min-h-50 items-end">
      <div className="flex flex-row w-full px-6 py-4">
        {horizontal_spacer}
        {jobHeader}
      </div>
      <div className="flex flex-col lg:flex-row flex-grow w-full p-4">
        <LabelSelector
          id={id}
          clickHandler={handler}
          selectedOption={details.label || details.predicted}
        />

        <div className="lg:w-5/6 py-8 lg:py-4 break-words whitespace-pre-line text-justify">
          {details.snippet}
        </div>
      </div>
    </div>
  );
};

function areEqual(prevProps, nextProps) {
  return prevProps.details.label === nextProps.details.label;
}

export default React.memo(Job, areEqual);
