import React, { useState, useEffect } from "react";

/* Bug here, double-call of fetchData sometimes */

const JobsCount = () => {
  const [count, setCount] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch(`http://localhost:5000/count_jobs`);
      const results = await response.json();

      if (count !== results["msg"]) {
        setCount(results["msg"]);
      }
    };

    fetchData();
  });

  if (count === null) {
    return <div> "Loading..."</div>;
  }
  return <div className="flex justify-end">{`${count} classified jobs`}</div>;
};

export default JobsCount;
