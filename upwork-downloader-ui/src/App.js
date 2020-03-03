import React, { useState, useEffect } from "react";
import Reader from "./components/Reader";
import { withRouter } from "react-router-dom";
import Job from "./components/Job";
import Saver from "./components/Saver";

function App() {
  const [jobs, setJobs] = useState([]);
  const [headers, setHeaders] = useState([]);
  const [save, setSave] = useState(false);

  function handleResults(results) {
    setJobs(results.data);
    setHeaders(results.meta.fields);
    setSave(true);
  }

  const handleOptionChange = changeEvent => {
    console.log("changeEvent.target: ", changeEvent.target);
    //changeEvent.target.value;
  };

  //useEffect(() => {}, [jobs]);

  return (
    <div className="flex flex-col m-5 justify-center container mx-auto text-center p-4">
      <div>Please select your file</div>
      <Reader handleResults={handleResults} />
      <Saver save={save} headers={headers} data={jobs} />
      <div className="flex flex-col m-5 justify-center container mx-auto text-center p-4 items-center">
        {jobs.map((job, index) => (
          <Job key={job.id} details={job} handler={handleOptionChange} />
        ))}
      </div>
    </div>
  );
}

export default withRouter(App);
