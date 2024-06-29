import React, { useEffect, useState } from "react";
import { Route, Routes } from "react-router-dom";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import Data from "./pages/Data";
import Home from "./pages/Home";
import { getSystemTheme } from "./utils/getSystemTheme";

const App = () => {
  const [theme, setTheme] = useState(getSystemTheme());
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  useEffect(() => {
    document.body.className = theme;
  }, [theme]);

  const toggleTheme = () => {
    setTheme(theme === "light" ? "dark" : "light");
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <>
      <Header
        theme={theme}
        toggleTheme={toggleTheme}
        toggleSidebar={toggleSidebar}
      />
      <Sidebar isOpen={isSidebarOpen} toggleSidebar={toggleSidebar} />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/data" element={<Data />} />
      </Routes>
    </>
  );
};

export default App;
