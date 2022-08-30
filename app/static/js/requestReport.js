// ЗАПРОС ОТЧЕТА
const requestReport = document.getElementById("request-report");
if (requestReport) {
  function addRequestFormRow() {
    if (dataRows >= 10) return;

    const lastRow = document.getElementById(
      `inputParam_${dataRows}_val`
    ).parentNode;

    if (!lastRow) return;

    dataRows = dataRows + 1;

    const newRow = `
		<div class="form-group col-6">
		<input
			type="text"
			class="form-control"
			id="inputParam_${dataRows}"
			name="inputParam_${dataRows}"
			placeholder=""/></div>
			<div class="form-group col-6">
			<input
				type="text"
				class="form-control"
				id="inputParam_${dataRows}_val"
				name="inputParam_${dataRows}"
				placeholder=""/></div>`;

    lastRow.insertAdjacentHTML("afterend", newRow);
  }
  function deleteRequestFormRow() {
    if (dataRows <= 3) return;

    let lastRow = document.getElementById(
      `inputParam_${dataRows}_val`
    ).parentNode;

    if (!lastRow) return;
    lastRow.parentNode.removeChild(lastRow);

    lastRow = document.getElementById(`inputParam_${dataRows}`).parentNode;

    if (!lastRow) return;
    lastRow.parentNode.removeChild(lastRow);

    dataRows = dataRows - 1;
  }

  const requestFormAddBtn = document.getElementById("request-form-add-btn");
  const requestFormDeleteBtn = document.getElementById(
    "request-form-delete-btn"
  );

  let dataRows = 3;

  if (requestFormAddBtn && requestFormDeleteBtn) {
    requestFormAddBtn.addEventListener("click", addRequestFormRow);
    requestFormDeleteBtn.addEventListener("click", deleteRequestFormRow);
  }
}
