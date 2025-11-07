// ============================
// CYBERADII - REPORT SCRIPT (Risk Bar Fixed + Unified Logic)
// ============================

document.addEventListener("DOMContentLoaded", function () {
  // ---------- METRICS ANIMATION ----------
  document.querySelectorAll(".metric-value").forEach((metric) => {
    const target = parseFloat(metric.innerText.replace(/[^0-9.]/g, ""));
    if (isNaN(target) || target === 0) return;
    let count = 0;
    const step = target / 40;
    const update = () => {
      count += step;
      if (count >= target) {
        metric.innerText = target.toLocaleString();
      } else {
        metric.innerText = Math.floor(count).toLocaleString();
        requestAnimationFrame(update);
      }
    };
    update();
  });

  // ---------- TABLE ROW HOVER ----------
  document.querySelectorAll("table tbody tr").forEach((row) => {
    row.addEventListener("mouseenter", () => (row.style.backgroundColor = "#f0f7ff"));
    row.addEventListener("mouseleave", () => (row.style.backgroundColor = "transparent"));
  });

  // ---------- COLOR MAP ----------
  const COLORS = {
    low: "#00b894",       // green
    medium: "#f9ca24",    // yellow
    high: "#e67e22",      // orange
    critical: "#d63031",  // red
  };

  // ---------- CHARTS ----------
  const anomalyCanvas = document.getElementById("anomalyChart");
  const barCanvas = document.getElementById("barChart");

  // ---- Doughnut Chart (Normal vs Anomalies) ----
  if (anomalyCanvas) {
    const normalLogs = parseFloat(anomalyCanvas.dataset.normal) || 0;
    const anomalies = parseFloat(anomalyCanvas.dataset.anomaly) || 0;
    new Chart(anomalyCanvas, {
      type: "doughnut",
      data: {
        labels: ["Normal Logs", "Anomalies"],
        datasets: [
          {
            data: [normalLogs, anomalies],
            backgroundColor: [COLORS.low, COLORS.critical],
            borderColor: "#fff",
            borderWidth: 2,
          },
        ],
      },
      options: {
        plugins: {
          legend: {
            labels: {
              color: "#111",
              font: { size: 14, family: "Smooch Sans" },
            },
          },
        },
        cutout: "70%",
      },
    });
  }

  // ---- Severity Risk Bar Chart ----
  if (barCanvas) {
    const percent = parseFloat(barCanvas.dataset.percent) || 0;
    const labels = ["Low", "Medium", "High", "Critical"];
    const colors = [COLORS.low, COLORS.medium, COLORS.high, COLORS.critical];

    // Compute which severity to activate
    let idx = 0;
    if (percent < 1) idx = 0;
    else if (percent < 5) idx = 1;
    else if (percent < 15) idx = 2;
    else idx = 3;

    const data = [0, 0, 0, 0];
    data[idx] = percent;

    new Chart(barCanvas, {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "Severity Risk (%)",
            data,
            backgroundColor: colors,
            borderColor: "#222",
            borderWidth: 1.8,
          },
        ],
      },
      options: {
        responsive: true,
        scales: {
          x: {
            ticks: { color: "#111", font: { size: 13 } },
            grid: { color: "rgba(0,0,0,0.05)" },
          },
          y: {
            beginAtZero: true,
            max: 100,
            ticks: { color: "#111", stepSize: 10 },
            grid: { color: "rgba(0,0,0,0.05)" },
          },
        },
        plugins: {
          legend: { labels: { color: "#111", font: { size: 13 } } },
        },
      },
    });
  }

  // ---------- RISK LEVEL BAR (the horizontal “scroll-bar” style one) ----------
  const riskBar = document.querySelector(".risk-fill");
  const riskLabel = document.querySelector(".risk-label span");
  if (riskBar && riskLabel) {
    const cls = riskLabel.className.trim().toLowerCase();
    const bgColor = COLORS[cls] || "#888";
    riskBar.style.backgroundColor = bgColor;
    riskBar.style.height = "12px";
    riskBar.style.borderRadius = "8px";
    riskBar.style.transition = "width 1.2s ease, background-color 0.5s ease";
    riskBar.style.boxShadow = `0 0 10px ${bgColor}80`;
  }

  // ---------- SCROLL TO TOP ----------
  const scrollBtn = document.createElement("button");
  scrollBtn.innerText = "↑ Top";
  Object.assign(scrollBtn.style, {
    display: "none",
    position: "fixed",
    bottom: "20px",
    right: "20px",
    padding: "8px 12px",
    background: "white",
    color: "black",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontWeight: "600",
    zIndex: "9999",
    transition: "all 0.3s ease",
  });
  document.body.appendChild(scrollBtn);
  scrollBtn.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
  window.addEventListener("scroll", () => {
    scrollBtn.style.display = window.scrollY > 250 ? "block" : "none";
  });
});
