import React from "react";
import { get_endpoint } from "../utils/utils";

const Reader = ({ handleResults, activeFilter }) => {
  let data = null;

  const ENDPOINT = get_endpoint();

  const query_jobs = async () => {
    let response, request;

    /* Return example: 'uncategorized,good' */
    activeFilter = Object.entries(activeFilter)
      .filter(([k, v]) => v === true)
      .map(([k, v]) => k)
      .join(",");

    request = `${ENDPOINT}/get_jobs?limit=10&offset=0&filter=${activeFilter}`;
    response = await fetch(request);
    data = await response.json();

    handleResults(data);
  };

  return (
    <div className="border-b flex flex-col justify-between items-center pb-1">
      <div className="flex flex-col items-start py-3">
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
