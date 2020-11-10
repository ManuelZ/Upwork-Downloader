import { Routes, Route } from "react-router-dom";
import ManualClassifier from "./containers/ManualClassifier";
import Predicter from "./containers/Predicter";

function App() {
  return (
    <div className="flex flex-col mx-2 my-2 lg:m-5 px-2 lg:p-4 justify-center mx-auto text-center">
      <Routes>
        <Route path="/" element={<ManualClassifier />} />
        <Route path="/predicter" element={<Predicter />} />
      </Routes>
    </div>
  );
}

export default App;
