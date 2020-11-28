import React from "react";

const ScoreDisplay = ({ Good, Maybe, Bad }) => {
  const best = Math.max(Good, Maybe, Bad);
  return (
    <div className="hidden lg:flex lg:flex-col items-center py-2 pr-8 lg:w-1/6">
      <div className="shadow w-full bg-grey-400">
        <div
          className={
            "text-xs leading-none py-1 text-center text-white " +
            (Good === best
              ? "bg-green-500 border-gray-600 font-medium"
              : "bg-green-200")
          }
          style={{ width: Good + "%" }}
        >
          {Good + "%"}
        </div>
      </div>

      <div className="shadow w-full bg-grey-400 mt-2">
        <div
          className={
            "text-xs leading-none py-1 text-center text-white " +
            (Maybe === best
              ? "bg-yellow-500 border-gray-600 font-medium"
              : "bg-yellow-200")
          }
          style={{ width: Maybe + "%" }}
        >
          {Maybe + "%"}
        </div>
      </div>

      <div className="shadow w-full bg-grey-400 mt-2">
        <div
          className={
            "text-xs leading-none py-1 text-center text-white " +
            (Bad === best
              ? "bg-red-500 border-gray-600 font-medium"
              : "bg-red-200")
          }
          style={{ width: Bad + "%" }}
        >
          {Bad + "%"}
        </div>
      </div>
      <span className="text-xs font-light text-gray-500">Prediction score</span>
    </div>
  );
};
export default ScoreDisplay;
