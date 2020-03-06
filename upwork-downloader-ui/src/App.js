import React, { useState, useCallback } from "react";
import Reader from "./components/Reader";
import { withRouter } from "react-router-dom";
import Job from "./components/Job";
import Saver from "./components/Saver";

function App() {
  const [jobs, setJobs] = useState({});
  const [headers, setHeaders] = useState([]);

  /* Handle the loaded CSV file */
  function handleCSVData(results) {
    let resultsObject = {};

    results.data.forEach(obj => {
      const { id, ...rest } = obj;
      resultsObject[id] = rest;
    });

    setHeaders(results.meta.fields);
    setJobs(resultsObject);
  }

  /* Handle the click on a class label */
  const handleClassSelection = useCallback(changeEvent => {
    let jobId = changeEvent.target.id.split("-")[1];
    let selectedClass = changeEvent.target.value;

    setJobs(previousJobs => {
      /* Create a deep copy of the state */
      let newJobs = {};
      Object.keys(previousJobs).forEach(jobId => {
        newJobs[jobId] = { ...previousJobs[jobId] };
      });

      /* Update only the job of interest */
      newJobs[jobId].class = selectedClass;
      return newJobs;
    });
  }, []);

  const sortByDate = (a, b) => {
    if (a.date_created < b.date_created) {
      return 1;
    }
    if (a.date_created > b.date_created) {
      return -1;
    }
    return 0;
  };

  return (
    <div className="flex flex-col m-5 justify-center container mx-auto text-center p-4">
      <div>Please select your file</div>

      <div className="flex flex-row justify-between w-3/4 container mx-auto">
        <Reader handleResults={handleCSVData} />
        <Saver headers={headers} data={jobs} />
      </div>

      <div className="flex flex-col m-5 justify-center container mx-auto text-center p-4 items-center"></div>
      {Object.keys(jobs)
        .map(jobKey => ({ id: jobKey, ...jobs[jobKey] }))
        .sort(sortByDate)
        .map(
          (job, index) =>
            job.id && (
              <Job
                key={job.id}
                id={job.id}
                details={job}
                handler={handleClassSelection}
              />
            )
        )}
    </div>
  );
}

export default withRouter(App);
