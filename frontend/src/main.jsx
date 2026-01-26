import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.jsx";
import "./styles.css";

const root = createRoot(document.getElementById("root"));
const routerFutureFlags = {
  v7_startTransition: true,
  v7_relativeSplatPath: true
};
root.render(
  <React.StrictMode>
    <BrowserRouter future={routerFutureFlags}>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
