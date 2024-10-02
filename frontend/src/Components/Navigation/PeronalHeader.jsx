import "./PersonalHeader.css";

import { NavLink } from "react-router-dom";
import { NavHashLink } from "react-router-hash-link";

import { useContext } from "react";
import Context from "../../context";

import { signOut } from "../../Utils/login";

export default function PersonalHeader() {
  const { setLogged, toggleNav, setToggleNav } = useContext(Context);

  const scrollWithOffset = (el) => {
    console.log(el);
    const elementPosition = el.offsetTop - 30;
    window.scroll({
      top: elementPosition,
      left: 0,
      behavior: "instant",
    });
  };

  function openNav() {
    // const body = document.getElementById('body')
    // body.classList.add('body-hidden')
    setToggleNav(true);
  }

  function closeNav() {
    // const body = document.getElementById('body')
    // body.classList.remove('body-hidden')
    setToggleNav(false);
  }

  function wrapperClick(event) {
    // console.log(event.target, event.currentTarget)
    if (event.target === event.currentTarget) {
      closeNav();
    }
  }

  return (
    <>
      <header className="navbar-mdgt">
        <nav className="container-fluid-mdgt container-mdgt container-fluid-mdgt-personal">
          <NavHashLink
            to="/#"
            scroll={(el) => scrollWithOffset({ offsetTop: 30 })}
            className="navbar-brand"
            onClick={closeNav}
          >
            <img
              className="navbar-brand__icon"
              src="https://s3.timeweb.com/cw78444-3db3e634-248a-495a-8c38-9f7322725c84/georeport/static/images/logo.png"
            />
            {/* <!-- <div className="navbar-brand__line"></div>
			<div className="navbar-brand__title">
				GEOREPORT
				<div className="navbar-brand__title-sub">
					by mdgt
				</div>
			</div> --> */}
          </NavHashLink>

          <div
            id="navbar-collapse-wrapper-personal"
            className={
              toggleNav
                ? "navbar-collapse-wrapper-personal navbar-collapse-wrapper-show"
                : "navbar-collapse-wrapper-personal"
            }
            onClick={wrapperClick}
          >
            <div
              className={
                toggleNav
                  ? "navbar-collapse-personal navbar-collapse-show"
                  : "navbar-collapse-personal"
              }
              id="navbar-collapse-personal"
            >
              <ul className="navbar-nav navbar-nav-personal">
                <li className="nav-item-personal">
                  <NavHashLink
                    className="nav-link-personal"
                    to="/#"
                    scroll={(el) => scrollWithOffset({ offsetTop: 30 })}
                    onClick={closeNav}
                  >
                    Главная
                  </NavHashLink>
                </li>
                <li className="nav-item-personal">
                  <button
                    className="nav-link-personal"
                    id="btn-out"
                    onClick={() => {
                      signOut(setLogged);
                      closeNav();
                    }}
                  >
                    Выйти
                  </button>
                </li>
              </ul>

              <div
                className="nav__close-personal"
                id="nav-close-personal"
                onClick={closeNav}
              >
                <i className="ri-close-line"></i>
              </div>
            </div>
          </div>

          <div
            className="nav__toggle-personal"
            id="nav-toggle-personal"
            onClick={openNav}
          >
            <i className="ri-menu-line"></i>
          </div>
        </nav>
      </header>
    </>
  );
}
