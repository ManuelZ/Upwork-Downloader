import React, { useState, useCallback, useRef, useEffect } from "react";

import Job from "../components/Job";
import Filter from "../components/Filter";
import JobsCount from "../components/JobsCount";
import { sortByDate, get_endpoint } from "../utils/utils";
import Button from "../components/Button";
import Pager from "../components/Pager";

const ENDPOINT = get_endpoint();

const ManualClassifier = () => {
  const [jobs, setJobs] = useState({});
  const [fetching, setFetching] = useState(false);
  const [page, setPage] = useState(1);
  const [limit] = useState(10); // max number of jobs per page
  const [totalJobs, setTotalJobs] = useState({}); // { "good":10, ...}
  const [classFilter, setClassFilter] = useState({
    good: true,
    maybe: false,
    bad: false,
    uncategorized: false,
  });

  const buttonRef = useRef(null);

  function handleData(data) {
    const { jobs, count } = data;
    let jobsById = {};
    for (const job of jobs["data"]) {
      jobsById[job.id] = job;
    }

    setJobs(jobsById);
    setTotalJobs(count);
  }

  let filterClasses = [
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
    /* Get the filter state for the given job label 
       or use the "uncategorized" value as default */
    .filter(jobFilter);

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
      `${ENDPOINT}/update_job?id=${jobId}&label=${selectedClass}`
    );

    if (!response.ok) {
      // Display error message
    }
  }, []);

  const refillDatabase = () => {
    if (buttonRef.current) {
      buttonRef.current.setAttribute("disabled", "disabled");
    }

    setFetching(true);

    fetch(`${ENDPOINT}/download`, { method: "POST" })
      .then((response) => response.json())
      .then((content) => {
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

  /*
  
  Returns:   {
    "msg": {
            "Bad": 1110,
            "Good": 141,
            "Maybe": 240
    }
  }
    
  */

  const queryJobs = useCallback(async () => {
    const countJobs = async () => {
      const response = await fetch(`${ENDPOINT}/count_jobs`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ classFilter: classFilter }),
      });
      const results = await response.json();
      return results["msg"];
    };

    /* Return example: 'uncategorized,good' */
    let activeFilter = Object.entries(classFilter)
      .filter(([k, v]) => v === true)
      .map(([k, v]) => k)
      .join(",");

    let offset = (page - 1) * limit;
    if (offset < 0) {
      offset = 0;
    }

    const request = `${ENDPOINT}/get_jobs?limit=${limit}&offset=${offset}&filter=${activeFilter}`;
    const response = await fetch(request);
    const jobs = await response.json();
    const countedJobs = await countJobs();

    handleData({ jobs: jobs, count: countedJobs });
  }, [classFilter, limit, page]);

  useEffect(() => {
    const fetchJobs = async () => {
      await queryJobs();
    };
    fetchJobs();
  }, [page, queryJobs]);

  return (
    <>
      <JobsCount
        count={Object.keys(totalJobs)
          .map((key) => totalJobs[key])
          .reduce((acc, v) => acc + v, 0)}
      />

      <div className="flex flex-row justify-between px-4 border-b">
        <div className="flex lg:w-1/6 items-center justify-center">
          <div>
            <Button
              onClick={refillDatabase}
              disabled={fetching}
              buttonRef={buttonRef}
              text="Refill database"
            />
          </div>
        </div>
        <div className="flex flex-col lg:w-4/6">
          <Filter classes={filterClasses} onToggleFilter={toggleFilter} />

          <div className="flex flex-col justify-between items-center pb-1">
            <div className="flex flex-col items-start py-3">
              <Button
                onClick={queryJobs}
                disabled={null}
                buttonRef={null}
                text="Load saved jobs"
              />
            </div>
          </div>
        </div>
        <div className="flex lg:w-1/6"></div>
      </div>

      <div className="flex flex-col m-2 lg:m-5 p-0 lg:p-4">{content}</div>

      <Pager
        currentPage={page}
        jobsPerPage={limit}
        totalJobs={Object.keys(totalJobs)
          .map((key) => totalJobs[key])
          .reduce((acc, v) => acc + v, 0)}
        setPage={setPage}
      />
    </>
  );
};

export default ManualClassifier;
