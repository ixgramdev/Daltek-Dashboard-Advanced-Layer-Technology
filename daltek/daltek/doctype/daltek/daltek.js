frappe.ui.form.on("Daltek", {
  onload(frm) {
    if (!frm.drag_drop_initialized) {
      frm.drag_drop_initialized = true;
      // Cargar widgets.js primero, luego cargar el sistema drag and drop
      frappe.require("/assets/daltek/js/widgets.js", function () {
        console.log("Widgets cargados:", availableWidgets);
        load_drag_drop_system(frm);
      });
    }
  },

  refresh(frm) {
    // Cargar Query Builder si existe el campo HTML
    if (frm.fields_dict.query_builder_html) {
      load_query_builder(frm);
    }
  },
});

// Función para cargar el Query Builder en el campo HTML
function load_query_builder(frm) {
  frappe.call({
    method: "daltek.daltek.doctype.daltek.daltek.get_query_builder_html",
    callback: function (r) {
      if (r.message) {
        frm.fields_dict.query_builder_html.$wrapper.html(r.message);
      }
    },
    error: function (err) {
      console.error("Error cargando Query Builder:", err);
      frm.fields_dict.query_builder_html.$wrapper.html(
        "<div style='padding: 20px; color: red;'>Error al cargar Query Builder</div>",
      );
    },
  });
}

// Función para cargar el sistema Drag and Drop en el campo HTML
function load_drag_drop_system(frm) {
  frappe.call({
    method: "daltek.daltek.doctype.daltek.daltek.get_drag_drop_html",
    callback: function (r) {
      if (r.message) {
        // Inyectar el HTML en el campo
        frm.fields_dict.drag_drop_html.$wrapper.html(r.message);

        // Esperar a que el DOM esté listo y luego inicializar el sistema
        setTimeout(function () {
          if (
            typeof window.initDragDropSystem === "function" &&
            typeof availableWidgets !== "undefined"
          ) {
            console.log(
              "Inicializando sistema Drag and Drop con widgets:",
              availableWidgets,
            );
            window.initDragDropSystem(frm, availableWidgets);
          } else {
            console.error(
              "Sistema Drag and Drop no disponible o widgets no cargados",
            );
          }
        }, 100);
      }
    },
    error: function (err) {
      console.error("Error cargando Drag and Drop:", err);
      frm.fields_dict.drag_drop_html.$wrapper.html(
        "<div style='padding: 20px; color: red;'>Error al cargar Drag and Drop</div>",
      );
    },
  });
}

