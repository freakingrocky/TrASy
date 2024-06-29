import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import "./Header.scss";
import Logo from "./Logo";
import SidebarToggle from "./SidebarToggle";
import ThemeToggle from "./ThemeToggle";

const Header = ({ theme, toggleTheme, toggleSidebar }) => {
  const [scrolling, setScrolling] = useState(false);

  useEffect(() => {
    let lastScrollTop = 0;
    const handleScroll = () => {
      let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      if (scrollTop > lastScrollTop) {
        setScrolling(true);
      } else {
        setScrolling(false);
      }
      lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <header className={`header ${scrolling ? "hide" : "show"}`}>
      <SidebarToggle toggleSidebar={toggleSidebar} />
      <Logo />
      <nav>
        <Link to="/Data">Data</Link>
        <Link to="/">Strategy</Link>
        <Link to="/">Custom Scripts</Link>
        <Link to="/">Settings</Link>
      </nav>
      <ThemeToggle theme={theme} toggleTheme={toggleTheme} />
    </header>
  );
};

export default Header;
