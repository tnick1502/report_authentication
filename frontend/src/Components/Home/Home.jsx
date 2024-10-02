import React, { useContext, useEffect, useState } from "react";

import "./Home.css";

import Context from "../../context";

import ViewsChart from "./ViewsChart";

import { loadImage } from "../../Utils/loadImage";
import { login, signOut } from "../../Utils/login";

import checkMark from "../images/check-mark.svg";
import close from "../images/close.png";
import mainimg from "../images/mainimg.png";
import qr_index from "../images/qr_index.png";
import lock from "../images/lock.gif";
import server from "../images/server.gif";
import qr_transparent from "../images/qr_transparent.png";
import IsMobile from "../../Utils/IsMobile";
import { useNavigate } from "react-router-dom";
import whenReady from "../../Utils/whenReady";
import { parseViews, getViews } from "../../Utils/views";

export default function Home() {
  const { setHomeLoaded, setLogged } = useContext(Context);
  const [reports, setReports] = useState(null);

  const [views, setViews] = useState({ views: [], dates: [] });
  const [chartLoaded, setChartLoaded] = useState(false);

  const navigate = useNavigate();

  useEffect(() => {
    setHomeLoaded(false);
    Promise.all([
      loadImage(checkMark),
      loadImage(close),
      loadImage(mainimg),
      loadImage(qr_index),
      loadImage(lock),
      loadImage(server),
      loadImage(qr_transparent),
    ])
      .then(() => {
        setHomeLoaded(true);
      })
      .catch((err) => {
        setHomeLoaded(true);
        // console.log("Failed to load images", err);
      });

    function updateReports() {
      fetch(`${process.env.REACT_APP_SERVER_IP}reports/count/`)
        .then((response) => {
          if (response.ok && response.status === 200) return response.json();
          return undefined;
        })
        .then((data) => {
          if (data) {
            setReports(data);
          }
        });
    }

    function imageMove() {
      const homeImgLink = document.getElementById("homeImg");
      // const screenWidth = window.innerWidth;
      if (IsMobile() && homeImgLink) {
        homeImgLink.addEventListener("click", (event) => {
          homeImgLink.classList.add("onscroll");
        });
      }

      if (IsMobile() && homeImgLink) {
        const sectionTop = homeImgLink.offsetTop;
        window.addEventListener("scroll", () => {
          if (window.scrollY > sectionTop) {
            homeImgLink.classList.add("onscroll");
          } else {
            homeImgLink.classList.remove("onscroll");
          }
        });
      }
    }

    function updateViewsChart() {
      fetch(`${process.env.REACT_APP_SERVER_IP}stat/period_count`)
        .then((response) => response.json())
        .then((data) => {
          if (data && Object.keys(data).length > 0) {
            const resultData = parseViews(data);
            setViews(resultData);
            setChartLoaded(true);
          }
        });
      // getViews().then((data) => {
      //   const resultData = parseViews(data);
      //   setViews(resultData);
      //   setChartLoaded(true);
      // });
    }

    updateViewsChart();
    updateReports();
    imageMove();
  }, [setHomeLoaded]);

  return (
    <>
      {/* <h2 className="container__title">Проект GEOREPORT</h2> */}
      <div className="index_contener">
        <div className="index_content home_info" id="home">
          <div className="">
            <p>
              Данный проект разработан компанией "АО МОСТДОРГЕОТРЕСТ" с целью
              обеспечения гарантии подлинности данных.
            </p>
            <br />
            <p>
              GEOREPORT позволяет аутентифицировать протоколы лабораторных
              испытаний, тем самым создавая дополнительную степень защиты.
            </p>
            <div className="reports-counter__wrapper">
              <div className="">Аутентифицированных протоколов:</div>
              <h1 className="" id="reportsCounter">
                {reports ? reports : "\u221E"}
              </h1>
            </div>

            <a
              className="btn-test btn btn-success btn-lg w-100 w-lg-50 align-center"
              id="btn-test"
              // onClick={(event) => {
              //   event.preventDefault();
              //   event.stopPropagation();
              //   signOut(setLogged).then(() => {
              //     login(setLogged, "trial", "trial").then(() => {
              //       whenReady().then(() => {
              //         navigate("/login", { replace: true });
              //       });
              //     });
              //   });
              // }}
              href="/report/4c795fb5002852b5af5df9e5de1e44b11b920d6f"
            >
              Протестировать
            </a>
          </div>
          <div className="home-img" id="homeImg">
            <img className="home-img__image" src={mainimg} alt="mainimg"></img>
            <div className="home-img__hover">
              <div className="home-img__link_wrapper">
                <a
                  href="/report/4c795fb5002852b5af5df9e5de1e44b11b920d6f"
                  className="home-img__hover_link"
                >
                  <img src={qr_index} width="100px" alt="qr_index" />
                </a>
              </div>
            </div>
          </div>
        </div>

        <section className="index_content" id="about">
          {/* <hr /> */}
          {/* <div className="content__container container-mdgt">
            <h2 className="container__title">Описание проекта</h2>
          </div>

          <p>
            Данный проект позволяет дублировать данные протоколов испытаний на
            специальном сервере, исключая ручные изменения в протоколе вне
            лаборатории.
          </p>
          */}
          {/* <br />  */}

          <div className="container-fidure">
            <div className="figure">
              {/* <!-- Path 1 --> */}
              <div className="figure__path">
                <div className="figure__path_wrapper">
                  <span
                    className="figure__pathStart"
                    style={{
                      backgroundColor:
                        "var(--brown_logo); outline-color: var(--brown_logo)",
                    }}
                  ></span>
                  <div className="figure__path_rest">
                    <span className="figure__pathPoint"></span>
                    <span className="figure__pathPoint"></span>
                    <span className="figure__pathPoint"></span>
                    <span className="figure__pathPoint"></span>
                    <span className="figure__pathPoint"></span>
                    <span className="figure__pathPoint"></span>
                  </div>
                </div>
                {/* <!-- Path Start Point --> */}
                <div
                  className="figure__product figure__product--right"
                  style={{ backgroundColor: "var(--brown_logo)" }}
                >
                  <div className="figure__productContent">
                    <p className="figure__productDesc">
                      Результаты испытания из протокола загружаются на сервер и
                      хранятся под своим уникальным ключом, исключающим
                      несанкционированный доступ.
                    </p>
                  </div>
                  <div className="figure__productIconBox">
                    <img src={lock} alt="lock gif" />
                  </div>
                </div>
              </div>

              {/* <!-- Path 2 --> */}
              <div className="figure__path">
                <div className="figure__path_wrapper">
                  <span
                    className="figure__pathStart"
                    style={{
                      backgroundColor:
                        "var(--beige_logo); outline-color: var(--beige_logo)",
                    }}
                  ></span>
                  <div className="figure__path_rest">
                    <span className="figure__pathPoint"></span>
                    <span className="figure__pathPoint"></span>
                    <span className="figure__pathPoint"></span>
                    <span className="figure__pathPoint"></span>
                    <span className="figure__pathPoint"></span>
                    <span className="figure__pathPoint"></span>
                  </div>
                </div>
                <div
                  className="figure__product figure__product--right"
                  style={{ backgroundColor: "var(--beige_logo)" }}
                >
                  <div className="figure__productContent">
                    <p className="figure__productDesc">
                      Сервер генерирует специальный QR-код, содержащий ссылку
                      для просмотра данных протокола.
                    </p>
                  </div>
                  <div className="figure__productIconBox">
                    <img src={server} alt="server gif" />
                  </div>
                </div>
              </div>

              {/* <!-- Path 3 --> */}
              <div className="figure__path">
                <div className="figure__path_wrapper">
                  <span
                    className="figure__pathStart"
                    style={{
                      backgroundColor:
                        "var(--green_logo); outline-color: var(--green_logo)",
                    }}
                  ></span>
                  <div className="figure__path_rest">
                    <span className="figure__pathPoint"></span>
                    <span className="figure__pathPoint"></span>
                    <span className="figure__pathPoint"></span>
                    <span className="figure__pathPoint"></span>
                    <span className="figure__pathPoint"></span>
                    <span className="figure__pathPoint"></span>
                  </div>
                </div>
                {/* <!-- Product --> */}
                <div
                  className="figure__product figure__product--right"
                  style={{ backgroundColor: "var(--green_logo)" }}
                >
                  <div className="figure__productContent">
                    <p className="figure__productDesc">
                      QR-код помещается на протокол испытаний, тем самым
                      исключая возможность редактирования данных в протоколе
                      после его выдачи.
                    </p>
                  </div>
                  <div className="figure__productIconBox">
                    <img src={qr_transparent} alt="qr transparent" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <div className="chart-card">
          <div className="chart-card__chart">
            <ViewsChart dataset={views} />
          </div>
        </div>

        {/* <div className="index_content" id="license">
          <hr />

          <div className="mdgt-cards__wrapper">
            <div className="mdgt-card">
              <div className="mdgt-card__title">Стандартная</div>
              <div className="mdgt-card__content">
                <div className="mdgt-card__price">
                  <p>10 000 &#8381;</p>
                  <p>в год</p>
                </div>
                <div className="mdgt-card__options">
                  <ul>
                    <li>
                      <p className="text-start">До 1000 протоколов*</p>
                    </li>
                    <li>
                      <p className="text-start">
                        Личный кабинет{" "}
                        <img
                          className="text-start_check"
                          src={checkMark}
                          alt="check mark"
                        />
                      </p>
                    </li>
                  </ul>
                </div>
              </div>
              <a className="mdgt-card__button" href="mailto:support@mdgt.ru">
                Приобрести
              </a>
            </div>
            <div className="mdgt-card best">
              <div className="mdgt-card__title">Расширенная</div>
              <div className="mdgt-card__content">
                <div className="mdgt-card__price">
                  <p>20 000 &#8381;</p>
                  <p>в год</p>
                </div>
                <div className="mdgt-card__options">
                  <ul>
                    <li>
                      <p className="text-start">До 10 000 протоколов*</p>
                    </li>
                    <li>
                      <p className="text-start">
                        Личный кабинет{" "}
                        <img
                          className="text-start_check"
                          src={checkMark}
                          alt="check mark"
                        />
                      </p>
                    </li>
                    <li>
                      <p className="text-start">
                        API{" "}
                        <img
                          className="text-start_check"
                          src={checkMark}
                          alt="check mark"
                        />
                      </p>
                    </li>
                  </ul>
                </div>
              </div>
              <a className="mdgt-card__button" href="mailto:support@mdgt.ru">
                Приобрести
              </a>
            </div>
            <div className="mdgt-card">
              <div className="mdgt-card__title">Максимальная</div>
              <div className="mdgt-card__content">
                <div className="mdgt-card__price">
                  <p>30 000 &#8381;</p>
                  <p>в год</p>
                </div>
                <div className="mdgt-card__options">
                  <ul>
                    <li>
                      <p className="text-start">До 100 000 протоколов*</p>
                    </li>
                    <li>
                      <p className="text-start">
                        Личный кабинет{" "}
                        <img
                          className="text-start_check"
                          src={checkMark}
                          alt="check mark"
                        />
                      </p>
                    </li>
                    <li>
                      <p className="text-start">
                        API{" "}
                        <img
                          className="text-start_check"
                          src={checkMark}
                          alt="check mark"
                        />
                      </p>
                    </li>
                    <li>
                      <p className="text-start">
                        Дополнительные файлы{" "}
                        <img
                          className="text-start_check"
                          src={checkMark}
                          alt="check mark"
                        />
                      </p>
                    </li>
                  </ul>
                </div>
              </div>
              <a className="mdgt-card__button" href="mailto:support@mdgt.ru">
                Приобрести
              </a>
            </div>
          </div>
        </div> */}
      </div>
    </>
  );
}
