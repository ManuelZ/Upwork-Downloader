import React, { useState, useRef } from "react";
import { get_endpoint, sortByDate } from "../utils/utils";
import Job from "../components/Job";
import Button from "../components/Button";
import { isEmpty, isNull } from "lodash";

const Predicter = () => {
  const [predicted, setPredicted] = useState(null);
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

  let jobs;
  if (fetching) {
    jobs = <div className="m-5 text-gray-700">Loading predictions...</div>;
  } else if (isNull(predicted)) {
    jobs = <div></div>;
  } else if (isEmpty(predicted)) {
    jobs = <div className="m-5">No jobs to predict</div>;
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
        <Button
          onClick={getPredictions}
          disabled={fetching}
          buttonRef={buttonRef}
          text="Predict good jobs"
        />
        {jobs}
      </div>
    </>
  );
};

export default Predicter;
