import React from "react";
import Home from "./pages/home";
import { useSelector } from "react-redux";
import { DASHBOARD_PAGE, HOME_PAGE } from "./lib/actionTypes";
import Dashboard from "./pages/dashboard";

function App() {
  const page = useSelector((state: any) => state.page.currentPage);

  return (
    <div className="relative h-screen w-screen overflow-hidden">
      <Home />
      <Dashboard />
    </div>
  );
}

export default App;
