import React from "react";
import ClassSelector from "./ClassSelector";
import Moment from "react-moment";
import { CopyToClipboard } from "react-copy-to-clipboard";
import { FaRegCopy } from "react-icons/fa";

const Job = ({ id, details, handler }) => {
  let jobHeader = (
    <div className="flex flex-col w-5/6 pb-2 border-b">
      <div className="flex flex-row justify-between">
        <div className="font-bold text-xl mb-2 w-5/6">
          <span>{details.title}</span>
          <CopyToClipboard text={`https://www.upwork.com/jobs/${id}`}>
            <button className="ml-4">
              <FaRegCopy size="0.8em" />
            </button>
          </CopyToClipboard>
        </div>
        <div className="text-sm text-gray-600 mb-2 w-1/6 text-right">
          <Moment fromNow>{details.date_created}</Moment>
        </div>
      </div>

      <div className="text-sm">
        {details.job_type}
        {`${details.job_type === "Fixed" ? ` - $${details.budget}` : ""}`}
      </div>
    </div>
  );

  return (
    <div className="flex flex-col w-full rounded shadow-lg text-left mb-5 min-h-50 items-end">
      <div className="flex flex-row w-full px-6 py-4">
        <div className="flex justify-center p-4  w-1/6">
          <span className="text-sm"></span>
        </div>
        {jobHeader}
      </div>
      <div className="flex flex-row flex-grow w-full p-4">
        <ClassSelector
          id={id}
          clickHandler={handler}
          selectedOption={details.label}
        />

        <div className="w-5/6 py-4 break-words whitespace-pre-line">
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
