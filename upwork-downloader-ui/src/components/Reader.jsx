import React from "react";
import { readString } from "react-papaparse";

const Reader = ({ handleResults }) => {
  let fileReader;

  const handleFileChosen = file => {
    fileReader = new FileReader();
    fileReader.onloadend = e => {
      const content = fileReader.result;
      var results = readString(content, { header: true });
      console.log(results);
      handleResults(results);
    };

    fileReader.readAsText(file);
  };

  return (
    <div className="border-b flex flex-row justify-between items-center py-3">
      <input
        type="file"
        id="file"
        className=""
        accept=".csv"
        onChange={e => handleFileChosen(e.target.files[0])}
      />
    </div>
  );
};

export default Reader;
