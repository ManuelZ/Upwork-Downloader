import React from "react";

const Button = ({onClick, disabled, buttonRef, text}) => {
  return (
    <button
      onClick={onClick}
      className={
        "bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded " +
        (disabled ? "opacity-50 cursor-not-allowed" : "")
      }
      ref={buttonRef}
    >
      {text}
    </button>
  );
};

export default Button;
