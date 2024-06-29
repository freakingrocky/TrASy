import React from "react";
import "./SidebarToggle.scss";

const SidebarToggle = ({ toggleSidebar }) => {
  return (
    <button className="sidebar-toggle" onClick={toggleSidebar}>
      ☰
    </button>
  );
};

export default SidebarToggle;
