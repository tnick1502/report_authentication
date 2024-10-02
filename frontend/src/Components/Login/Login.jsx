import React from "react";

import "./Login.css";
import { useRef } from "react";
import { useContext } from "react";
import Context from "../../context";
import { useEffect } from "react";
import Personal from "../Personal/Personal";

import { login } from "../../Utils/login";

export default function Login() {
  const form = useRef();

  const { logged, setLogged } = useContext(Context);

  useEffect(() => {
    fetch(`${process.env.REACT_APP_SERVER_IP}auth/user/`, {
      method: "GET", // *GET, POST, PUT, DELETE, etc.
      credentials: "include", // include, *same-origin, omit
    }).then((response) => {
      if (!response.ok || response.status !== 200) {
        setLogged(false);
      } else {
        setLogged(true);
      }
    });
  }, []);

  function checkForm(username, password) {
    if (username === "" || password === "") {
      return false;
    } else {
      return true;
    }
  }

  function formSbmt(event) {
    event.preventDefault();
    event.stopPropagation();

    const inputs = document.querySelectorAll("#login-form input");
    inputs.forEach((input) => {
      input.classList.remove("is-valid");
      input.classList.remove("is-invalid");
    });

    if (!checkForm(form.current.username.value, form.current.password.value)) {
      inputs.forEach((input) => {
        input.classList.add("is-invalid");
      });
      return;
    }

    login(setLogged, form.current.username.value, form.current.password.value);
  }

  return (
    <>
      {!logged ? (
        <>
          <h2 className="container__title">Личный кабинет</h2>
          <form
            ref={form}
            className="row form-row"
            id="login-form"
            noValidate
            onSubmit={formSbmt}
          >
            <div className="col-12">
              <label for="username">Имя пользователя:</label>
              <input
                className="form-control"
                id="username"
                placeholder="Введите имя"
                aria-describedby="validationServer"
                required
              />
            </div>
            <div className="col-12">
              <label for="password">Пароль:</label>
              <input
                type="password"
                className="form-control"
                id="password"
                placeholder="Введите пароль"
                aria-describedby="validationServer"
                required
              />
              <div id="validationServer" className="invalid-feedback">
                Не верные имя пользователя или пароль.
              </div>
            </div>
            <div className="col-12">
              <button
                type="submit"
                className="btn btn-success btn-test align-center"
                id="mdgt-btn"
              >
                Войти
              </button>
            </div>
          </form>
        </>
      ) : (
        <Personal />
      )}
    </>
  );
}
