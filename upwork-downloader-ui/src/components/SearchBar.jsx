import React,{ useState} from "react";

const ENTER_KEY_VAL = 13;

const SearchBar = ({searchCall}) => {
  const [value, setValue] = useState('');

  function onEnter(event) {
    if (event.which === ENTER_KEY_VAL || event.keyCode === ENTER_KEY_VAL) {
      console.log("Pressed enter");
      console.log(event.target.value);
      searchCall(event.target.value);
    }
  }


  return (
  <div className="flex justify-start mx-2 text-sm pb-2 text-gray-600">
    <input
      key="searchbar"
      value={value}
      placeholder={"Search"}
      onChange={(e) => setValue(e.target.value)}
      onKeyPress={onEnter}
    />
  </div>)
};

export default SearchBar;