// ============ CÓDIGO ANTERIOR (YA NO SE USA) ============
// Se mantiene comentado por si se necesita referencia
/*
function init_drag_drop_view(frm) {
  const wrapper = frm.fields_dict["drag_drop_html"].wrapper;
  wrapper.innerHTML = "";

  const layout = document.createElement("div");
  layout.style.display = "flex";
  layout.style.height = "600px";
  layout.style.overflow = "hidden";

  const canvas = document.createElement("div");
  canvas.id = "canvas";
  canvas.style.flex = "1";
  canvas.style.padding = "10px";
  canvas.style.height = "60vh";
  canvas.style.minHeight = "60vh";
  canvas.style.overflowY = "auto";
  canvas.style.borderRadius = "8px";

  const isDark =
    document.body.classList.contains("dark") ||
    document.documentElement.getAttribute("data-theme") === "dark";
  canvas.style.background = isDark ? "#171717" : "#f8f9fa";
  canvas.style.border = isDark ? "1px solid #333" : "1px solid #dee2e6";

  const sidebar = document.createElement("div");
  sidebar.id = "widget-menu";
  sidebar.style.width = "200px";
  sidebar.style.borderLeft = isDark ? "1px solid #333" : "1px solid #dee2e6";
  sidebar.style.padding = "10px";
  sidebar.innerHTML = "<h5 style='margin-top: 0;'>Dashboard Widgets</h5>";

  layout.appendChild(canvas);
  layout.appendChild(sidebar);
  wrapper.appendChild(layout);

  const gridContainer = document.createElement("div");
  gridContainer.style.width = "100%";
  gridContainer.style.minHeight = "100%";
  gridContainer.style.padding = "15px";
  gridContainer.style.cssText += `
        @media (max-width: 768px) {
            padding: 10px;
        }
        @media (max-width: 480px) {
            padding: 5px;
        }
    `;
  canvas.appendChild(gridContainer);

  const grid = GridStack.init(
    {
      column: 12,
      cellHeight: 40,
      verticalMargin: 10,
      disableOneColumnMode: false,
      oneColumnModeDomSort: true,
      disableResize: false,
      float: false,
      staticGrid: false,
      maxRow: 0,
    },
    gridContainer,
  );

  grid.on("change", function (event, items) {
    const updatedWidgets = items.map((item) => {
      const original = frm.doc.layout_json.find(
        (w) => w.id === item.el.dataset.id,
      );
      return {
        id: original.id,
        type: original.type,
        position: { col: item.x, row: item.y, width: item.w, height: item.h },
        properties: { ...original.properties },
      };
    });
    frm.set_value("layout_json", updatedWidgets);
  });

  window.availableWidgets.forEach((widget) => {
    const widgetItem = document.createElement("div");
    widgetItem.innerHTML = widget.previewHtml;
    widgetItem.draggable = true;
    widgetItem.style.marginBottom = "10px";

    widgetItem.addEventListener("mousedown", (e) => {
      e.preventDefault();
      const ghost = widgetItem.cloneNode(true);
      ghost.style.position = "absolute";
      ghost.style.pointerEvents = "none";
      ghost.style.opacity = "0.8";
      ghost.style.zIndex = 9999;
      ghost.style.left = e.pageX + "px";
      ghost.style.top = e.pageY + "px";
      document.body.appendChild(ghost);

      const onMouseMove = (moveEvent) => {
        ghost.style.left = moveEvent.pageX - ghost.offsetWidth / 2 + "px";
        ghost.style.top = moveEvent.pageY - ghost.offsetHeight / 2 + "px";
      };

      const onMouseUp = (upEvent) => {
        document.removeEventListener("mousemove", onMouseMove);
        document.removeEventListener("mouseup", onMouseUp);
        document.body.removeChild(ghost);

        const canvasRect = canvas.getBoundingClientRect();
        if (
          upEvent.clientX >= canvasRect.left &&
          upEvent.clientX <= canvasRect.right &&
          upEvent.clientY >= canvasRect.top &&
          upEvent.clientY <= canvasRect.bottom
        ) {
          const offsetX = upEvent.clientX - canvasRect.left;
          const offsetY = upEvent.clientY - canvasRect.top;
          const cellWidth = canvas.offsetWidth / grid.getColumn();
          const cellHeight = grid.getCellHeight();
          const col = Math.floor(offsetX / cellWidth);
          const row = Math.floor(offsetY / cellHeight);

          addWidget(frm, grid, widget, { x: col, y: row });
        }
      };

      document.addEventListener("mousemove", onMouseMove);
      document.addEventListener("mouseup", onMouseUp);
    });

    sidebar.appendChild(widgetItem);
  });

  renderWidgets(frm, grid);
}

function addWidget(frm, grid, widgetData, pos) {
  const id = widgetData.id + "_" + Date.now();
  const node = document.createElement("div");
  node.className = "grid-stack-item";
  node.dataset.id = id;
  node.dataset.type = widgetData.type;
  node.innerHTML = `
        <div class="grid-stack-item-content" style="padding:0;height:100%;box-sizing:border-box;position:relative;">
            <div style="margin:3px;padding:8px;background:${
              widgetData.options.color
            };border-radius:6px;height:calc(100% - 6px);box-sizing:border-box;display:flex;flex-direction:column;justify-content:space-between;position:relative;overflow:hidden;">
                <div style="display:flex;justify-content:space-between;align-items:center;position:relative;z-index:2;">
                    <h5 style="font-size:11px;color:white;margin:0;font-weight:600;">${
                      widgetData.options.title
                    }</h5>
                    <button style="border:none;border-radius:50%;width:18px;height:18px;background:rgba(255,255,255,0.2);color:white;cursor:pointer;font-size:10px;">⚙</button>
                </div>
                <span style="font-size:20px;color:white;display:block;text-align:center;font-weight:bold;position:relative;z-index:2;">${
                  widgetData.options.number || 0
                }</span>
                <div style="position:absolute;bottom:0;right:0;width:15px;height:15px;background:rgba(255,255,255,0.1);cursor:se-resize;z-index:3;border-radius:3px 0 6px 0;"></div>
            </div>
        </div>
    `;

  node.setAttribute("gs-x", pos.x);
  node.setAttribute("gs-y", pos.y);
  node.setAttribute("gs-w", 2);
  node.setAttribute("gs-h", 4);

  grid.addWidget(node, { x: pos.x, y: pos.y, w: 2, h: 4 });

  const currentWidgets = frm.doc.layout_json || [];
  currentWidgets.push({
    id: widgetData.id,
    type: widgetData.type,
    position: { col: pos.x, row: pos.y, width: 2, height: 4 },
    properties: { ...widgetData.options },
  });
  frm.set_value("layout_json", currentWidgets);

  node.querySelector("button").addEventListener("click", () => {
    const widgets = frm.doc.layout_json || [];
    const instance = widgets.find((w) => node.dataset.id === w.id);
    if (!instance) return;
    const newTitle = prompt("Nuevo título:", instance.properties.title);
    if (newTitle !== null) {
      instance.properties.title = newTitle;
      node.querySelector("h5").textContent = newTitle;
      frm.set_value("layout_json", widgets);
    }
  });
}

function renderWidgets(frm, grid) {
  const widgets = frm.doc.layout_json || [];
  widgets.forEach((widget) => {
    const id = widget.id + "_" + Date.now();
    const node = document.createElement("div");
    node.className = "grid-stack-item";
    node.dataset.id = id;
    node.dataset.type = widget.type;
    node.innerHTML = `
            <div class="grid-stack-item-content" style="padding:0;height:100%;box-sizing:border-box;position:relative;">
                <div style="margin:3px;padding:8px;background:${
                  widget.properties.color
                };border-radius:6px;height:calc(100% - 6px);box-sizing:border-box;display:flex;flex-direction:column;justify-content:space-between;position:relative;overflow:hidden;">
                    <div style="display:flex;justify-content:space-between;align-items:center;position:relative;z-index:2;">
                        <h5 style="font-size:11px;color:white;margin:0;font-weight:600;">${
                          widget.properties.title
                        }</h5>
                        <button style="border:none;border-radius:50%;width:18px;height:18px;background:rgba(255,255,255,0.2);color:white;cursor:pointer;font-size:10px;">⚙</button>
                    </div>
                    <span style="font-size:20px;color:white;display:block;text-align:center;font-weight:bold;position:relative;z-index:2;">${
                      widget.properties.number || 0
                    }</span>
                    <div style="position:absolute;bottom:0;right:0;width:15px;height:15px;background:rgba(255,255,255,0.1);cursor:se-resize;z-index:3;border-radius:3px 0 6px 0;"></div>
                </div>
            </div>
        `;

    grid.addWidget(node, {
      x: widget.position.col || widget.position.x || 0,
      y: widget.position.row || widget.position.y || 0,
      w: 2,
      h: 4,
    });

    node.querySelector("button").addEventListener("click", () => {
      const widgets = frm.doc.layout_json || [];
      const instance = widgets.find((w) => node.dataset.id === w.id);
      if (!instance) return;
      const newTitle = prompt("Nuevo título:", instance.properties.title);
      if (newTitle !== null) {
        instance.properties.title = newTitle;
        node.querySelector("h5").textContent = newTitle;
        frm.set_value("layout_json", widgets);
      }
    });
  });
}
*/
// ============ FIN DEL CÓDIGO ANTERIOR ============
