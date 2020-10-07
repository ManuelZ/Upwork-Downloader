import React, { useState, useCallback } from "react";
import Reader from "./components/Reader";
import { withRouter } from "react-router-dom";
import Job from "./components/Job";
import Filter from "./components/Filter";

function App() {
  const [jobs, setJobs] = useState({});
  const [classFilter, setClassFilter] = useState({
    good: true,
    maybe: true,
    bad: true,
    uncategorized: true,
  });

  /* Handle the loaded CSV file */
  function handleCSVData(data) {
    let jobs = {};
    for (const job of data["data"]) {
      jobs[job.id] = { ...job };
    }

    setJobs(jobs);
  }

  /*
  Explanation of useCallback:
  handleClassSelection variable will have always the same object of the 
  callback function between renderings of App. 
  Source: https://dmitripavlutin.com/dont-overuse-react-usecallback/
  */
  const handleClassSelection = useCallback(async (changeEvent) => {
    let jobId = changeEvent.target.id.split("-")[1];
    let selectedClass = changeEvent.target.value;

    setJobs((previousJobs) => {
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
      `http://localhost:5000/update_job?id=${jobId}&label=${selectedClass}`
    );

    if (!response.ok) {
      // Display error message
    }
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
      active: classFilter.good,
    },
    {
      id: "maybe",
      label: "Maybe",
      active: classFilter.maybe,
    },
    {
      id: "bad",
      label: "Bad",
      active: classFilter.bad,
    },
    {
      id: "uncategorized",
      label: "Uncategorized",
      active: classFilter.uncategorized,
    },
  ];

  const toggleFilter = (filterId) => {
    setClassFilter((prevFilter) => {
      let newFilter = { ...prevFilter };
      newFilter[filterId] = !prevFilter[filterId];
      return newFilter;
    });
  };

  const jobFilter = (job) => {
    if (!job["id"]) {
      return false;
    }
    let jobLabel = job["label"];
    if (jobLabel) {
      jobLabel = jobLabel.toLowerCase();
    }
    let show = classFilter[jobLabel];

    if (jobLabel === "") {
      show = classFilter["uncategorized"];
    }
    return show;
  };

  const filteredJobs = Object.keys(jobs)
    .map((jobKey) => ({ id: jobKey, ...jobs[jobKey] }))
    /* Get the filter state for the given job label or use the "uncategorized" value as default */
    .filter(jobFilter);

  return (
    <div className="flex flex-col m-5 justify-center container mx-auto text-center p-4">
      <div className="flex flex-row justify-between w-3/4 container mx-auto">
        <Reader handleResults={handleCSVData} />
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
