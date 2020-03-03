import React, { useState } from "react";
import "./ClassSelector.css";

const ClassSelector = ({ id, handler }) => {
  const [selectedOption, setSelectedOption] = useState();

  let labelClass = "rounded-lg shadow-md p-6 hover:cursor-pointer";

  // https://blog.bitsrc.io/customise-radio-buttons-without-compromising-accessibility-b03061b5ba93
  return (
    <div className="flex flex-col flex-1 items-center justify-around h-full">
      <div>
        <input
          id={`class1-${id}`}
          type="radio"
          name={`classes-${id}`}
          value="class1"
          checked={selectedOption === "class1"}
          onChange={changeEvent => {
            setSelectedOption("class1");
            handler(changeEvent);
          }}
        />
        <label className={labelClass} htmlFor={`class1-${id}`}>
          <span>Class1</span>
        </label>
      </div>

      <div>
        <input
          id={`class2-${id}`}
          type="radio"
          name={`classes-${id}`}
          value="class2"
          checked={selectedOption === "class2"}
          onChange={changeEvent => {
            setSelectedOption("class2");
            handler(changeEvent);
          }}
        />
        <label className={labelClass} htmlFor={`class2-${id}`}>
          <span>Class2</span>
        </label>
      </div>

      <div>
        <input
          id={`class3-${id}`}
          type="radio"
          name={`classes-${id}`}
          value="class3"
          checked={selectedOption === "class3"}
          onChange={changeEvent => {
            setSelectedOption("class3");
            handler(changeEvent);
          }}
        />
        <label className={labelClass} htmlFor={`class3-${id}`}>
          <span>Class3</span>
        </label>
      </div>
    </div>
  );
};

export default ClassSelector;
