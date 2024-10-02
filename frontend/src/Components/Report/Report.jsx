import React, { useEffect, useState } from "react";

import "./Report.css";
import { useParams } from "react-router-dom";

export default function Report() {
  const { id } = useParams();
  const [report, setReport] = useState(null);
  const [additional, setAdditional] = useState(null);
  const [notes, setNotes] = useState(null);

  useEffect(() => {
    if (!id) return;
    getReport(id);
    getAdditional(id);
    getNotes(id);
  }, []);

  const getReport = (id) => {
    fetch(`${process.env.REACT_APP_SERVER_IP}reports/?id=${id}`, {
      method: "GET", // *GET, POST, PUT, DELETE, etc.
      credentials: "include", // include, *same-origin, omit
    }).then((response) => {
      if (response.ok && response.status === 200) {
        response.json().then((data) => {
          setReport(data);
          // console.log(data);
        });
      }
    });
  };

  const getAdditional = (id) => {
    fetch(`${process.env.REACT_APP_SERVER_IP}files/?report_id=${id}`, {
      method: "GET", // *GET, POST, PUT, DELETE, etc.
      credentials: "include", // include, *same-origin, omit
    }).then((response) => {
      if (response.ok && response.status === 200) {
        response.json().then((data) => {
          setAdditional(data);
          // console.log(data);
        });
      }
    });
  };

  const getNotes = (id) => {
    fetch(`${process.env.REACT_APP_SERVER_IP}test_type_files/${id}`, {
      method: "GET", // *GET, POST, PUT, DELETE, etc.
      credentials: "include", // include, *same-origin, omit
    }).then((response) => {
      if (response.ok && response.status === 200) {
        response.json().then((data) => {
          setNotes(data);
          // console.log(data);
        });
      }
    });
  };

  function downloadData(_BLOB, _file_name) {
    const a = document.createElement("a");
    a.href = window.URL.createObjectURL(_BLOB);
    a.target = "_blank";
    a.download = _file_name;
    a.click();
  }

  const dowloadFile = (link, object_number, laboratory_number, test_type, filename) => {
    if (!link) return;

    fetch(`${process.env.REACT_APP_SERVER_IP}s3/?key=${link}`, {
      method: "GET",
      credentials: "include", // include, *same-origin, omit
      headers: {
        Accept: "application/json",
      },
    })
      .then((response) => {
        return response.blob();
      })
      .then((data) => {
        downloadData(data, `${object_number} - ${laboratory_number} - ${test_type} ${filename}`);
      });
  };

  return (
    <>
      {report ? (
        <div className="report-wrapper">
          <div className="table__container">
            <div className="table-header">
              <img
                className="table-header__logo"
                src="https://s3.timeweb.com/cw78444-3db3e634-248a-495a-8c38-9f7322725c84/georeport/static/images/lock.gif"
                alt="lock"
              />
              <div className="table-header__wrapper">
                <div className="table-header__title-wrapper">
                  <div className="table-header__title_main">
                    МОСТДОРГЕОТРЕСТ
                  </div>
                </div>
                <a
                  href="https://mdgt.ru"
                  target="_blank"
                  className="table-header__url"
                >
                  mdgt.ru
                </a>
              </div>
            </div>
            <table className="table__table">
              <tbody className="table__tbody">
                {report ? (
                  <>
                    <tr className="table__tr">
                      <td className="table__td">Номер объекта</td>
                      <td className="table__td">{report.object_number}</td>
                    </tr>
                    <tr className="table__tr">
                      <td className="table__td">Лабораторый номер</td>
                      <td className="table__td">{report.laboratory_number}</td>
                    </tr>
                    <tr className="table__tr">
                      <td className="table__td">Дата выдачи протокола</td>
                      <td className="table__td">
                        {new Date(report.datetime).toLocaleString()}
                      </td>
                    </tr>
                    <tr className="table__tr">
                      <td className="table__td">Тип опыта</td>
                      <td className="table__td">{report.test_type}</td>
                    </tr>
                    {Object.keys(report.data).map((key) => {
                      return (
                        <tr className="table__tr" key={key}>
                          <td className="table__td">{key}</td>
                          <td className="table__td">{report.data[key]}</td>
                        </tr>
                      );
                    })}
                  </>
                ) : (
                  ""
                )}
              </tbody>
            </table>
          </div>

          {additional ? (
            <div className="table__container table__container-additional">
              <div className="table-header">
                <div className="table-header__wrapper">
                  <div className="table-header__title-wrapper">
                    <div className="table-header__title_main">
                      Дополнительные файлы
                    </div>
                  </div>
                </div>
              </div>
              <table className="table__table table__table-additional">
                <tbody className="table__tbody">
                  {additional
                    ? additional.map((file) => {
                        const filenameArr = file.filename.split(".");
                        return (
                          <tr className="table__tr table__tr-additional">
                            <td className="table__td">
                              {["png", "jpg"].includes(
                                filenameArr[filenameArr.length - 1]
                              ) ? (
                                <>
                                  <a
                                    href={`${process.env.REACT_APP_SERVER_IP}s3/?key=${file.link}`}
                                    onClick={(event) => {
                                      event.preventDefault();
                                      event.stopPropagation();

                                      dowloadFile(file.link, report.object_number, report.laboratory_number, report.test_type, file.filename);
                                    }}
                                  >
                                    {file.filename}
                                  </a>
                                  <img
                                    src={`${process.env.REACT_APP_SERVER_IP}s3/?key=${file.link}`}
                                    alt=""
                                  />
                                </>
                              ) : (
                                <a
                                  href={`${process.env.REACT_APP_SERVER_IP}s3/?key=${file.link}`}
                                  onClick={(event) => {
                                    event.preventDefault();
                                    event.stopPropagation();

                                    dowloadFile(file.link, report.object_number, report.laboratory_number, report.test_type, file.filename);
                                  }}
                                >
                                  {file.filename}
                                </a>
                              )}
                            </td>
                          </tr>
                        );
                      })
                    : ""}
                </tbody>
              </table>
            </div>
          ) : (
            ""
          )}

          {notes ? (
            <div className="table__container table__container-additional">
              <div className="table-header">
                <div className="table-header__wrapper">
                  <div className="table-header__title-wrapper">
                    <div className="table-header__title_main">
                      Справочные файлы
                    </div>
                  </div>
                </div>
              </div>
              <table className="table__table table__table-additional">
                <tbody className="table__tbody">
                  {notes
                    ? notes.map((file) => {
                        const filenameArr = file.filename.split(".");
                        return (
                          <tr className="table__tr table__tr-additional">
                            <td className="table__td">
                              {["png", "jpg"].includes(
                                filenameArr[filenameArr.length - 1]
                              ) ? (
                                <>
                                  <a
                                    href={`${process.env.REACT_APP_SERVER_IP}s3/?key=${file.link}`}
                                    onClick={(event) => {
                                      event.preventDefault();
                                      event.stopPropagation();

                                      dowloadFile(file.link, report.object_number, report.laboratory_number, report.test_type, file.filename);
                                    }}
                                  >
                                    {file.filename}
                                  </a>
                                  <img
                                    src={`${process.env.REACT_APP_SERVER_IP}s3/?key=${file.link}`}
                                    alt=""
                                  />
                                </>
                              ) : (
                                <a
                                  href={`${process.env.REACT_APP_SERVER_IP}s3/?key=${file.link}`}
                                  onClick={(event) => {
                                    event.preventDefault();
                                    event.stopPropagation();

                                    dowloadFile(file.link, report.object_number, report.laboratory_number, report.test_type, file.filename);
                                  }}
                                >
                                  {file.filename}
                                </a>
                              )}
                            </td>
                          </tr>
                        );
                      })
                    : ""}
                </tbody>
              </table>
            </div>
          ) : (
            ""
          )}
        </div>
      ) : (
        "Данные по отчету не найдены."
      )}
    </>
  );
}
