import React from "react";
import { Link } from "react-router-dom";
import "./Logo.scss";

const Logo = () => {
  return (
    <div className="logo">
      <Link className="reset" to="/">
        <div className="logo-main">TrASy</div>
        <div className="logo-sub">Trading Automation System</div>
      </Link>
    </div>
  );
};

export default Logo;
