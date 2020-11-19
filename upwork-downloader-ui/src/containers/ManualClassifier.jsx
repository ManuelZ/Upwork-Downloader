import React, { useState, useCallback, useRef } from "react";
import Reader from "../components/Reader";
import Job from "../components/Job";
import Filter from "../components/Filter";
import JobsCount from "../components/JobsCount";
import { sortByDate, get_endpoint } from "../utils/utils";
import Button from "../components/Button";

const ManualClassifier = () => {
  const [jobs, setJobs] = useState({});
  const [fetching, setFetching] = useState(false);
  const [classFilter, setClassFilter] = useState({
    good: true,
    maybe: true,
    bad: true,
    uncategorized: true,
  });

  const buttonRef = useRef(null);

  const ENDPOINT = get_endpoint();

  /* Handle the loaded CSV file */
  function handleData(data) {
    let jobs = {};
    for (const job of data["data"]) {
      jobs[job.id] = { ...job };
    }

    setJobs(jobs);
  }

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

  /*
  Explanation of useCallback:
  handleClassSelection variable will have always the same object of the 
  callback function between renderings of App. 
  Source: https://dmitripavlutin.com/dont-overuse-react-usecallback/
  */
  const handleClassSelection = useCallback(
    async (changeEvent) => {
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
        `${ENDPOINT}/update_job?id=${jobId}&label=${selectedClass}`
      );

      if (!response.ok) {
        // Display error message
      }
    },
    [ENDPOINT]
  ); // I don't really expect ENDPOINT to change, idk why I need this here just so to avoid a warning

  const refillDatabase = () => {
    if (buttonRef.current) {
      buttonRef.current.setAttribute("disabled", "disabled");
    }

    setFetching(true);

    fetch(`${ENDPOINT}/download`, { method: "POST" })
      .then((response) => response.json())
      .then((content) => {
        console.log("Done fetching new jobs");
        setFetching(false);
        buttonRef.current.removeAttribute("disabled");
      });
  };

  let content;
  if (fetching) {
    content = <div className="m-5 text-gray-700">Fetching new jobs...</div>;
  }
  content = filteredJobs
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
    );

  return (
    <>
      <JobsCount />
      <div className="flex flex-row justify-between px-4 container mx-auto">
        <div className="flex w-1/6 items-center justify-center">
          <div>
            <Button
              onClick={refillDatabase}
              disabled={fetching}
              buttonRef={buttonRef}
              text="Refill database"
            />
          </div>
        </div>
        <div className="flex flex-col w-4/6">
          <Filter classes={classes} onToggleFilter={toggleFilter} />
          <Reader handleResults={handleData} activeFilter={classFilter} />
        </div>
        <div className="flex w-1/6"></div>
      </div>

      <div className="flex flex-col m-2 lg:m-5 p-0 lg:p-4 justify-center mx-auto text-center items-center">
        {content}
      </div>
    </>
  );
};

export default ManualClassifier;
