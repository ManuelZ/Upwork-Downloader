import React, { useState, useEffect } from "react";
import { get_endpoint } from "../utils/utils";

/* Bug here, double-call of fetchData sometimes */

const JobsCount = () => {
  const [count, setCount] = useState(null);

  const ENDPOINT = get_endpoint();

  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch(`${ENDPOINT}/count_jobs`);
      const results = await response.json();

      if (count !== results["msg"]) {
        setCount(results["msg"]);
      }
    };

    fetchData();
  });

  if (count === null) {
    return <div className="flex justify-end mx-2 text-sm pb-2 text-gray-600"> "Loading..."</div>;
  }
  return <div className="flex justify-end mx-2 text-sm pb-2 text-gray-600">{`${count} classified jobs`}</div>;
};

export default JobsCount;
