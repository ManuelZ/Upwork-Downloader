import React from "react";

const Reader = ({ handleResults, activeFilter }) => {
  let data = null;

  const capitalize = (s) => s.charAt(0).toUpperCase() + s.slice(1);

  const query_jobs = async () => {
    let response, request;

    /* Return example: 'uncategorized,good' */
    activeFilter = Object.entries(activeFilter)
      .filter(([k, v]) => v === true)
      .map(([k, v]) => k)
      .join(",");

    request = `http://localhost:5000/get_jobs?limit=50&offset=0&filter=${activeFilter}`;
    response = await fetch(request);
    data = await response.json();

    handleResults(data);
  };

  return (
    <div className="border-b flex flex-col justify-between items-start py-3">
      <div className="flex flex-col items-start py-3">
        <label className="font-bold">Load data</label>
        <button
          onClick={query_jobs}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Load saved jobs
        </button>
      </div>
    </div>
  );
};

export default Reader;
