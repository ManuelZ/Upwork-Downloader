import React, { useState, useRef } from "react";
import { get_endpoint, sortByDate } from "../utils/utils";
import Job from "../components/Job";
import { isEmpty, isNull } from "lodash";

const Predicter = () => {
  const [predicted, setPredicted] = useState(null);
  const [fetching, setFetching] = useState(false);
  const [body, setBody] = useState({
    retrain: true,
    window: 2,
  });

  const buttonRef = useRef(null);

  const ENDPOINT = get_endpoint();

  const getPredictions = (event) => {
    event.preventDefault();

    const { retrain, window } = body;

    if (buttonRef.current) {
      buttonRef.current.setAttribute("disabled", "disabled");
    }

    setFetching(true);

    fetch(`${ENDPOINT}/predict`, {
      method: "POST",
      body: JSON.stringify({ "retrain": retrain, "window": window }),
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        let jobs = {};
        for (const job of data["msg"]) {
          jobs[job.id] = { ...job };
        }

        console.log(data["report"]);

        setPredicted(jobs);
        setFetching(false);
        buttonRef.current.removeAttribute("disabled");
      });
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

    let newWindow = body.window - 1 < 0 ? 0 : body.window - 1;

    setBody({
      ...body,
      window: newWindow,
    });
  };

  const handlePlusOne = (event) => {
    event.preventDefault();

    setBody({
      ...body,
      window: body.window + 1,
    });
  };

  const handleInputChange = (event) => {
    setBody({
      ...body,
      [event.target.name]: event.target.value,
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
    <>
      <div className="flex flex-col m-5 justify-center container mx-auto text-center p-4 items-center">
        <div className="my-10 sm:mt-0">
          <div className="md:grid md:grid-cols-1 md:gap-6">
            <div className="mt-5 md:mt-0 md:col-span-1">
              <form className="flex flex-row" action="#" method="POST">
                <div className="shadow sm:rounded-md">
                  <div className="flex flex-row">
                    <div className="px-4 py-5 bg-white sm:p-6">
                      <fieldset>
                        <div>
                          <legend className="text-base font-medium text-gray-900">
                            Retrain
                          </legend>
                          <p className="text-sm text-gray-500">
                            Whether to retrain or not the model before
                            predicting.
                          </p>
                        </div>
                        <div className="mt-4 space-y-4">
                          <div className="flex items-center">
                            <input
                              id="retrain_true"
                              name="retrain"
                              type="radio"
                              className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300"
                              value={true}
                              onChange={handleInputChange}
                            />
                            <label
                              htmlFor="retrain_true"
                              className="ml-3 block text-sm font-medium text-gray-700"
                            >
                              True
                            </label>
                          </div>
                          <div className="flex items-center">
                            <input
                              defaultChecked
                              id="retrain_false"
                              name="retrain"
                              type="radio"
                              className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300"
                              value={false}
                              onChange={handleInputChange}
                            />
                            <label
                              htmlFor="retrain_false"
                              className="ml-3 block text-sm font-medium text-gray-700"
                            >
                              False
                            </label>
                          </div>
                        </div>
                      </fieldset>
                    </div>
                    <div className="px-4 py-5 bg-white sm:p-6">
                      <div className="flex flex-col items-center h-10">
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
                            value={body.window}
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
                  </div>
                  <div className="px-4 py-3 bg-gray-50 text-right sm:px-6">
                    <button
                      type="submit"
                      onClick={getPredictions}
                      className={
                        "inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 " +
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
        <div>
        {jobs}
        </div>
      </div>
    </>
  );
};

export default Predicter;
