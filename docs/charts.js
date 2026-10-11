(function () {
  const el = document.getElementById("chart-data");
  if (!el) return;
  const data = JSON.parse(el.textContent);

  function pct(x) {
    return (100 * x).toFixed(x >= 0.995 ? 1 : 0) + "%";
  }

  function fmt(v) {
    const n = Number(v);
    if (n >= 0.995) return n.toFixed(2);
    return n.toFixed(2);
  }

  function renderBars(root, series) {
    const order = [
      ["decisions", "Decisions"],
      ["none", "Resp. none"],
      ["medium", "Resp. medium"],
      ["high", "Resp. high"],
    ];
    root.innerHTML = "";
    for (const [key, label] of order) {
      const v = series[key];
      const row = document.createElement("div");
      row.className = "bar-row";
      row.innerHTML =
        '<div class="name"></div><div class="bar-track"><div class="bar-fill ' +
        key +
        '"></div></div><div class="val"></div>';
      row.querySelector(".name").textContent = label;
      row.querySelector(".val").textContent = fmt(v);
      root.appendChild(row);
      requestAnimationFrame(() => {
        row.querySelector(".bar-fill").style.width = pct(v);
      });
    }
  }

  function renderDepth(root, depth) {
    const depths = ["1-op", "2-op", "3-op"];
    root.innerHTML = "";
    const wrap = document.createElement("div");
    wrap.className = "depth";
    depths.forEach((label, i) => {
      const col = document.createElement("div");
      col.className = "depth-col";
      col.innerHTML =
        '<div class="label"></div><div class="depth-stack"></div>';
      col.querySelector(".label").textContent = label;
      wrap.appendChild(col);
      const stack = col.querySelector(".depth-stack");
      const vals = [
        ["decisions", depth.decisions[i]],
        ["none", depth.none[i]],
        ["medium", depth.medium[i]],
      ];
      vals.forEach(([cls, v]) => {
        const cell = document.createElement("div");
        cell.className = "depth-bar";
        cell.innerHTML =
          '<div class="depth-val"></div><span class="depth-fill ' + cls + '"></span>';
        cell.querySelector(".depth-val").textContent = fmt(v);
        cell.title = cls + ": " + Number(v).toFixed(3);
        stack.appendChild(cell);
        const bar = cell.querySelector(".depth-fill");
        requestAnimationFrame(() => {
          bar.style.height = Math.max(4, 120 * v) + "px";
        });
      });
    });
    root.appendChild(wrap);
    const legend = document.createElement("div");
    legend.className = "depth-legend";
    legend.innerHTML =
      "<span><i class='decisions'></i>Decisions</span>" +
      "<span><i class='none'></i>none</span>" +
      "<span><i class='medium'></i>medium</span>";
    root.appendChild(legend);
  }

  document.querySelectorAll('[data-chart="pairs"]').forEach((n) => renderBars(n, data.pairs));
  document.querySelectorAll('[data-chart="pragmatic"]').forEach((n) => renderBars(n, data.pragmatic));
  document.querySelectorAll('[data-chart="depth"]').forEach((n) => renderDepth(n, data.depth));
})();
