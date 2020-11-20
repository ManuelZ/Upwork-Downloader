import React, { useState } from "react";
import ManualClassifier from "../containers/ManualClassifier";
import Predicter from "../containers/Predicter";
import { Routes, Route, Link, useLocation } from "react-router-dom";

const Tabs = (props) => {
  const { pathname } = useLocation();

  const activeTabClass =
    "bg-white inline-block border-l border-t border-r rounded-t py-2 px-4 text-blue-700 font-semibold";
  const tabClass =
    "bg-white inline-block py-2 px-4 text-blue-500 hover:text-blue-800 font-semibold";

  return (
    <>
      {/* Tabs links */}
      <div className="flex flex-row mx-2 my-2 lg:mt-5 px-2 lg:pt-4 justify-start mx-auto text-center border-b">
        <div className={pathname === "/classifier" ? "-mb-px mr-1" : "mr-1"}>
          <Link
            to="/classifier"
            className={pathname === "/classifier" ? activeTabClass : tabClass}
          >
            Manual Classifier
          </Link>
        </div>
        <div className={pathname === "/predicter" ? "-mb-px mr-1" : "mr-1"}>
          <Link
            to="/predicter"
            className={pathname === "/predicter" ? activeTabClass : tabClass}
          >
            Predicter
          </Link>
        </div>
      </div>
      {/* Tabs contents */}
      <div className="">
        <Routes>
          <Route path="/classifier" element={<ManualClassifier />} />
          <Route path="/predicter" element={<Predicter />} />
        </Routes>
      </div>
    </>
  );
};

export default Tabs;
