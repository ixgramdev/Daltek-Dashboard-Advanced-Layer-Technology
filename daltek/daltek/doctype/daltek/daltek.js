frappe.ui.form.on("Daltek", {
  onload(frm) {
    if (!frm.drag_drop_initialized) {
      frm.drag_drop_initialized = true;

      // Cargar widgets y scripts del drag and drop
      frappe.require(
        [
          "/assets/daltek/js/drag_and_drop/widgets.js",
          "/assets/daltek/js/drag_and_drop/state.js",
          "/assets/daltek/js/drag_and_drop/ui.js",
          "/assets/daltek/js/drag_and_drop/grid.js",
          "/assets/daltek/js/drag_and_drop/drag_drop_handlers.js",
          "/assets/daltek/js/drag_and_drop/main.js",
        ],
        function () {
          console.log("✅ Todos los scripts cargados correctamente");
          console.log("Widgets disponibles:", availableWidgets);
          console.log("Sistema Drag and Drop listo:", window.DragDropSystem);
          load_drag_drop_system(frm);
        },
      );
    }
  },

  refresh(frm) {
    toggle_tabs_visibility(frm);

    if (frm.fields_dict.query_builder_html) {
      load_query_builder(frm);
    }
  },

  name1(frm) {
    toggle_tabs_visibility(frm);
  },

  dashboard_owner(frm) {
    toggle_tabs_visibility(frm);
  },
});

function toggle_tabs_visibility(frm) {
  const is_saved = !frm.is_new();
  const has_name = frm.doc.name1 && frm.doc.name1.trim() !== "";
  const has_owner =
    frm.doc.dashboard_owner && frm.doc.dashboard_owner.trim() !== "";

  const should_show_tabs = is_saved && has_name && has_owner;

  const tabs_to_toggle = [
    "editable_menu_tab",
    "query_builder_tab",
    "preview_tab",
  ];

  tabs_to_toggle.forEach((tab_name) => {
    frm.toggle_display(tab_name, should_show_tabs);

    if (tab_name === "editable_menu_tab") {
      frm.toggle_display("editable_menu_html", should_show_tabs);
    } else if (tab_name === "query_builder_tab") {
      frm.toggle_display("query_builder_html", should_show_tabs);
    } else if (tab_name === "preview_tab") {
      frm.toggle_display("drag_drop_html", should_show_tabs);
      frm.toggle_display("preview", should_show_tabs);
    }
  });
}

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

function load_drag_drop_system(frm) {
  frappe.call({
    method: "daltek.daltek.doctype.daltek.daltek.get_drag_drop_html",
    callback: function (r) {
      if (r.message) {
        frm.fields_dict.drag_drop_html.$wrapper.html(r.message);

        setTimeout(function () {
          // Debug: verificar estado de los módulos
          console.log("🔍 Estado de módulos Drag and Drop:");
          console.log(
            "   - window.DragDropSystem:",
            typeof window.DragDropSystem,
          );
          console.log(
            "   - window.initDragDropSystem:",
            typeof window.initDragDropSystem,
          );
          console.log(
            "   - window.availableWidgets:",
            typeof window.availableWidgets,
          );
          console.log(
            "   - availableWidgets (global):",
            typeof availableWidgets,
          );

          if (
            typeof window.initDragDropSystem === "function" &&
            (typeof window.availableWidgets !== "undefined" ||
              typeof availableWidgets !== "undefined")
          ) {
            const widgets = window.availableWidgets || availableWidgets || [];
            console.log(
              "✅ Inicializando sistema Drag and Drop con widgets:",
              widgets,
            );
            window.initDragDropSystem(frm, widgets);
          } else {
            console.error(
              "❌ Sistema Drag and Drop no disponible o widgets no cargados",
            );
            console.error(
              "   Verificar que los scripts fueron cargados correctamente",
            );
          }
        }, 100);
      }
    },
    error: function (err) {
      console.error("Error cargando Drag and Drop:", err);
      frm.fields_dict.drag_drop_html.$wrapper.html(
        "<div style='padding: 20px; color: red;'>Error al cargar Drag and Drop: " +
          err +
          "</div>",
      );
    },
  });
}
