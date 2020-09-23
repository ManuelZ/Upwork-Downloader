import React from "react";
import { readString } from "react-papaparse";

const Reader = ({ handleResults }) => {
  let data = null;
  let labels = null;

  const handleFileChosen = (file) => {
    const reader = new FileReader();

    reader.onloadend = (e) => {
      let results = readString(reader.result, { header: true });
      if (file.name === "labels.csv") {
        labels = results;
      } else {
        data = results;
      }

      if (data && labels) {
        handleResults(data, labels);
      }
    };

    try {
      reader.readAsText(file);
    } catch (error) {
      if (error instanceof TypeError) {
        console.log("Bad file");
      }
    }
  };

  return (
    <div className="border-b flex flex-col justify-between items-start py-3">
      <div className="flex flex-col items-start py-3">
        <label className="font-bold">Data file</label>
        <input
          type="file"
          id="file"
          className=""
          accept=".csv"
          onChange={(e) => handleFileChosen(e.target.files[0])}
        />
      </div>
      <div className="flex flex-col items-start py-3">
        <label className="font-bold">Labels file</label>
        <input
          type="file"
          id="file"
          className=""
          accept=".csv"
          onChange={(e) => handleFileChosen(e.target.files[0])}
        />
      </div>
    </div>
  );
};

export default Reader;
