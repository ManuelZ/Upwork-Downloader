import React from "react";

const Reader = ({ handleResults }) => {
  let data = null;

  const query_jobs = async () => {
    let response, results;

    response = await fetch(
      "http://localhost:5000/get_all_jobs?limit=50&offset=0"
    );
    data = await response.json();

    handleResults(data);
  };

  return (
    <div className="border-b flex flex-col justify-between items-start py-3">
      <div className="flex flex-col items-start py-3">
        <label className="font-bold">Data file</label>
        <button
          onClick={query_jobs}
          class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Load saved jobs
        </button>
      </div>
    </div>
  );
};

export default Reader;
