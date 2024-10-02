import React, { useEffect } from "react";
import { Toast } from "bootstrap";

import "./Footer.css";

import mdgt from "./mdgt.png";

export default function Footer() {
  // load
  useEffect(() => {
    const toastItem = document.getElementById("toast");
    const toast = new Toast(toastItem);

    // console.log(toast)

    const toastBtnAccept = document.getElementById("btnAccept");
    toastBtnAccept.addEventListener("click", (event) => {
      setCookie("allowCookies", "1", 7);
      toast.hide();
    });

    function setCookie(name, value, days) {
      var expires = "";
      if (days) {
        var date = new Date();
        date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
        expires = "; expires=" + date.toUTCString();
      }
      document.cookie = name + "=" + (value || "") + expires + "; path=/";
    }
    function getCookie(name) {
      var nameEQ = name + "=";
      var ca = document.cookie.split(";");
      for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) === " ") c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0)
          return c.substring(nameEQ.length, c.length);
      }
      return null;
    }

    // function eraseCookie(name) {
    //   document.cookie =
    //     name + "=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;";
    // }

    function cookieConsent() {
      if (!getCookie("allowCookies")) {
        toast.show();
      }
    }

    cookieConsent();
  }, []);

  return (
    <>
      <footer className="footer__container">
        <div className="container_contact" id="contact">
          <div className="container-mdgt">
            <div className="row row-mdgt">
              <div className="contacts__double-contact">
                <div className="">
                  <h3 className="contacts__header">
                    <i className="bi bi-envelope"></i> Почта:
                  </h3>
                  <div className="contacts__description">
                    <a
                      href="mailto:support@mdgt.ru"
                      target="_blank"
                      rel="noreferrer"
                      className="contacts__link"
                    >
                      support@mdgt.ru
                    </a>
                  </div>
                </div>
              </div>
              <div className="contacts__double-contact">
                <div className="">
                  <h3 className="contacts__header">
                    <i className="bi bi-globe"></i> Веб-сайт:
                  </h3>
                  <div className="contacts__description">
                    <a
                      href="http://mdgt.site/"
                      target="_blank"
                      rel="noreferrer"
                      className="contacts__link"
                    >
                      mdgt.site
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="footer__logo">
          <a
            href="https://mdgt.ru/"
            target="_blank"
            rel="noreferrer"
            className="mb-3 me-2 mb-md-0 text-muted_mdgt text-decoration-none lh-1"
          >
            <img className="footer__img" src={mdgt} alt="логотип МДГТ" />
          </a>
          <span className="text-muted_mdgt">
            &copy; Мостдоргеотрест {new Date().getFullYear()}
          </span>
        </div>

        <div
          className="modal fade"
          id="exampleModal"
          tabIndex="-1"
          aria-labelledby="exampleModalLabel"
          aria-hidden="true"
        >
          <div className="modal-dialog modal-lg modal-dialog-centered">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title" id="exampleModalLabel">
                  На карте
                </h5>
                <button
                  type="button"
                  className="btn-close"
                  data-bs-dismiss="modal"
                  aria-label="Close"
                ></button>
              </div>
              <div className="modal-body">
                <div className="normalMap" id="mapId">
                  <iframe
                    title="map"
                    id="map_702049289"
                    frameBorder="0"
                    width="100%"
                    height="600px"
                    sandbox="allow-modals allow-forms allow-scripts allow-same-origin allow-popups allow-top-navigation-by-user-activation"
                  ></iframe>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="fixed-bottom p-4">
          <div
            className="toast text-white w-100 mw-100"
            id="toast"
            role="alert"
            data-bs-autohide="false"
          >
            <div className="toast-body p-4 d-flex flex-column">
              <h4>Мы используем файлы cookie.</h4>
              <p>
                Мы используем cookie для обеспечения функционирования веб-сайта
                и улучшения качества обслуживания. Если Вы не хотите, чтобы эти
                данные обрабатывались, отключите cookie в настройках браузера.
              </p>
              <div className="ms-auto">
                <button type="button" className="btn btn-light" id="btnAccept">
                  Принять
                </button>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </>
  );
}
