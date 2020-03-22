import React, { useState, useCallback } from "react";
import Reader from "./components/Reader";
import { withRouter } from "react-router-dom";
import Job from "./components/Job";
import Saver from "./components/Saver";
import Filter from "./components/Filter";

function App() {
  const [jobs, setJobs] = useState({});
  const [headers, setHeaders] = useState([]);
  const [classFilter, setClassFilter] = useState({
    good: true,
    maybe: true,
    bad: true,
    uncategorized: true
  });

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

  let classes = [
    {
      id: "good",
      label: "Good",
      active: classFilter.good
    },
    {
      id: "maybe",
      label: "Maybe",
      active: classFilter.maybe
    },
    {
      id: "bad",
      label: "Bad",
      active: classFilter.bad
    },
    {
      id: "uncategorized",
      label: "Uncategorized",
      active: classFilter.uncategorized
    }
  ];

  const toggleFilter = filterId => {
    setClassFilter(prevFilter => {
      let newFilter = { ...prevFilter };
      newFilter[filterId] = !prevFilter[filterId];
      return newFilter;
    });
  };

  const jobFilter = job => {
    if (!job["id"]) {
      return false;
    }
    let jobClass = job["class"];
    if (jobClass) {
      jobClass = jobClass.toLowerCase();
    }
    let show = classFilter[jobClass];
    if (jobClass === "") {
      show = classFilter["uncategorized"];
    }
    return show;
  };

  const filteredJobs = Object.keys(jobs)
    .map(jobKey => ({ id: jobKey, ...jobs[jobKey] }))
    /* Get the filter state for the given job class or use the "uncategorized" value as default */
    .filter(jobFilter);

  console.log(filteredJobs);

  return (
    <div className="flex flex-col m-5 justify-center container mx-auto text-center p-4">
      <div>Please select your file</div>
      <div className="flex flex-row justify-between w-3/4 container mx-auto">
        <Reader handleResults={handleCSVData} />
        <Saver headers={headers} data={jobs} />
      </div>
      <Filter classes={classes} onToggleFilter={toggleFilter} />

      <div className="flex flex-col m-5 justify-center container mx-auto text-center p-4 items-center">
        {filteredJobs
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
    </div>
  );
}

export default withRouter(App);
