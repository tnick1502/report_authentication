import React, { useState } from "react";

import "./Personal.css";
import { useRef } from "react";
import { useContext } from "react";
import Context from "../../context";
import { useEffect } from "react";

export default function Personal() {
  const { logged, setLogged } = useContext(Context);

  const [userData, setUserData] = useState(null);
  const [reportsCount, setReportsCount] = useState(0);

  const [pageLim, setPageLim] = useState(9);
  const [page, setPage] = useState(0);

  const [objects, setObjects] = useState(null);
  const [objectsData, setObjectsData] = useState(null);
  const [selectedObj, setSelectedObj] = useState(null);

  const delReportId = useRef();
  const requestTokenDialog = useRef();
  const delReportDialog = useRef();
  const submitBtnRef = useRef();

  const reportForm = useRef();
  const formRows = useRef(3);
  const maxFromRows = 10;

  const [inputObj, setInputObj] = useState("");
  const [inputLabNo, setInputLabNo] = useState("");
  const [inputType, setInputType] = useState("");

  const [updateID, setUpdateID] = useState(null);

  const fetchUserData = () => {
    fetch(`${process.env.REACT_APP_SERVER_IP}auth/user/`, {
      method: "GET", // *GET, POST, PUT, DELETE, etc.
      credentials: "include", // include, *same-origin, omit
    }).then((response) => {
      if (response.ok && response.status === 200) {
        response.json().then((data) => {
          setUserData(data);
        });
      } else {
        setLogged(false);
      }
    });
  };

  const fetchReportsCount = () => {
    fetch(`${process.env.REACT_APP_SERVER_IP}reports/count/`, {
      method: "GET", // *GET, POST, PUT, DELETE, etc.
      credentials: "include", // include, *same-origin, omit
    }).then((response) => {
      if (response.ok && response.status === 200) {
        response.json().then((data) => {
          setReportsCount(data);
        });
      }
    });
  };

  const fetchObjects = () => {
    fetch(`${process.env.REACT_APP_SERVER_IP}reports/objects/`, {
      method: "GET", // *GET, POST, PUT, DELETE, etc.
      credentials: "include", // include, *same-origin, omit
    }).then((response) => {
      if (response.ok && response.status === 200) {
        response.json().then((data) => {
          setObjects(data);
        });
      }
    });
  };

  const fetchObject = (objId) => {
    return new Promise((resolve, reject) => {
      fetch(`${process.env.REACT_APP_SERVER_IP}reports/objects/${objId}`, {
        method: "GET", // *GET, POST, PUT, DELETE, etc.
        credentials: "include", // include, *same-origin, omit
      })
        .then((response) => {
          if (response.ok && response.status === 200) {
            response
              .json()
              .then((data) => {
                resolve(data);
              })
              .catch((err) => reject(err));
          }
        })
        .catch((err) => reject(err));
    });
  };

  const requestToken = () => {
    fetch(`${process.env.REACT_APP_SERVER_IP}auth/token/`, {
      method: "POST", // *GET, POST, PUT, DELETE, etc.
      credentials: "include", // include, *same-origin, omit
    }).then((response) => {
      if (!response.ok) {
        requestTokenDialog.current.classList.add(
          "request-token-modal__wrapper_show"
        );
      } else {
        response.json().then((data) => {
          const content = document.getElementById("request-token__content");
          content.innerText = "Токен скопирован в буфер обмена";
          navigator.clipboard.writeText(data["access_token"]);
          requestTokenDialog.current.classList.add(
            "request-token-modal__wrapper_show"
          );
        });
      }
    });
  };

  const setReportForDel = (reportId) => {
    if (!reportId) return;

    delReportId.current = reportId;
    delReportDialog.current.classList.add("del-report-modal__wrapper_show");
  };

  const delReport = () => {
    if (!delReportId.current) return;

    fetch(
      `${process.env.REACT_APP_SERVER_IP}reports/?id=${delReportId.current}`,
      {
        method: "DELETE", // *GET, POST, PUT, DELETE, etc.
        credentials: "include", // include, *same-origin, omit
        headers: {
          Accept: "*/*",
        },
      }
    ).then(() => {
      delReportDialog.current.classList.remove(
        "del-report-modal__wrapper_show"
      );
      fetchObjects();
    });
  };

  function downloadData(_BLOB, _file_name) {
    const a = document.createElement("a");
    a.href = window.URL.createObjectURL(_BLOB);
    a.target = "_blank";
    a.download = _file_name;
    a.click();
  }

  const dowloadQr = (ID, object_number, laboratory_number, test_type) => {
    if (!ID) return;

    fetch(`${process.env.REACT_APP_SERVER_IP}reports/qr?id=${ID}`, {
      method: "POST",
      credentials: "include", // include, *same-origin, omit
      headers: {
        Accept: "application/json",
      },
    })
      .then((response) => {
        return response.blob();
      })
      .then((data) => {
        downloadData(
          data,
          `${object_number} - ${laboratory_number} - ${test_type}`
        );
      });
  };

  useEffect(() => {
    if (!logged) return;

    fetchUserData();
    fetchReportsCount();
    fetchObjects();
  }, [logged]);

  useEffect(() => {
    if (!objects) return;

    let promiseArr = objects
      .filter((obj) => {
        if (selectedObj) return obj === selectedObj;
        return true;
      })
      .map((obj) => {
        return fetchObject(obj).then((data) => {
          if (!data) return null;
          return data;
        });
      });

    Promise.all(promiseArr).then((data) => {
      let objectsData = data.filter((obj) => (obj ? true : false));
      if (!objectsData) return;
      setObjectsData(objectsData.flat(1));
    });
  }, [objects, selectedObj]);

  function clearSubmit() {
    const inputs = document.querySelectorAll("#request-report .form-control");
    inputs.forEach((input) => {
      input.classList.remove("is-valid");
      input.classList.remove("is-invalid");
    });

    const requestReportSuccses = document.getElementById(
      "request-report-succses"
    );
    if (requestReportSuccses) {
      requestReportSuccses.classList.remove("request-report-succses-show");
    }
  }

  const submitReport = (event) => {
    event.preventDefault();
    event.stopPropagation();

    clearSubmit();

    const inputObj = document.getElementById("inputObj"),
      inputLabNo = document.getElementById("inputLabNo"),
      inputType = document.getElementById("inputType");

    if (reportForm.current.inputObj.length === 0) {
      inputObj.classList.add("is-invalid");
      submitBtnRef.current.disabled = false;
      return;
    } else inputObj.classList.add("is-valid");

    if (reportForm.current.inputType === 0) {
      inputLabNo.classList.add("is-invalid");
      submitBtnRef.current.disabled = false;
      return;
    } else inputLabNo.classList.add("is-valid");

    if (reportForm.current.inputLabNo === 0) {
      inputType.classList.add("is-invalid");
      submitBtnRef.current.disabled = false;
      return;
    } else inputType.classList.add("is-valid");

    let notValid = false;
    // Проверяем парные поля (поля должны быть заполнены по парам)
    const inputs = document.querySelectorAll(
      "#request-report .col-6 .form-control"
    );
    // Будем проверять элементы парами, проходя по массиву через одного
    for (let i = 0; i < inputs.length - 1; i = i + 2) {
      // Пустые пары тупо пропускаем
      if (inputs[i].value.length === 0 && inputs[i + 1].value.length === 0) {
        continue;
      }
      if (inputs[i].value.length === 0 && inputs[i + 1].value.length !== 0) {
        inputs[i].classList.add("is-invalid");
        inputs[i + 1].classList.add("is-valid");
        notValid = true;
        continue;
      }
      if (inputs[i].value.length !== 0 && inputs[i + 1].value.length === 0) {
        inputs[i].classList.add("is-valid");
        inputs[i + 1].classList.add("is-invalid");
        notValid = true;
        continue;
      }
      inputs[i].classList.add("is-valid");
      inputs[i + 1].classList.add("is-valid");
    }

    if (notValid) {
      submitBtnRef.current.disabled = false;
      return;
    }

    // Содаем из формы класс с данными
    const formData = new FormData(event.target);

    const resultInfo = {};
    const resultData = {};

    for (let [key, value] of formData.entries()) {
      // Оба значения будут браться по параметру name парных элементов
      // Если name импута содержит нижнее подчеркивание, то это парный элемент
      if (key.includes("_")) {
        const data = formData.getAll(key);

        if (data[0].length === 0 || data[1].length === 0) {
          continue;
        }

        resultData[data[0]] = data[1];
      } else {
        resultInfo[key] = value;
      }
    }

    if (updateID) {
      sendUpdateReport(updateID, resultInfo, resultData);
    } else {
      sendRequestReport(resultInfo, resultData);
    }

    fetchObjects();

    submitBtnRef.current.disabled = false;
  };

  function sendRequestReport(info, tableData) {
    fetch(`${process.env.REACT_APP_SERVER_IP}reports/`, {
      method: "POST",
      credentials: "include", // include, *same-origin, omit
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        object_number: info["inputObj"],
        laboratory_number: info["inputLabNo"],
        test_type: info["inputType"],
        data: tableData,
        active: true,
      }),
    }).then((response) => {
      if (!response.ok) {
        // console.log(response)
        serverError();
      } else {
        response.json().then((response_data) => {
          if (response_data) {
            // Показ сообщения об успехе
            const requestReportSuccses = document.getElementById(
              "request-report-succses"
            );
            if (requestReportSuccses) {
              requestReportSuccses.classList.add("request-report-succses-show");
            }

            // console.log(response_data);

            const id = 0;

            // Скачивание кода
            fetch(`${process.env.REACT_APP_SERVER_IP}reports/qr/?id=${id}`, {
              method: "POST",
              credentials: "include", // include, *same-origin, omit
              headers: {
                Accept: "application/json",
                "Content-Type": "application/json",
              },
            }).then((response) => {
              if (!response.ok) {
                // console.log(response)
                serverError();
                return;
              }

              response.blob().then((response_data) => {
                downloadData(
                  response_data,
                  `${info["inputObj"]} - ${info["inputLabNo"]} - ${info["inputType"]}`
                );

                fetchObjects();
                clearSubmit();
                setInputObj("");
                setInputLabNo("");
                setInputType("");
                setUpdateID(null);
                const inputs = document.querySelectorAll(
                  "#request-report .form-control"
                );
                inputs.forEach((input) => {
                  input.classList.remove("is-valid");
                  input.classList.remove("is-invalid");
                  input.value = "";
                });
              });
            });
          } else {
            serverError();
          }
        });
        // window.location.reload()
      }
    });
  }

  function sendUpdateReport(id, info, tableData) {
    fetch(`${process.env.REACT_APP_SERVER_IP}reports/?id=${id}`, {
      method: "PUT",
      credentials: "include", // include, *same-origin, omit
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        data: tableData,
        active: true,
      }),
    }).then((response) => {
      if (!response.ok) {
        // console.log(response)
        serverError();
      } else {
        response.blob().then((response_data) => {
          if (response_data) {
            // Показ сообщения об успехе
            const requestReportSuccses = document.getElementById(
              "request-report-succses"
            );
            if (requestReportSuccses) {
              requestReportSuccses.classList.add("request-report-succses-show");
            }

            // Скачивание кода
            fetch(`${process.env.REACT_APP_SERVER_IP}reports/qr/?id=${id}`, {
              method: "POST",
              credentials: "include", // include, *same-origin, omit
              headers: {
                Accept: "application/json",
                "Content-Type": "application/json",
              },
            }).then((response) => {
              if (!response.ok) {
                // console.log(response)
                serverError();
                return;
              }

              response.blob().then((response_data) => {
                downloadData(
                  response_data,
                  `${info["inputObj"]} - ${info["inputLabNo"]} - ${info["inputType"]}`
                );

                fetchObjects();
                clearSubmit();
                setInputObj("");
                setInputLabNo("");
                setInputType("");
                setUpdateID(null);
                const inputs = document.querySelectorAll(
                  "#request-report .form-control"
                );
                inputs.forEach((input) => {
                  input.classList.remove("is-valid");
                  input.classList.remove("is-invalid");
                  input.value = "";
                });
              });
            });
          } else {
            serverError();
          }
        });
        // window.location.reload()
      }
    });
  }

  function serverError() {
    const inputs = document.querySelectorAll(
      "#request-report .col-md-4 .form-control"
    );
    inputs.forEach((input) => {
      input.classList.remove("is-valid");
      input.classList.add("is-invalid");
    });
  }

  const addRow = () => {
    if (formRows.current >= maxFromRows) return;

    const lastRow = document.getElementById(
      `inputParam_${formRows.current}_val`
    ).parentNode;

    if (!lastRow) return;

    formRows.current = formRows.current + 1;

    const newRow = `
      <div class="form-group col-6">
        <input
        type="text"
        class="form-control"
        id="inputParam_${formRows.current}"
        name="inputParam_${formRows.current}"
        placeholder=""
        aria-describedby="validationFeedback"/>
        <div class="invalid-feedback" id="validationFeedback">
        Пожалуйста, заполните это поле.</div>
      </div>
      <div class="form-group col-6">
      <input
        type="text"
        class="form-control"
        id="inputParam_${formRows.current}_val"
        name="inputParam_${formRows.current}"
        placeholder=""
        aria-describedby="validationFeedback"/>
        <div class="invalid-feedback" id="validationFeedback">
        Пожалуйста, заполните это поле.</div>
      </div>`;

    lastRow.insertAdjacentHTML("afterend", newRow);
  };

  const deleteRequestFormRow = () => {
    if (formRows.current <= 3) return;

    let lastRow = document.getElementById(
      `inputParam_${formRows.current}_val`
    ).parentNode;

    if (!lastRow) return;
    lastRow.parentNode.removeChild(lastRow);

    lastRow = document.getElementById(
      `inputParam_${formRows.current}`
    ).parentNode;

    if (!lastRow) return;
    lastRow.parentNode.removeChild(lastRow);

    formRows.current = formRows.current - 1;
  };

  const setReportForUpdate = (id, labNo, obj, type, data) => {
    clearSubmit();

    setUpdateID(id);

    const _requestReport = document.getElementById("request-report");

    const gotoBlockValue =
      _requestReport.parentNode.getBoundingClientRect().top +
      window.scrollY -
      document.querySelector("header").offsetHeight;
    window.scrollTo({
      top: gotoBlockValue,
      behavior: "smooth",
    });

    const fillInputTable = (_data) => {
      const keys = Object.keys(_data);
      const dataLenth = keys.length;

      while (formRows.current < dataLenth && formRows.current < maxFromRows) {
        addRow();
      }

      if (formRows.current < keys.length) return;

      for (let row = 0; row < keys.length; row++) {
        let inputRow = document.getElementById(`inputParam_${row + 1}`);
        let inputRowVal = document.getElementById(`inputParam_${row + 1}_val`);

        if (!inputRow || !inputRowVal) continue;

        inputRow.value = keys[row];
        inputRowVal.value = _data[keys[row]];
      }
    };

    setInputLabNo(labNo);
    setInputObj(obj);
    setInputType(type);
    fillInputTable(data);
  };

  return (
    <>
      {!userData ? (
        ""
      ) : (
        <table className="table">
          <tbody>
            <tr>
              <td>Имя пользователя:</td>
              <td>{userData.username}</td>
            </tr>

            <tr>
              <td>Уровень лицензии:</td>
              <td>{userData.license_level}</td>
            </tr>

            <tr>
              <td>Дата окончания лицензии:</td>
              <td>{userData.license_end_date}</td>
            </tr>

            <tr>
              <td>Лимит:</td>
              <td>{userData.limit}</td>
            </tr>

            <tr>
              <td>Выдано:</td>
              <td>{reportsCount ? reportsCount : "-"}</td>
            </tr>

            <tr>
              <td>Остаток:</td>
              <td>{reportsCount ? userData.limit - reportsCount : "-"}</td>
            </tr>
          </tbody>
        </table>
      )}

      <br />

      <div className="request-token__wrapper">
        <button
          type="button"
          className="btn-out btn btn-success btn-lg w-100 w-lg-50 align-center"
          id="get-token-btn"
          onClick={requestToken}
        >
          Получить токен
        </button>
        <a href="#">Просмотр инструкции к api</a>
      </div>

      <div className="request-token-modal__wrapper" ref={requestTokenDialog}>
        <div className="request-token-modal">
          <h2 className="request-token__title">Получение токена</h2>
          <div className="request-token__content" id="request-token__content">
            Получение токена доступно только для лицензии уровня Enterprise
          </div>
          <button
            type="button"
            className="request-token__btn"
            id="request-token-dialog-btn"
            onClick={() => {
              requestTokenDialog.current.classList.remove(
                "request-token-modal__wrapper_show"
              );
            }}
          >
            Хорошо
          </button>
        </div>
      </div>

      <br />

      <div className="request-report__wrapper">
        <div className="request-report__description">
          Уникальный номер протокола формируется по номеру объекта, лаб.номеру и
          типу испытания, поэтому для разных протоколов эти параметры должны
          отличаться. Например, для одной пробы два разных протокола будут с
          одинаковыми номерами объекта и лаб.номерами, но тип опыта нужно
          вводить разный.
        </div>
        <form
          className="row g-3"
          id="request-report"
          ref={reportForm}
          onSubmit={(event) => {
            submitBtnRef.current.disabled = true;
            event.preventDefault();
            event.stopPropagation();
            submitReport(event);
          }}
        >
          <div className="col-md-4">
            <label htmlFor="inputObj">Объект *</label>
            <div className="input-group has-validation">
              <span className="input-group-text" id="inputGroupObjInfo">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  fill="currentColor"
                  className="bi bi-info-circle"
                  viewBox="0 0 16 16"
                >
                  <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
                  <path d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z" />
                </svg>
                <div className="form-info-box">Внутренний номер объекта</div>
              </span>
              <input
                type="text"
                className="form-control"
                id="inputObj"
                name="inputObj"
                placeholder="111-11"
                required
                aria-describedby="inputGroupObjInfo"
                value={inputObj}
                onChange={(event) => setInputObj(event.target.value)}
              />
              <div className="invalid-feedback">Ошибка в номере объекта</div>
            </div>
          </div>
          <div className="col-md-4">
            <label htmlFor="inputLabNo">Лаб.№ *</label>
            <div className="input-group has-validation">
              <span className="input-group-text" id="inputGroupLabInfo">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  fill="currentColor"
                  className="bi bi-info-circle"
                  viewBox="0 0 16 16"
                >
                  <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
                  <path d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z" />
                </svg>
                <div className="form-info-box">Лабораторный номер пробы</div>
              </span>
              <input
                type="text"
                className="form-control"
                id="inputLabNo"
                name="inputLabNo"
                placeholder="A1-1/AA"
                required
                aria-describedby="inputGroupLabInfo"
                value={inputLabNo}
                onChange={(event) => setInputLabNo(event.target.value)}
              />
              <div className="invalid-feedback">
                Ошибка в лабораторном номере
              </div>
            </div>
          </div>
          <div className="col-md-4">
            <label htmlFor="inputType">Тип испытания *</label>
            <div className="input-group has-validation">
              <span className="input-group-text" id="inputGroupTypeInfo">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  fill="currentColor"
                  className="bi bi-info-circle"
                  viewBox="0 0 16 16"
                >
                  <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
                  <path d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z" />
                </svg>
                <div className="form-info-box">Тип испытания</div>
              </span>
              <input
                type="text"
                className="form-control"
                id="inputType"
                name="inputType"
                placeholder="FC, FCE, вибро, консолидация и т.д."
                required
                aria-describedby="inputGroupTypeInfo"
                value={inputType}
                onChange={(event) => setInputType(event.target.value)}
              />
              <div className="invalid-feedback">Ошибка в типе испытания</div>
            </div>
          </div>
          <div className="col-6">
            <label htmlFor="inputParam_1">Параметр</label>
            <input
              type="text"
              className="form-control"
              id="inputParam_1"
              name="inputParam_1"
              placeholder="Дата выдачи протокола"
              aria-describedby="validationFeedback"
            />
            <div className="invalid-feedback" id="validationFeedback">
              Пожалуйста, заполните это поле.
            </div>
          </div>
          <div className="col-6">
            <label htmlFor="inputParam_1_val">Значение</label>
            <input
              type="text"
              className="form-control"
              id="inputParam_1_val"
              name="inputParam_1"
              placeholder="01.09.2022"
              aria-describedby="validationFeedback"
            />
            <div className="invalid-feedback" id="validationFeedback">
              Пожалуйста, заполните это поле.
            </div>
          </div>
          <div className="col-6">
            <input
              type="text"
              className="form-control"
              id="inputParam_2"
              name="inputParam_2"
              placeholder=""
              aria-describedby="validationFeedback"
            />
            <div className="invalid-feedback" id="validationFeedback">
              Пожалуйста, заполните это поле.
            </div>
          </div>
          <div className="col-6">
            <input
              type="text"
              className="form-control"
              id="inputParam_2_val"
              name="inputParam_2"
              placeholder=""
              aria-describedby="validationFeedback"
            />
            <div className="invalid-feedback" id="validationFeedback">
              Пожалуйста, заполните это поле.
            </div>
          </div>
          <div className="col-6">
            <input
              type="text"
              className="form-control"
              id="inputParam_3"
              name="inputParam_3"
              placeholder=""
              aria-describedby="validationFeedback"
            />
            <div className="invalid-feedback" id="validationFeedback">
              Пожалуйста, заполните это поле.
            </div>
          </div>
          <div className="col-6">
            <input
              type="text"
              className="form-control"
              id="inputParam_3_val"
              name="inputParam_3"
              placeholder=""
              aria-describedby="validationFeedback"
            />
            <div className="invalid-feedback" id="validationFeedback">
              Пожалуйста, заполните это поле.
            </div>
          </div>
          <div className="request-form__actions">
            <button
              type="button"
              className="btn btn-outline-secondary request-form__action"
              id="request-form-add-btn"
              onClick={addRow}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                fill="currentColor"
                className="bi bi-plus"
                viewBox="0 0 16 16"
              >
                <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z" />
              </svg>
            </button>
            <button
              type="button"
              className="btn btn-outline-secondary request-form__action"
              id="request-form-delete-btn"
              onClick={deleteRequestFormRow}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                fill="currentColor"
                className="bi bi-dash"
                viewBox="0 0 16 16"
              >
                <path d="M4 8a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7A.5.5 0 0 1 4 8z" />
              </svg>
            </button>
          </div>
          <div className="col-12">
            <button
              type="submit"
              className="btn-out btn btn-success btn-lg w-100 w-lg-50 align-center"
              id="request-report-submit-btn"
              ref={submitBtnRef}
              disabled={
                inputObj &&
                inputObj.length > 0 &&
                inputType &&
                inputType.length > 0 &&
                inputLabNo &&
                inputLabNo.length > 0
                  ? false
                  : true
              }
            >
              Отправить
            </button>
          </div>
        </form>
        <div className="request-report-succses" id="request-report-succses">
          Данные успешно отправлены!
          <div className="request-report-succses__sub">
            Дождитесь загрузки QR-кода
          </div>
        </div>
      </div>

      <br />

      <h2 className="container__title">Выданные протоколы</h2>

      <div className="dropdown">
        <button
          className="btn dropdown-toggle"
          type="button"
          id="dropdownMenuButton1"
          data-bs-toggle="dropdown"
          aria-expanded="false"
        >
          Выбор объекта
        </button>
        <ul
          className="dropdown-menu  verticalScroll"
          aria-labelledby="dropdownMenuButton1"
        >
          <li>
            <button
              className="dropdown-item"
              onClick={() => setSelectedObj(null)}
            >
              Все объекты
            </button>
          </li>
          {!objects ? (
            <></>
          ) : (
            objects.map(function (object, i) {
              return (
                <li key={i}>
                  <button
                    className="dropdown-item"
                    onClick={() => {
                      setSelectedObj(object);
                      setPage(0);
                    }}
                  >
                    {object}
                  </button>
                </li>
              );
            })
          )}
        </ul>
      </div>

      <div className="table-report__wrapper">
        <table className="table">
          <tbody>
            <tr>
              <th scope="col">
                <p>Дата выдачи:</p>
              </th>
              <th scope="col">
                <p>Объект:</p>
              </th>
              <th scope="col">
                <p>Лаб. номер:</p>
              </th>
              <th scope="col">
                <p>Тип испытания</p>
              </th>
              <th scope="col">
                <p>Информация:</p>
              </th>
              <th scope="col">
                <p>Действия:</p>
              </th>
            </tr>
            {!objectsData
              ? ""
              : objectsData
                  .slice(page * pageLim, page * pageLim + pageLim)
                  .map((report, i) => {
                    return (
                      <tr key={i}>
                        <td className="table__td">
                          {report["datetime"].split("T")[0]}
                        </td>
                        <td className="table__td">{report["object_number"]}</td>
                        <td className="table__td">
                          {report["laboratory_number"]}
                        </td>
                        <td className="table__td">{report["test_type"]}</td>
                        <td className="table__td">
                          {Object.keys(report["data"]).map((key) => (
                            <div key={key}>
                              {key}: {report["data"][key]}
                            </div>
                          ))}
                        </td>
                        <td className="table__td">
                          <div className="action">
                            <button
                              className="update-report-btn"
                              // data-id="{{ key }}"
                              // data-object_number="{{ value["object_number"] }}"
                              // data-laboratory_number="{{ value["laboratory_number"] }}"
                              // data-test_type="{{ value["test_type"] }}"
                            >
                              <img
                                src="https://s3.timeweb.com/cw78444-3db3e634-248a-495a-8c38-9f7322725c84/georeport/static/images/update.png"
                                className="img-fluid"
                                width="30"
                                height="30"
                                alt="update"
                                onClick={() => {
                                  setReportForUpdate(
                                    report["id"],
                                    report["laboratory_number"],
                                    report["object_number"],
                                    report["test_type"],
                                    report["data"]
                                  );
                                }}
                              />
                            </button>
                            <button
                              className="delete-report-btn"
                              onClick={() => setReportForDel(report["id"])}
                              // data-id="{{ key }}"
                            >
                              <img
                                src="https://s3.timeweb.com/cw78444-3db3e634-248a-495a-8c38-9f7322725c84/georeport/static/images/trash.png"
                                className="img-fluid"
                                width="30"
                                height="30"
                                alt="delete"
                              />
                            </button>
                            <button
                              className="download-report-btn"
                              // data-id=" key "
                              // data-object_number='value["object_number"]'
                              // data-laboratory_number='value["laboratory_number"]'
                              // data-test_type='value["test_type"]'
                              onClick={() => {
                                dowloadQr(
                                  report["id"],
                                  report["object_number"],
                                  report["laboratory_number"],
                                  report["test_type"]
                                );
                              }}
                            >
                              <img
                                src="https://s3.timeweb.com/cw78444-3db3e634-248a-495a-8c38-9f7322725c84/georeport/static/images/download.png"
                                className="img-fluid"
                                width="30"
                                height="30"
                                alt="download"
                              />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
          </tbody>
        </table>
      </div>

      <div>
        <nav aria-label="Page navigation example">
          {!objectsData ? (
            <li className="page-item active">
              <button
                className="page-link"
                onClick={() => {
                  setPage(0);
                }}
              >
                1
              </button>
            </li>
          ) : (
            <ul className="pagination horizontalScroll">
              {Array(Math.ceil(objectsData.length / pageLim))
                .fill(0)
                .map((elem, i) => {
                  return (
                    <li
                      className={`page-item  ${page === i ? "active" : ""}`}
                      key={i}
                    >
                      <button
                        className="page-link"
                        onClick={() => {
                          setPage(i);
                        }}
                      >
                        {i + 1}
                      </button>
                    </li>
                  );
                })}
            </ul>
          )}
        </nav>
      </div>

      <div
        className="del-report-modal__wrapper"
        id="del-report-dialog"
        ref={delReportDialog}
      >
        <div className="del-report-modal">
          <h2 className="del-report__title">Удалить отчет?</h2>
          <div className="del-report__content">
            Это действие отменить нельзя.
          </div>
          <div className="del-report__actions">
            <button
              type="button"
              className="del-report__btn"
              id="del-report__btn-cancel"
              onClick={() => {
                delReportId.current = null;
                delReportDialog.current.classList.remove(
                  "del-report-modal__wrapper_show"
                );
              }}
            >
              Отмена
            </button>
            <button
              type="button"
              className="del-report__btn"
              id="del-report__btn-del"
              onClick={delReport}
            >
              Удалить
            </button>
          </div>
        </div>
      </div>

      <br />
    </>
  );
}
