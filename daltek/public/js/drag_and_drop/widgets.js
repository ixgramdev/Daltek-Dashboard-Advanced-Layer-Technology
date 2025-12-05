// widgets.js - Definición de widgets disponibles con propiedades generales y específicas
window.availableWidgets = [
  // ========== WIDGETS TIPO ECHART ==========
  {
    // Propiedades generales
    id: "line_chart_widget",
    name: "Line Chart",
    label: "Gráfico de Líneas - Muestra tendencias temporales",
    type: "echart", // Tipo principal

    // Propiedades específicas de EChart
    chart_type: "line", // Subtipo para el backend
    default_data: {
      series: [
        { name: "Ventas", data: [120, 200, 150, 180, 220] },
        { name: "Gastos", data: [80, 120, 100, 140, 160] },
      ],
      categories: ["Ene", "Feb", "Mar", "Abr", "May"],
    },
    default_config: {
      smooth: true,
      fill_area: false,
      colors: ["#2196F3", "#FF9800"],
    },

    // Dimensiones recomendadas para visualización correcta
    default_width: 8,
    default_height: 6,
    min_width: 6,
    min_height: 4,

    // Preview HTML para el sidebar
    previewHtml: `
      <div style="
        width:100px;
        height:60px;
        background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color:white;
        text-align:center;
        font-size:11px;
        border-radius:6px;
        display:flex;
        flex-direction:column;
        align-items:center;
        justify-content:center;
        cursor:grab;
      ">
        <i class="fa fa-line-chart" style="font-size:20px;margin-bottom:4px;"></i>
        <span>Line Chart</span>
      </div>
    `,

    // Configuración del grid
    grid_config: { w: 6, h: 4, minW: 4, minH: 3 },
  },

  {
    id: "bar_chart_widget",
    name: "Bar Chart",
    label: "Gráfico de Barras - Comparaciones categóricas",
    type: "echart",
    chart_type: "bar",
    default_data: {
      series: [{ name: "Ventas Q1", data: [100, 200, 150, 250] }],
      categories: ["Producto A", "Producto B", "Producto C", "Producto D"],
    },
    default_config: {
      barWidth: "60%",
      colors: ["#4CAF50"],
    },
    previewHtml: `
      <div style="
        width:100px;
        height:60px;
        background:linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color:white;
        text-align:center;
        font-size:11px;
        border-radius:6px;
        display:flex;
        flex-direction:column;
        align-items:center;
        justify-content:center;
        cursor:grab;
      ">
        <i class="fa fa-bar-chart" style="font-size:20px;margin-bottom:4px;"></i>
        <span>Bar Chart</span>
      </div>
    `,
    grid_config: { w: 6, h: 4, minW: 4, minH: 3 },
  },

  {
    id: "pie_chart_widget",
    name: "Pie Chart",
    label: "Gráfico Circular - Distribución porcentual",
    type: "echart",
    chart_type: "pie",
    default_data: {
      data: [
        { name: "Categoría A", value: 400 },
        { name: "Categoría B", value: 300 },
        { name: "Categoría C", value: 200 },
        { name: "Categoría D", value: 100 },
      ],
    },
    default_config: {
      show_labels: true,
      radius: "60%",
      colors: ["#FF9800", "#2196F3", "#4CAF50", "#F44336"],
    },
    previewHtml: `
      <div style="
        width:100px;
        height:60px;
        background:linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color:white;
        text-align:center;
        font-size:11px;
        border-radius:6px;
        display:flex;
        flex-direction:column;
        align-items:center;
        justify-content:center;
        cursor:grab;
      ">
        <i class="fa fa-pie-chart" style="font-size:20px;margin-bottom:4px;"></i>
        <span>Pie Chart</span>
      </div>
    `,
    grid_config: { w: 4, h: 4, minW: 3, minH: 3 },
  },

  // ========== WIDGETS TRADICIONALES ==========
  {
    id: "card_widget",
    name: "KPI Card",
    label: "Tarjeta de indicador clave",
    type: "card", // No es echart
    default_properties: {
      title: "KPI",
      value: "0",
      color: "#2196F3",
      icon: "/assets/daltek/icons/card.svg",
    },
    previewHtml: `
      <div style="
        width:100px;
        height:60px;
        background:#2196F3;
        color:white;
        text-align:center;
        font-size:11px;
        border-radius:6px;
        display:flex;
        flex-direction:column;
        align-items:center;
        justify-content:center;
        cursor:grab;
      ">
        <img src="/assets/daltek/icons/card.svg" style="width:20px;height:20px;margin-bottom:4px;">
        <span>KPI Card</span>
      </div>
    `,
    grid_config: { w: 3, h: 2, minW: 2, minH: 2 },
  },
];
