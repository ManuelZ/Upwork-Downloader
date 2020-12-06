import React, { useState, useRef } from "react";
import { get_endpoint, sortByDate } from "../utils/utils";
import Job from "../components/Job";
import { isEmpty, isNull } from "lodash";

const ENDPOINT = get_endpoint();

const Predicter = () => {
  const [predicted, setPredicted] = useState(null);
  const [fetching, setFetching] = useState(false);
  const [retrain, setRetrain] = useState(false);
  const [search, setSearch] = useState(false);
  const [window, setWindow] = useState(1);
  const [toPredict, setToPredict] = useState({
    Good: true,
    Maybe: true,
    Bad: false,
  });

  const buttonRef = useRef(null);

  const getPredictions = async (event) => {
    event.preventDefault();
    setFetching(true);

    if (buttonRef.current) {
      buttonRef.current.setAttribute("disabled", "disabled");
    }

    let response = await fetch(`${ENDPOINT}/predict`, {
      method: "POST",
      body: JSON.stringify({
        retrain: retrain,
        window: window,
        to_predict: toPredict,
        search: search
      }),
      headers: {
        "Content-Type": "application/json",
      },
    });

    let data = await response.json();

    let jobs = {};
    for (const job of data["msg"]) {
      jobs[job.id] = { ...job };
    }

    console.log(data["report"]);
    setPredicted(jobs);
    setFetching(false);
    buttonRef.current.removeAttribute("disabled");
  };

  const handleClassSelection = async (changeEvent) => {
    let jobId = changeEvent.target.id.split("-")[1];
    let selectedClass = changeEvent.target.value;

    setPredicted((previousJobs) => {
      /* Create a deep copy of the state */
      let newJobs = {};
      for (let id of Object.keys(previousJobs)) {
        newJobs[id] = { ...previousJobs[id] };
      }

      /* Update only the job of interest */
      newJobs[jobId].label = selectedClass;

      return newJobs;
    });

    let response = await fetch(
      `${ENDPOINT}/update_job?id=${jobId}&label=${selectedClass}`
    );

    if (!response.ok) {
      // Display error message
    }
  };

  const handleMinusOne = (event) => {
    event.preventDefault();
    let newWindow = window - 1 < 0 ? 0 : window - 1;
    setWindow(newWindow);
  };

  const handlePlusOne = (event) => {
    event.preventDefault();
    setWindow(window + 1);
  };

  const handleRetrainChange = (event) => {
    setRetrain(!retrain);
  };
  const handleSearchChange = (event) => {
    setSearch(!search);
  };

  const handleToPredictChange = (event) => {
    setToPredict({
      ...toPredict,
      [event.target.name]: !toPredict[event.target.name],
    });
  };

  let jobs;
  if (fetching) {
    jobs = <div className="m-5 text-gray-700">Loading predictions...</div>;
  } else if (isNull(predicted)) {
    jobs = <div></div>;
  } else if (isEmpty(predicted)) {
    jobs = <div className="m-5">No predicted jobs to display.</div>;
  } else {
    jobs = Object.keys(predicted)
      .map((jobKey) => ({ id: jobKey, ...predicted[jobKey] }))
      .sort(sortByDate)
      .map((job, index) => (
        <Job
          key={job.id}
          id={job.id}
          details={job}
          handler={handleClassSelection}
        />
      ));
  }

  return (
    <div className="flex flex-col m-1 lg:m-3 p-2 lg:p-4 justify-center text-center items-center">
      <div className="lg:mb-10 sm:mt-0">
        <div className="md:grid md:grid-cols-1 md:gap-6">
          <div className="lg:mt-5 md:mt-0 md:col-span-1">
            <form className="flex flex-row" action="#" method="POST">
              <div className="shadow sm:rounded-md">
                <div className="grid grid-cols-2 md:grid-cols-3 md:grid-rows-1">
                  <div className="px-4 py-5 bg-white sm:p-6">
                    <div className="flex flex-col items-center">
                      <legend className="text-base font-medium text-gray-900">
                        Traininig
                      </legend>
                      <p className="text-sm text-gray-500">Training options</p>
                    </div>
                    <fieldset className="mt-5 pb-4">
                      <div className="flex items-start pb-4">
                        <div className="flex items-center h-5">
                          <input
                            id="retrain"
                            name="retrain"
                            type="checkbox"
                            checked={retrain}
                            onChange={handleRetrainChange}
                            className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                          />
                        </div>
                        <div className="flex flex-col items-start ml-3 text-sm">
                          <label
                            htmlFor="retrain"
                            className="font-medium text-gray-700"
                          >
                            Retrain
                          </label>
                          <p className="text-gray-500 text-left">
                            Retrain the model before prediction
                          </p>
                        </div>
                      </div>
                      <div className="flex items-start pb-4">
                        <div className="flex items-center h-5">
                          <input
                            id="search"
                            name="search"
                            type="checkbox"
                            checked={search}
                            onChange={handleSearchChange}
                            className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                          />
                        </div>
                        <div className="flex flex-col items-start ml-3 text-sm">
                          <label
                            htmlFor="search"
                            className="font-medium text-gray-700"
                          >
                            Search
                          </label>
                          <p className="text-gray-500 text-left">
                            Hyperparameters search
                          </p>
                        </div>
                      </div>
                    </fieldset>
                  </div>
                  <div className="px-4 py-5 bg-white sm:p-6">
                    <div className="flex flex-col items-center">
                      <legend className="text-base font-medium text-gray-900">
                        Look-back window
                      </legend>
                      <p className="text-sm text-gray-500">
                        How many days to look back for jobs
                      </p>
                      <div className="flex flex-row h-10 rounded-lg bg-transparent mt-5">
                        <button
                          onClick={handleMinusOne}
                          className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                        >
                          <span className="sr-only">Previous</span>
                          <svg
                            className="h-5 w-5"
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                            aria-hidden="true"
                          >
                            <path
                              fillRule="evenodd"
                              d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
                              clipRule="evenodd"
                            />
                          </svg>
                        </button>
                        <input
                          type="number"
                          className="no-arrows text-center w-16 text-md bg-gray-300 text-gray-700 font-semibold  hover:text-black focus:text-black "
                          name="custom-input-number"
                          onChange={() => {}}
                          value={window}
                        />

                        <button
                          onClick={handlePlusOne}
                          className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                        >
                          <span className="sr-only">Next</span>
                          <svg
                            className="h-5 w-5"
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                            aria-hidden="true"
                          >
                            <path
                              fillRule="evenodd"
                              d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                              clipRule="evenodd"
                            />
                          </svg>
                        </button>
                      </div>
                    </div>
                  </div>
                  <div className="px-4 py-5 bg-white sm:p-6">
                    <fieldset>
                      <div className="flex flex-col items-center">
                        <legend className="text-base font-medium text-gray-900">
                          Prediction
                        </legend>
                        <p className="text-sm text-gray-500">
                          Which kind of predicted jobs to return
                        </p>
                      </div>
                      <div className="mt-5 space-y-4">
                        <div className="flex items-start">
                          <div className="flex items-center h-5">
                            <input
                              id="predict-good"
                              name="Good"
                              type="checkbox"
                              checked={toPredict["Good"]}
                              onChange={handleToPredictChange}
                              className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                            />
                          </div>
                          <div className="ml-3 text-sm">
                            <label
                              htmlFor="predict-good"
                              className="font-medium text-gray-700"
                            >
                              Good
                            </label>
                          </div>
                        </div>
                        <div className="flex items-start">
                          <div className="flex items-center h-5">
                            <input
                              id="predict-maybe"
                              name="Maybe"
                              type="checkbox"
                              checked={toPredict["Maybe"]}
                              onChange={handleToPredictChange}
                              className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                            />
                          </div>
                          <div className="ml-3 text-sm">
                            <label
                              htmlFor="predict-maybe"
                              className="font-medium text-gray-700"
                            >
                              Maybe
                            </label>
                          </div>
                        </div>
                        <div className="flex items-start">
                          <div className="flex items-center h-5">
                            <input
                              id="predict-bad"
                              name="Bad"
                              type="checkbox"
                              checked={toPredict["Bad"]}
                              onChange={handleToPredictChange}
                              className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                            />
                          </div>
                          <div className="ml-3 text-sm">
                            <label
                              htmlFor="predict-bad"
                              className="font-medium text-gray-700"
                            >
                              Bad
                            </label>
                          </div>
                        </div>
                      </div>
                    </fieldset>
                  </div>
                </div>
                <div className="px-4 py-3 bg-gray-50 text-right sm:px-6">
                  <button
                    type="submit"
                    onClick={getPredictions}
                    className={
                      "inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-bold rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 " +
                      (fetching ? "opacity-50 cursor-not-allowed" : "")
                    }
                    ref={buttonRef}
                  >
                    {"Predict good jobs"}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
      <div className="w-full mt-5">{jobs}</div>
    </div>
  );
};

export default Predicter;
