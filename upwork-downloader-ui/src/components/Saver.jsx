import React, { useState } from "react";
/* Beware with the window.require, this is an Electron app, not a Web app */
const createCsvWriter = window.require("csv-writer").createObjectCsvWriter;

const Saver = ({ save, headers, data }) => {
  const [saved, setSaved] = useState(false);

  headers = headers.map(h => {
    return { id: h, title: h };
  });

  const csvWriter = createCsvWriter({
    path: "../data/out.csv",
    header: headers
  });

  if (save) {
    csvWriter.writeRecords(data).then(() => {
      setSaved(false);
    });
  }

  return (
    <div>
      <button onClick={() => setSaved(true)}>Save</button>
      <div>{saved ? "Saved!" : ""}</div>
    </div>
  );
};

export default Saver;
