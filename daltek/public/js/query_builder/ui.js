// Accesos rápidos al DOM y helpers visuales

(function (window) {
  "use strict";

  window.QueryBuilderUI = window.QueryBuilderUI || {};

  const getState = () => window.QueryBuilderState.state;

  const tableSelect = document.getElementById("tableSelect");
  const tableHint = document.getElementById("tableHint");
  const colsSection = document.getElementById("colsSection");
  const colsSelect = document.getElementById("colsSelect");
  const addColBtn = document.getElementById("addColBtn");
  const colsList = document.getElementById("colsList");
  const selectAllCols = document.getElementById("selectAllCols");

  const filtersSection = document.getElementById("filtersSection");
  const filtersContainer = document.getElementById("filtersContainer");
  const addFilterBtn = document.getElementById("addFilterBtn");

  const runBtn = document.getElementById("runBtn");
  const resetBtn = document.getElementById("resetBtn");

  const resultsSection = document.getElementById("resultsSection");
  const resultsWrap = document.getElementById("resultsWrap");

  const metaTable = document.getElementById("metaTable");
  const metaCols = document.getElementById("metaCols");
  const metaFilters = document.getElementById("metaFilters");

  const showSqlChk = document.getElementById("showSqlChk");
  const sqlCard = document.getElementById("sqlCard");
  const sqlArea = document.getElementById("sqlArea");

  const themeToggle = document.getElementById("themeToggle");

  window.QueryBuilderUI.dom = {
    tableSelect,
    tableHint,
    colsSection,
    colsSelect,
    addColBtn,
    colsList,
    selectAllCols,
    filtersSection,
    filtersContainer,
    addFilterBtn,
    runBtn,
    resetBtn,
    resultsSection,
    resultsWrap,
    metaTable,
    metaCols,
    metaFilters,
    showSqlChk,
    sqlCard,
    sqlArea,
    themeToggle,
  };

  window.QueryBuilderUI.renderSelectedCols = function () {
    const state = getState();
    colsList.innerHTML = "";

    state.selectedCols.forEach((col) => {
      const chip = document.createElement("div");
      chip.className = "col-chip";
      chip.innerHTML = `${col} <button data-col="${col}" style="border:none;background:transparent;color:var(--qb-muted);cursor:pointer">✕</button>`;
      chip.querySelector("button").addEventListener("click", () => {
        state.selectedCols = state.selectedCols.filter((x) => x !== col);
        window.QueryBuilderUI.renderSelectedCols();
        metaCols.textContent = state.selectedCols.length
          ? state.selectedCols.join(", ")
          : "—";
        if (!state.selectedCols.length) filtersSection.style.display = "none";
      });
      colsList.appendChild(chip);
    });
  };

  window.QueryBuilderUI.renderResults = function (rows) {
    const state = getState();
    resultsWrap.innerHTML = "";

    if (!rows.length) {
      resultsWrap.innerHTML = `<div class="empty">La consulta no devolvió filas.</div>`;
      return;
    }

    const table = document.createElement("table");

    const thead = document.createElement("thead");
    const trh = document.createElement("tr");
    state.selectedCols.forEach((c) => {
      const th = document.createElement("th");
      th.textContent = c;
      trh.appendChild(th);
    });
    thead.appendChild(trh);

    const tbody = document.createElement("tbody");
    rows.forEach((r) => {
      const tr = document.createElement("tr");
      state.selectedCols.forEach((c) => {
        const td = document.createElement("td");
        td.textContent = String(r[c]);
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });

    table.appendChild(thead);
    table.appendChild(tbody);
    resultsWrap.appendChild(table);
  };
})(window);
