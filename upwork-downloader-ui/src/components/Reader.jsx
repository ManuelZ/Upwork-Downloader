import React from "react";
import { get_endpoint } from "../utils/utils";
import Button from "../components/Button";

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
    <div className="flex flex-col justify-between items-center pb-1">
      <div className="flex flex-col items-start py-3">

      <Button
              onClick={query_jobs}
              disabled={null}
              buttonRef={null}
              text="Load saved jobs"
            />
        
      </div>
    </div>
  );
};

export default Reader;
