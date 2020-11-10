import React, { useState, useRef } from "react";
import { get_endpoint, sortByDate } from "../utils/utils";
import Job from "../components/Job";

const Predicter = () => {
  const [predicted, setPredicted] = useState({});
  const [fetching, setFetching] = useState(false);

  const buttonRef = useRef(null);

  const ENDPOINT = get_endpoint();

  const getPredictions = () => {
    if (buttonRef.current) {
      buttonRef.current.setAttribute("disabled", "disabled");
    }

    setFetching(true);

    fetch(`${ENDPOINT}/predict`, { method: "POST" })
      .then((response) => response.json())
      .then((data) => {
        let jobs = {};
        for (const job of data["msg"]) {
          jobs[job.id] = { ...job };
        }

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

  return (
    <>
      <div className="flex flex-col m-5 justify-center container mx-auto text-center p-4 items-center">
        PREDICTER
        <button
          ref={buttonRef}
          onClick={getPredictions}
          className={
            "bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded " +
            (fetching ? "opacity-50 cursor-not-allowed" : "")
          }
        >
          Predict good jobs
        </button>
        {Object.keys(predicted)
          .map((jobKey) => ({ id: jobKey, ...predicted[jobKey] }))
          .sort(sortByDate)
          .map((job, index) => (
            <Job
              key={job.id}
              id={job.id}
              details={job}
              handler={handleClassSelection}
            />
          ))}
      </div>
    </>
  );
};

export default Predicter;
