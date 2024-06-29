import React from "react";
import { Link } from "react-router-dom";
import Logo from "./Logo";
import "./Sidebar.scss";

const Sidebar = ({ isOpen, toggleSidebar }) => {
  return (
    <div className={`sidebar ${isOpen ? "active" : ""}`}>
      <Logo />
      <nav>
        <Link to="/" onClick={toggleSidebar}>
          Data
        </Link>
        <Link to="/Data" onClick={toggleSidebar}>
          Strategy
        </Link>
        <Link to="/" onClick={toggleSidebar}>
          Custom Scripts
        </Link>
        <Link to="/" onClick={toggleSidebar}>
          Settings
        </Link>
      </nav>
    </div>
  );
};

export default Sidebar;
