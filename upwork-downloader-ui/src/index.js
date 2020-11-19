import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import App from "./App";
import "./index.css";
import "./css/tailwind.css";

const routes = (
  <BrowserRouter>
    <Routes>
      <Route path="/*" element={<App/>} />
    </Routes>
  </BrowserRouter>
);

ReactDOM.render(routes, document.getElementById("root"));