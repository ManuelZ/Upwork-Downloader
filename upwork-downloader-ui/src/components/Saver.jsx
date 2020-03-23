import React, { useState } from "react";
/* Beware with the window.require, this is an Electron app, not a Web app */
const createCsvWriter = window.require("csv-writer").createObjectCsvWriter;

const Saver = ({ data }) => {
  const [save, setSave] = useState(false);

  const csvWriter = createCsvWriter({
    path: "../data/labels.csv",
    header: [
      { id: "id", title: "id" },
      { id: "label", title: "label" }
    ]
  });

  if (save) {
    let labels = Object.keys(data)
      .filter(id => Boolean(data[id]["label"]))
      .map(id => ({
        id: id,
        label: data[id]["label"]
      }));
    csvWriter.writeRecords(labels).then(() => setSave(false));
  }

  return (
    <div className="py-3 flex items-center">
      <button
        className="px-4 py-2 bg-teal-500 hover:bg-teal-700 text-white font-bold rounded"
        onClick={() => setSave(true)}
      >
        Save
      </button>
      <div>{save ? "Saved!" : ""}</div>
    </div>
  );
};

export default Saver;
