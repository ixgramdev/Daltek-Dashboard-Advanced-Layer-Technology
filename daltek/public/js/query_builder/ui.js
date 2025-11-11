// Accesos rápidos al DOM y helpers visuales

(function (window) {
  "use strict";

  window.QueryBuilderUI = window.QueryBuilderUI || {};

  const getState = () => window.QueryBuilderState.state;

  // Elementos principales del query builder
  const tableHint = document.getElementById("tableHint");
  const colsSection = document.getElementById("colsSection");
  const fieldsSearch = document.getElementById("fieldsSearch");
  const fieldsDropdown = document.getElementById("fieldsDropdown");
  const addColBtn = document.getElementById("addColBtn");
  const colsList = document.getElementById("colsList");
  const selectAllCols = document.getElementById("selectAllCols");

  const filtersSection = document.getElementById("filtersSection");
  const filtersContainer = document.getElementById("filtersContainer");
  const addFilterBtn = document.getElementById("addFilterBtn");

  const resetBtn = document.getElementById("resetBtn");
  const saveQueryBtn = document.getElementById("saveQueryBtn");

  window.QueryBuilderUI.dom = {
    tableHint,
    colsSection,
    fieldsSearch,
    fieldsDropdown,
    addColBtn,
    colsList,
    selectAllCols,
    filtersSection,
    filtersContainer,
    addFilterBtn,
    resetBtn,
    saveQueryBtn,
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
        if (!state.selectedCols.length) filtersSection.style.display = "none";
      });
      colsList.appendChild(chip);
    });
  };
})(window);
