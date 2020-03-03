import React, { useState } from "react";

const ClassSelector = handler => {
  const [selectedOption, setSelectedOption] = useState("");

  return (
    <div>
      <div>
        <label>
          <input
            type="radio"
            name="react-tips"
            value="option1"
            checked={setSelectedOption("option1")}
            onChange={handler}
          />
          Option 1
        </label>
      </div>

      <div>
        <label>
          <input
            type="radio"
            name="react-tips"
            value="option2"
            checked={setSelectedOption("option2")}
            onChange={handler}
          />
          Option 2
        </label>
      </div>

      <div>
        <label>
          <input
            type="radio"
            name="react-tips"
            value="option3"
            checked={setSelectedOption("option3")}
            onChange={handler}
          />
          Option 3
        </label>
      </div>

      <div>
        <button>Save</button>
      </div>
    </div>
  );
};

export default ClassSelector;
