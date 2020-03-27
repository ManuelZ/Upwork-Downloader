import React from "react";
import "./ClassSelector.css";

const ClassSelector = ({ id, clickHandler, selectedOption }) => {
  let labelClass =
    "rounded-lg shadow-md hover:cursor-pointer py-4 font-semibold ";
  let onClass = "bg-teal-400 ";
  let offClass = "";

  let class1Value = "Good";
  let class2Value = "Maybe";
  let class3Value = "Bad";

  // https://blog.bitsrc.io/customise-radio-buttons-without-compromising-accessibility-b03061b5ba93
  return (
    <div className="flex flex-col w-1/6 items-center justify-around">
      <div>
        <input
          id={`class1-${id}`}
          type="radio"
          name={`classes-${id}`}
          value={class1Value}
          checked={selectedOption === class1Value}
          onChange={changeEvent => {
            clickHandler(changeEvent);
          }}
        />
        <label
          className={
            labelClass +
            (selectedOption === class1Value ? onClass : offClass) +
            "px-5"
          }
          htmlFor={`class1-${id}`}
        >
          <span>{class1Value}</span>
        </label>
      </div>

      <div>
        <input
          id={`class2-${id}`}
          type="radio"
          name={`classes-${id}`}
          value={class2Value}
          checked={selectedOption === class2Value}
          onChange={changeEvent => {
            clickHandler(changeEvent);
          }}
        />
        <label
          className={
            labelClass +
            (selectedOption === class2Value ? onClass : offClass) +
            "px-4"
          }
          htmlFor={`class2-${id}`}
        >
          <span>{class2Value}</span>
        </label>
      </div>

      <div>
        <input
          id={`class3-${id}`}
          type="radio"
          name={`classes-${id}`}
          value={class3Value}
          checked={selectedOption === class3Value}
          onChange={changeEvent => {
            clickHandler(changeEvent);
          }}
        />
        <label
          className={
            labelClass +
            (selectedOption === class3Value ? onClass : offClass) +
            "px-6"
          }
          htmlFor={`class3-${id}`}
        >
          <span>{class3Value}</span>
        </label>
      </div>
    </div>
  );
};

export default ClassSelector;
