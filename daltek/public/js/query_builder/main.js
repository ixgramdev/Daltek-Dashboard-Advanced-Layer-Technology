// Inicialización del sistema

function init() {
  populateTableSelect();

  tableHint.textContent = "Comienza seleccionando una tabla";

  tableSelect.addEventListener("change", handleTableChange);
  addColBtn.addEventListener("click", handleAddColumn);
  selectAllCols.addEventListener("click", handleSelectAllColumns);

  addFilterBtn.addEventListener("click", addFilterRow);

  runBtn.addEventListener("click", () => {
    if (!state.table) return alert("Selecciona una tabla");
    if (!state.selectedCols.length) return alert("Selecciona columnas");

    const sql = buildSQL();
    sqlArea.value = sql;

    if (showSqlChk.checked) sqlCard.style.display = "block";

    const result = executeMockQuery();
    renderResults(result);
    resultsSection.style.display = "block";
  });

  resetBtn.addEventListener("click", () => {
    location.reload();
  });

  showSqlChk.addEventListener("change", () => {
    sqlCard.style.display = showSqlChk.checked ? "block" : "none";
  });

  themeToggle.addEventListener("click", () => {
    const root = document.documentElement;
    root.classList.toggle("dark");
    themeToggle.textContent = root.classList.contains("dark")
      ? "Modo claro"
      : "Modo oscuro";
  });
}

init();
