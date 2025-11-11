// Inicialización del sistema

function init() {
  window.QueryBuilderSteps.populateTableSelect();

  const dom = window.QueryBuilderUI.dom;

  dom.tableHint.textContent = "Comienza seleccionando un DocType";

  dom.tableSelect.addEventListener(
    "change",
    window.QueryBuilderSteps.handleTableChange,
  );
  dom.addColBtn.addEventListener(
    "click",
    window.QueryBuilderSteps.handleAddColumn,
  );
  dom.selectAllCols.addEventListener(
    "click",
    window.QueryBuilderSteps.handleSelectAllColumns,
  );

  dom.addFilterBtn.addEventListener(
    "click",
    window.QueryBuilderSteps.addFilterRow,
  );

  dom.runBtn.addEventListener("click", () => {
    const state = window.QueryBuilderState.state;

    if (!state.table) return frappe.msgprint("Selecciona un DocType");
    if (!state.selectedCols.length)
      return frappe.msgprint("Selecciona columnas");

    const sql = buildSQL();
    dom.sqlArea.value = sql;

    if (dom.showSqlChk.checked) dom.sqlCard.style.display = "block";

    frappe.call({
      method: "daltek.daltek.doctype.daltek.daltek.execute_query_builder_sql",
      args: {
        sql_query: sql,
        limit: 100,
      },
      callback: function (response) {
        if (response.message && response.message.success) {
          window.QueryBuilderUI.renderResults(response.message.data);
          dom.resultsSection.style.display = "block";

          frappe.show_alert({
            message: response.message.message,
            indicator: "green",
          });
        } else {
          frappe.msgprint({
            title: "Error en la consulta",
            message: response.message.error || "Error desconocido",
            indicator: "red",
          });
        }
      },
      error: function (error) {
        console.error("Error ejecutando consulta:", error);
        frappe.msgprint({
          title: "Error de conexión",
          message: "No se pudo ejecutar la consulta: " + error.message,
          indicator: "red",
        });
      },
    });
  });

  dom.resetBtn.addEventListener("click", () => {
    location.reload();
  });

  dom.showSqlChk.addEventListener("change", () => {
    dom.sqlCard.style.display = dom.showSqlChk.checked ? "block" : "none";
  });

  dom.themeToggle.addEventListener("click", () => {
    const root = document.documentElement;
    root.classList.toggle("dark");
    dom.themeToggle.textContent = root.classList.contains("dark")
      ? "Modo claro"
      : "Modo oscuro";
  });
}

init();
