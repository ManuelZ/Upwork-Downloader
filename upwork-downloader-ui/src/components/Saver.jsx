import React, { useState } from "react";
/* Beware with the window.require, this is an Electron app, not a Web app */
const createCsvWriter = window.require("csv-writer").createObjectCsvWriter;

const Saver = ({ headers, data }) => {
  const [save, setSave] = useState(false);

  headers = headers.map(h => {
    return { id: h, title: h };
  });

  const csvWriter = createCsvWriter({
    path: "../data/data-out.csv",
    header: headers
  });

  if (save) {
    console.log("Saving...");
    let data_transformed = Object.keys(data).map(jobKey => ({
      id: jobKey,
      ...data[jobKey]
    }));
    csvWriter.writeRecords(data_transformed).then(() => setSave(false));
  }

  return (
    <div>
      <button onClick={() => setSave(true)}>Save</button>
      <div>{save ? "Saved!" : ""}</div>
    </div>
  );
};

export default Saver;
