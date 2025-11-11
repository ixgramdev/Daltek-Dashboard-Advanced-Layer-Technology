// Inicialización del sistema

function init() {
  // ✅ Inicializar vistas
  if (window.QueryBuilderViews) {
    window.QueryBuilderViews.loadSavedQueries();
    window.QueryBuilderViews.showListView();
  }

  // ✅ Poblar el dropdown de búsqueda
  window.QueryBuilderSteps.populateTableSelect();

  const dom = window.QueryBuilderUI.dom;
  const searchInput = document.getElementById("search");
  const dropdown = document.getElementById("dropdown");

  dom.tableHint.textContent = "Comienza escribiendo para buscar un DocType";

  // ✅ Event listeners para el campo de búsqueda
  if (searchInput && dropdown) {
    // Filtrar items mientras el usuario escribe
    searchInput.addEventListener("input", function () {
      const query = this.value.toLowerCase();
      dropdown.style.display = "block";

      const allItems = window.QueryBuilderSteps.allDoctypeItems || [];
      const groupTitles = dropdown.querySelectorAll(".dropdown-group-title");
      let visibleCount = 0;

      // Filtrar items
      allItems.forEach((item) => {
        const text = item.textContent.toLowerCase();
        if (text.includes(query)) {
          item.style.display = "block";
          visibleCount++;
        } else {
          item.style.display = "none";
        }
      });

      // Mostrar/ocultar títulos de grupo según si tienen items visibles
      groupTitles.forEach((title) => {
        let hasVisibleItems = false;
        let sibling = title.nextElementSibling;

        while (sibling && !sibling.classList.contains("dropdown-group-title")) {
          if (
            sibling.classList.contains("dropdown-item") &&
            sibling.style.display !== "none"
          ) {
            hasVisibleItems = true;
            break;
          }
          sibling = sibling.nextElementSibling;
        }

        title.style.display = hasVisibleItems ? "block" : "none";
      });

      // Mensaje si no hay coincidencias
      if (visibleCount === 0) {
        dropdown.innerHTML =
          '<div class="dropdown-item" style="color: var(--qb-muted); cursor: default;">No se encontraron coincidencias</div>';
      }
    });

    // Mostrar dropdown al enfocar
    searchInput.addEventListener("focus", function () {
      if (
        window.QueryBuilderSteps.allDoctypeItems &&
        window.QueryBuilderSteps.allDoctypeItems.length > 0
      ) {
        dropdown.style.display = "block";
      }
    });

    // Cerrar dropdown al hacer clic fuera
    document.addEventListener("click", function (e) {
      if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.style.display = "none";
      }
    });
  }

  // ✅ Event listeners para el campo de búsqueda de campos
  const fieldsSearch = document.getElementById("fieldsSearch");
  const fieldsDropdown = document.getElementById("fieldsDropdown");

  if (fieldsSearch && fieldsDropdown) {
    // Filtrar campos mientras el usuario escribe
    fieldsSearch.addEventListener("input", function () {
      const query = this.value.toLowerCase();
      fieldsDropdown.style.display = "block";

      const allItems = window.QueryBuilderSteps.allFieldItems || [];
      const groupTitles = fieldsDropdown.querySelectorAll(
        ".dropdown-group-title",
      );
      let visibleCount = 0;

      // Filtrar items
      allItems.forEach((item) => {
        const text = item.textContent.toLowerCase();
        if (text.includes(query)) {
          item.style.display = "block";
          visibleCount++;
        } else {
          item.style.display = "none";
        }
      });

      // Mostrar/ocultar títulos de grupo según si tienen items visibles
      groupTitles.forEach((title) => {
        let hasVisibleItems = false;
        let sibling = title.nextElementSibling;

        while (sibling && !sibling.classList.contains("dropdown-group-title")) {
          if (
            sibling.classList.contains("dropdown-item") &&
            sibling.style.display !== "none"
          ) {
            hasVisibleItems = true;
            break;
          }
          sibling = sibling.nextElementSibling;
        }

        title.style.display = hasVisibleItems ? "block" : "none";
      });

      // Mensaje si no hay coincidencias
      if (visibleCount === 0) {
        fieldsDropdown.innerHTML =
          '<div class="dropdown-item" style="color: var(--qb-muted); cursor: default;">No se encontraron coincidencias</div>';
      }
    });

    // Mostrar dropdown al enfocar
    fieldsSearch.addEventListener("focus", function () {
      if (
        window.QueryBuilderSteps.allFieldItems &&
        window.QueryBuilderSteps.allFieldItems.length > 0
      ) {
        fieldsDropdown.style.display = "block";
      }
    });

    // Cerrar dropdown al hacer clic fuera
    document.addEventListener("click", function (e) {
      if (
        !fieldsSearch.contains(e.target) &&
        !fieldsDropdown.contains(e.target)
      ) {
        fieldsDropdown.style.display = "none";
      }
    });
  }

  // Event listeners para botones principales
  if (dom.addColBtn) {
    dom.addColBtn.addEventListener(
      "click",
      window.QueryBuilderSteps.handleAddColumn,
    );
  }

  if (dom.selectAllCols) {
    dom.selectAllCols.addEventListener(
      "click",
      window.QueryBuilderSteps.handleSelectAllColumns,
    );
  }

  if (dom.addFilterBtn) {
    dom.addFilterBtn.addEventListener(
      "click",
      window.QueryBuilderSteps.addFilterRow,
    );
  }

  if (dom.resetBtn) {
    dom.resetBtn.addEventListener("click", () => {
      if (window.QueryBuilderViews && window.QueryBuilderViews.resetBuilder) {
        window.QueryBuilderViews.resetBuilder();
      }
    });
  }
}

init();
