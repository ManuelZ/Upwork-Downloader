import React, { useState, useEffect } from "react";
import { get_endpoint } from "../utils/utils";

/* Bug here, double-call of countJobs sometimes */

const ENDPOINT = get_endpoint();

const JobsCount = ({ count }) => {
  if (count === null) {
    return (
      <div className="flex justify-end mx-2 text-sm pb-2 text-gray-600">
        {" "}
        "Loading..."
      </div>
    );
  }
  return (
    <div className="flex justify-end mx-2 text-sm pb-2 text-gray-600">{`${count} classified jobs`}</div>
  );
};

export default JobsCount;
