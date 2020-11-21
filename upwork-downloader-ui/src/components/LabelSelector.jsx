import React from "react";

const LabelSelector = ({ id, clickHandler, selectedOption }) => {
  let labelClass =
    "rounded-lg shadow-md hover:cursor-pointer py-4 font-semibold ";
  let onClass = "bg-green-400 ";
  let offClass = "";

  let class1Value = "Good";
  let class2Value = "Maybe";
  let class3Value = "Bad";

  // https://blog.bitsrc.io/customise-radio-buttons-without-compromising-accessibility-b03061b5ba93
  return (
    <div className="flex flex-row lg:flex-col py-3 lg:py-0 lg:w-1/6 items-left justify-between lg:justify-around">
      <div>
        <input
          id={`class1-${id}`}
          type="radio"
          name={`classes-${id}`}
          value={class1Value}
          defaultChecked={selectedOption === class1Value}
          onClick={changeEvent => {
            clickHandler(changeEvent);
          }}
          className="opacity-0 absolute"
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
          defaultChecked={selectedOption === class2Value}
          onClick={changeEvent => {
            clickHandler(changeEvent);
          }}
          className="opacity-0 absolute"
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
          defaultChecked={selectedOption === class3Value}
          onClick={changeEvent => {
            clickHandler(changeEvent);
          }}
          className="opacity-0 absolute"
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

export default LabelSelector;
