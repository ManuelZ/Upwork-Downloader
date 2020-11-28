import React, { useState } from "react";
import LabelSelector from "./LabelSelector";
import Moment from "react-moment";
import Truncate from "react-truncate";

const Job = ({ id, details, handler }) => {
  const [truncated, setTruncated] = useState(true);
  const [firstRender, setFirstRender] = useState(true);

  /* Gets called by the Truncate component when it is indeed, truncated */
  const handleTruncate = (isTruncated) => {
    setTruncated(isTruncated);
  };

  const toggleLines = React.useCallback((event) => {
    event.preventDefault();
    setTruncated(!truncated);
    setFirstRender(false);
  }, [truncated, setTruncated]);

  let jobHeader = (
    <div className="flex flex-col w-full lg:w-5/6 pb-2 border-b">
      <div className="font-bold text-xl mb-2 ">
        <span className="text-justify">
          <a
            href={`https://www.upwork.com/jobs/${id}`}
            target="_blank"
            rel="noreferrer"
          >
            {details.title}
          </a>
        </span>
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

  return (
    <div className="flex flex-col w-full rounded shadow-lg text-left py-2 px-1 lg:px-4 mb-6 lg:min-h-50 items-end bg-gray-50">
      <div className="flex flex-row w-full px-6 py-4 justify-between lg:justify-end">
        {jobHeader}
      </div>
      <div className="flex flex-col lg:flex-row flex-grow w-full px-4 pb-4">
        <LabelSelector
          id={id}
          clickHandler={handler}
          selectedOption={details.label || details.predicted}
        />

        <div className="lg:w-5/6 pt-8 pb-2 lg:py-4 break-words whitespace-pre-line text-justify">
          <Truncate
            lines={truncated && 5}
            ellipsis={
              <span>
                ...{" "}
                <a
                  className="text-indigo-700 font-semibold hover:underline"
                  href="#"
                  onClick={toggleLines}
                >
                  Show more
                </a>
              </span>
            }
            onTruncate={handleTruncate}
          >
            {details.snippet}
          </Truncate>
          {!truncated && !firstRender && (
            <span>
              <a
                className="text-indigo-700 font-semibold hover:underline"
                href="#"
                onClick={toggleLines}
              >
                {" "}
                Show less
              </a>
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

function areEqual(prevProps, nextProps) {
  return prevProps.details.label === nextProps.details.label;
}

export default React.memo(Job, areEqual);
