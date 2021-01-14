import React, { useState } from "react";
import LabelSelector from "./LabelSelector";
import Moment from "react-moment";
import Truncate from "react-truncate";
import ScoreDisplay from "./ScoreDisplay/ScoreDisplay";

const Job = ({ id, details, handler }) => {
  const [truncated, setTruncated] = useState(true);
  const [firstRender, setFirstRender] = useState(true);

  /* Gets called by the Truncate component when it is indeed, truncated */
  const handleTruncate = (isTruncated) => {
    setTruncated(isTruncated);
  };

  const toggleLines = React.useCallback(
    (event) => {
      event.preventDefault();
      setTruncated(!truncated);
      setFirstRender(false);
    },
    [truncated, setTruncated]
  );

  const { Good, Maybe, Bad } = details;

  return (
    <div className="flex flex-col w-full rounded shadow-lg text-left py-2 px-1 lg:px-4 mb-6 lg:min-h-50 items-end bg-gray-50">
      <div className="flex flex-row w-full p-4">
        <div className="flex flex-col w-1/3 lg:w-1/6 mr-4 lg:mr-0 justify-center">
          <p className="font-light text-left text-sm mb-1">
            Feedback: {details["client.feedback"].toFixed(2)} (
            {details["client.reviews_count"]})
          </p>
          <p className="font-light text-left text-sm">
            Jobs posted: {details["client.jobs_posted"]}
          </p>
        </div>
        <div className="flex flex-wrap w-4/6 content-between border-b">
          <div className="font-bold text-xl mb-2">
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
          <div className="flex flex-row w-full justify-between">
            <div className="text-sm">
              {details.job_type}
              {`${details.job_type === "Fixed" ? ` - $${details.budget}` : ""}`}
            </div>
            <div className="text-sm text-gray-600 text-right">
              <Moment fromNow>{details.date_created}</Moment>
            </div>
          </div>
        </div>

        {!Good ? "" : <ScoreDisplay Good={Good} Maybe={Maybe} Bad={Bad} />}
      </div>
      <div className="flex flex-col lg:flex-row flex-grow w-full px-4 pb-4 justify-end">
        <div className="lg:w-4/6 pt-8 pb-2 lg:py-4 break-words whitespace-pre-line text-justify">
          <Truncate
            lines={truncated && 5}
            ellipsis={
              <span>
                ...{" "}
                <button
                  className="bg-transparent border-none cursor-pointer text-indigo-700 font-semibold hover:shadow-none hover:underline"
                  onClick={toggleLines}
                >
                  Show more
                </button>
              </span>
            }
            onTruncate={handleTruncate}
          >
            {details.snippet}
          </Truncate>
          {!truncated && !firstRender && (
            <span>
              <button
                className="bg-transparent border-none cursor-pointer text-indigo-700 font-semibold hover:shadow-none hover:underline"
                onClick={toggleLines}
              >
                {" "}
                Show less
              </button>
            </span>
          )}
        </div>

        <LabelSelector
          id={id}
          clickHandler={handler}
          selectedOption={details.label || details.predicted}
        />
      </div>
    </div>
  );
};

function areEqual(prevProps, nextProps) {
  return prevProps.details.label === nextProps.details.label;
}

function toPercentage(num) {
  return (100 * Math.round(num * 100)) / 100;
}

export default React.memo(Job, areEqual);
