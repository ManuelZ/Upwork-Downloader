import React from "react";

const LabelSelector = ({ id, clickHandler, selectedOption }) => {
  let labelClass =
    "rounded-lg shadow-md hover:cursor-pointer py-3 font-semibold w-26 text-center ";
  let onClass = "bg-green-400 ";
  let offClass = "";

  let class1Value = "Good";
  let class2Value = "Maybe";
  let class3Value = "Bad";
  let class4Value = "Irrelevant";

  // https://blog.bitsrc.io/customise-radio-buttons-without-compromising-accessibility-b03061b5ba93
  return (
    <div className="flex flex-row lg:flex-col py-3 lg:py-0 lg:w-1/6 items-center justify-between lg:justify-around">
      <>
        <input
          id={`class1-${id}`}
          type="radio"
          name={`classes-${id}`}
          value={class1Value}
          defaultChecked={selectedOption === class1Value}
          onClick={(changeEvent) => {
            clickHandler(changeEvent);
          }}
          className="opacity-0 absolute"
        />
        <label
          className={
            labelClass +
            (selectedOption === class1Value ? onClass : offClass)
          }
          htmlFor={`class1-${id}`}
        >
          <span>{class1Value}</span>
        </label>
      </>

      <>
        <input
          id={`class2-${id}`}
          type="radio"
          name={`classes-${id}`}
          value={class2Value}
          defaultChecked={selectedOption === class2Value}
          onClick={(changeEvent) => {
            clickHandler(changeEvent);
          }}
          className="opacity-0 absolute"
        />
        <label
          className={
            labelClass +
            (selectedOption === class2Value ? onClass : offClass)
          }
          htmlFor={`class2-${id}`}
        >
          <span>{class2Value}</span>
        </label>
      </>

      <>
        <input
          id={`class3-${id}`}
          type="radio"
          name={`classes-${id}`}
          value={class3Value}
          defaultChecked={selectedOption === class3Value}
          onClick={(changeEvent) => {
            clickHandler(changeEvent);
          }}
          className="opacity-0 absolute"
        />
        <label
          className={
            labelClass +
            (selectedOption === class3Value ? onClass : offClass)
          }
          htmlFor={`class3-${id}`}
        >
          <span>{class3Value}</span>
        </label>
      </>

      <>
        <input
          id={`class4-${id}`}
          type="radio"
          name={`classes-${id}`}
          value={class4Value}
          defaultChecked={selectedOption === class4Value}
          onClick={(changeEvent) => {
            clickHandler(changeEvent);
          }}
          className="opacity-0 absolute"
        />
        <label
          className={
            labelClass +
            (selectedOption === class4Value ? onClass : offClass)
          }
          htmlFor={`class4-${id}`}
        >
          <span>{class4Value}</span>
        </label>
      </>
    </div>
  );
};

export default LabelSelector;
