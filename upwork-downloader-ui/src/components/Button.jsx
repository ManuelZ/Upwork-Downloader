import React from "react";

const Button = ({onClick, disabled, buttonRef, text}) => {
  return (
    <button
      onClick={onClick}
      className={
        "inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-bold rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500  " +
        (disabled ? "opacity-50 cursor-not-allowed" : "")
      }
      ref={buttonRef}
    >
      {text}
    </button>
  );
};

export default Button;
