// widgets.js
window.availableWidgets = [
  {
    id: "card_widget",
    title: "KPI Card",
    type: "card",
    previewHtml: `
            <div style="
                width:100px;
                height:60px;
                background:#2196F3;
                color:white;
                text-align:center;
                font-size:12px;
                border-radius:6px;
                display:flex;
                flex-direction:column;
                align-items:center;
                justify-content:center;
            ">
                <img src="/assets/daltek/icons/card.svg" style="width:24px;height:24px;margin-bottom:2px;">
                Card
            </div>
        `,
    options: {
      color: "#2196F3",
      number: 0,
      title: "KPI Card",
      icon: "/assets/daltek/icons/card.svg",
    },
  },
  {
    id: "line_chart_widget",
    title: "Line Chart",
    type: "line_chart",
    previewHtml: `
            <div style="
                width:100px;
                height:60px;
                background:#4CAF50;
                color:white;
                text-align:center;
                font-size:12px;
                border-radius:6px;
                display:flex;
                flex-direction:column;
                align-items:center;
                justify-content:center;
            ">
                <img src="/assets/daltek/icons/chart.svg" style="width:24px;height:24px;margin-bottom:2px;">
                Chart
            </div>
        `,
    options: {
      color: "#4CAF50",
      title: "Line Chart",
      icon: "/assets/daltek/icons/chart.svg",
    },
  },
];
