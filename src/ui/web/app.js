/**
 * Lógica de la Interfaz Web Interactiva - Calculadora de Álgebra Lineal
 * UAM - Facultad de Ingeniería y Arquitectura (FIA)
 */

document.addEventListener("DOMContentLoaded", () => {
  inicializarNavegacion();
  inicializarModuloVectores();
  inicializarModuloCombinacion();
  inicializarModuloMatrices();
  inicializarModuloEcuaciones();
  inicializarBotonProgramaAnterior();
});

/* ==========================================================================
   1. Navegación por Pestañas
   ========================================================================== */
function inicializarNavegacion() {
  const tabs = document.querySelectorAll(".nav-tab");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      const targetId = tab.getAttribute("data-tab");
      document.querySelectorAll(".tab-pane").forEach(pane => {
        pane.classList.remove("active");
      });
      document.getElementById(targetId)?.classList.add("active");
    });
  });
}

function mostrarToast(mensaje, duracion = 3500) {
  const toast = document.getElementById("notification-toast");
  const msgEl = document.getElementById("toast-message");
  if (!toast || !msgEl) return;
  msgEl.innerText = mensaje;
  toast.classList.remove("hidden");
  setTimeout(() => {
    toast.classList.add("hidden");
  }, duracion);
}

/* ==========================================================================
   2. Módulo de Vectores
   ========================================================================== */
let vectorDim = 3;

function inicializarModuloVectores() {
  actualizarEntradasVectores();
  cargarEjemploVector(1);
}

function cambiarDimVector(delta) {
  const input = document.getElementById("vec-dim");
  let val = parseInt(input.value, 10) || 3;
  val = Math.max(1, Math.min(20, val + delta));
  input.value = val;
  actualizarEntradasVectores();
}

function actualizarEntradasVectores() {
  const input = document.getElementById("vec-dim");
  vectorDim = parseInt(input.value, 10) || 3;

  const contU = document.getElementById("vec-u-inputs");
  const contV = document.getElementById("vec-v-inputs");
  contU.innerHTML = "";
  contV.innerHTML = "";

  for (let i = 0; i < vectorDim; i++) {
    const inpU = document.createElement("input");
    inpU.type = "text";
    inpU.className = "cell-input";
    inpU.id = `vec-u-${i}`;
    inpU.placeholder = `u_${i + 1}`;
    inpU.value = (i + 1).toString();
    contU.appendChild(inpU);

    const inpV = document.createElement("input");
    inpV.type = "text";
    inpV.className = "cell-input";
    inpV.id = `vec-v-${i}`;
    inpV.placeholder = `v_${i + 1}`;
    inpV.value = (vectorDim - i).toString();
    contV.appendChild(inpV);
  }
}

function obtenerValoresVector(prefijo) {
  const res = [];
  for (let i = 0; i < vectorDim; i++) {
    const el = document.getElementById(`vec-${prefijo}-${i}`);
    res.push(el ? el.value.trim() || "0" : "0");
  }
  return res;
}

function cargarEjemploVector(tipo) {
  const input = document.getElementById("vec-dim");
  if (tipo === 1) {
    input.value = 3;
    actualizarEntradasVectores();
    const uVals = ["2", "-3", "4"];
    const vVals = ["5", "1", "-2"];
    uVals.forEach((val, i) => document.getElementById(`vec-u-${i}`).value = val);
    vVals.forEach((val, i) => document.getElementById(`vec-v-${i}`).value = val);
    document.getElementById("vec-scalar-c").value = "3";
  } else {
    input.value = 4;
    actualizarEntradasVectores();
    const uVals = ["1/2", "-3/4", "1", "5/2"];
    const vVals = ["3/2", "1/4", "-2", "0"];
    uVals.forEach((val, i) => document.getElementById(`vec-u-${i}`).value = val);
    vVals.forEach((val, i) => document.getElementById(`vec-v-${i}`).value = val);
    document.getElementById("vec-scalar-c").value = "-2";
  }
}

async function calcularOperacionVector(operacion) {
  const u = obtenerValoresVector("u");
  const v = obtenerValoresVector("v");
  const c = document.getElementById("vec-scalar-c").value.trim() || "1";

  const badge = document.getElementById("vec-badge-status");
  const resultBox = document.getElementById("vec-result-content");
  badge.className = "badge badge-dim";
  badge.innerText = "Calculando...";

  try {
    const res = await fetch("/api/vectores/operar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ operacion, u, v, c })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Error al procesar la operación");

    badge.className = "badge badge-success";
    badge.innerText = "Éxito";

    let html = `
      <div class="result-card-highlight">
        <div class="result-formula">${data.titulo_operacion}: ${data.resultado_str}</div>
        <div class="result-explanation">${data.explicacion_teorica}</div>
      </div>
    `;

    if (data.desglose_componentes && data.desglose_componentes.length > 0) {
      html += `<div class="steps-container"><h4>Desglose componente a componente:</h4>`;
      data.desglose_componentes.forEach(paso => {
        html += `<div class="step-item"><div class="step-item-desc">${paso}</div></div>`;
      });
      html += `</div>`;
    }

    resultBox.innerHTML = html;
  } catch (err) {
    badge.className = "badge badge-error";
    badge.innerText = "Error";
    resultBox.innerHTML = `<div class="result-card-highlight" style="border-color: rgba(244,63,94,0.4);"><div class="result-formula" style="color:#fda4af;">Error:</div><p>${err.message}</p></div>`;
  }
}

/* ==========================================================================
   3. Módulo de Combinación Lineal
   ========================================================================== */
let combN = 3;
let combK = 2;

function inicializarModuloCombinacion() {
  actualizarEntradasCombinacion();
  cargarEjemploCombinacion(1);
}

function cambiarDimCombN(delta) {
  const el = document.getElementById("comb-dim-n");
  let val = Math.max(1, Math.min(15, (parseInt(el.value, 10) || 3) + delta));
  el.value = val;
  actualizarEntradasCombinacion();
}

function cambiarDimCombK(delta) {
  const el = document.getElementById("comb-num-k");
  let val = Math.max(1, Math.min(10, (parseInt(el.value, 10) || 2) + delta));
  el.value = val;
  actualizarEntradasCombinacion();
}

function actualizarEntradasCombinacion() {
  combN = parseInt(document.getElementById("comb-dim-n").value, 10) || 3;
  combK = parseInt(document.getElementById("comb-num-k").value, 10) || 2;

  const listContainer = document.getElementById("comb-vectors-list");
  listContainer.innerHTML = "";

  for (let j = 0; j < combK; j++) {
    const block = document.createElement("div");
    block.className = "vec-block";
    block.style.marginBottom = "0.75rem";
    block.innerHTML = `<span class="vec-label">Vector v_${j + 1} en R^${combN}:</span>`;

    const row = document.createElement("div");
    row.className = "cells-row";
    for (let i = 0; i < combN; i++) {
      const inp = document.createElement("input");
      inp.type = "text";
      inp.className = "cell-input";
      inp.id = `comb-v-${j}-${i}`;
      inp.placeholder = `v${j + 1}_${i + 1}`;
      inp.value = (i === j ? "1" : "0");
      row.appendChild(inp);
    }
    block.appendChild(row);
    listContainer.appendChild(block);
  }

  const targetContainer = document.getElementById("comb-target-inputs");
  targetContainer.innerHTML = "";
  for (let i = 0; i < combN; i++) {
    const inp = document.createElement("input");
    inp.type = "text";
    inp.className = "cell-input";
    inp.id = `comb-b-${i}`;
    inp.placeholder = `b_${i + 1}`;
    inp.value = "1";
    targetContainer.appendChild(inp);
  }
}

function cargarEjemploCombinacion(caso) {
  if (caso === 1) {
    // SCD: Combinación única
    document.getElementById("comb-dim-n").value = 2;
    document.getElementById("comb-num-k").value = 2;
    actualizarEntradasCombinacion();
    document.getElementById("comb-v-0-0").value = "1";
    document.getElementById("comb-v-0-1").value = "2";
    document.getElementById("comb-v-1-0").value = "3";
    document.getElementById("comb-v-1-1").value = "4";
    document.getElementById("comb-b-0").value = "5";
    document.getElementById("comb-b-1").value = "6";
  } else if (caso === 2) {
    // SI: No es combinación lineal
    document.getElementById("comb-dim-n").value = 3;
    document.getElementById("comb-num-k").value = 2;
    actualizarEntradasCombinacion();
    document.getElementById("comb-v-0-0").value = "1";
    document.getElementById("comb-v-0-1").value = "0";
    document.getElementById("comb-v-0-2").value = "0";
    document.getElementById("comb-v-1-0").value = "0";
    document.getElementById("comb-v-1-1").value = "1";
    document.getElementById("comb-v-1-2").value = "0";
    document.getElementById("comb-b-0").value = "2";
    document.getElementById("comb-b-1").value = "3";
    document.getElementById("comb-b-2").value = "7"; // componente z imposible
  } else {
    // SCI: Infinitas combinaciones
    document.getElementById("comb-dim-n").value = 2;
    document.getElementById("comb-num-k").value = 3;
    actualizarEntradasCombinacion();
    document.getElementById("comb-v-0-0").value = "1";
    document.getElementById("comb-v-0-1").value = "1";
    document.getElementById("comb-v-1-0").value = "2";
    document.getElementById("comb-v-1-1").value = "2";
    document.getElementById("comb-v-2-0").value = "0";
    document.getElementById("comb-v-2-1").value = "1";
    document.getElementById("comb-b-0").value = "3";
    document.getElementById("comb-b-1").value = "4";
  }
}

async function evaluarCombinacionLinealUI() {
  const vectores = [];
  for (let j = 0; j < combK; j++) {
    const vec = [];
    for (let i = 0; i < combN; i++) {
      const el = document.getElementById(`comb-v-${j}-${i}`);
      vec.push(el ? el.value.trim() || "0" : "0");
    }
    vectores.push(vec);
  }

  const b = [];
  for (let i = 0; i < combN; i++) {
    const el = document.getElementById(`comb-b-${i}`);
    b.push(el ? el.value.trim() || "0" : "0");
  }

  const badge = document.getElementById("comb-badge-status");
  const resultBox = document.getElementById("comb-result-content");
  badge.className = "badge badge-dim";
  badge.innerText = "Evaluando...";

  try {
    const res = await fetch("/api/vectores/combinacion", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ vectores, b })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Error al evaluar combinación");

    if (data.es_combinacion) {
      badge.className = (data.tipo_solucion === "UNICA") ? "badge badge-success" : "badge badge-warning";
      badge.innerText = (data.tipo_solucion === "UNICA") ? "Combinación Única (SCD)" : "Infinitas Combinaciones (SCI)";
    } else {
      badge.className = "badge badge-error";
      badge.innerText = "NO es Combinación (SI)";
    }

    let html = `
      <div class="result-card-highlight">
        <div class="result-formula">${data.expresion_algebraica}</div>
        <div class="result-explanation" style="white-space: pre-line;">${data.justificacion_teorica}</div>
      </div>
    `;

    if (data.comprobacion && data.comprobacion.length > 0) {
      html += `
        <div class="verification-box">
          <h4>Comprobación Componente por Componente:</h4>
          ${data.comprobacion.map(c => `<div>${c}</div>`).join("")}
        </div>
      `;
    }

    if (data.pasos && data.pasos.length > 0) {
      html += `<div class="steps-container"><h4>Pasos de Reducción por Filas (Gauss-Jordan):</h4>`;
      data.pasos.forEach(p => {
        html += `
          <div class="step-item">
            <div class="step-item-title">Paso ${p.step_number}: ${p.title}</div>
            <div class="step-item-desc">${p.description}</div>
          </div>
        `;
      });
      html += `</div>`;
    }

    resultBox.innerHTML = html;
  } catch (err) {
    badge.className = "badge badge-error";
    badge.innerText = "Error";
    resultBox.innerHTML = `<div class="result-card-highlight" style="border-color: rgba(244,63,94,0.4);"><div class="result-formula" style="color:#fda4af;">Error:</div><p>${err.message}</p></div>`;
  }
}

/* ==========================================================================
   4. Módulo de Matrices Básicas
   ========================================================================== */
function inicializarModuloMatrices() {
  renderizarMatrizA();
  renderizarMatrizB();
  cargarEjemploMatrices(1);
}

function renderizarMatrizA() {
  const m = parseInt(document.getElementById("mat-a-m").value, 10) || 2;
  const n = parseInt(document.getElementById("mat-a-n").value, 10) || 3;
  const grid = document.getElementById("mat-a-grid");
  grid.style.gridTemplateColumns = `repeat(${n}, auto)`;
  grid.innerHTML = "";

  for (let i = 0; i < m; i++) {
    for (let j = 0; j < n; j++) {
      const inp = document.createElement("input");
      inp.type = "text";
      inp.className = "cell-input";
      inp.id = `mat-a-${i}-${j}`;
      inp.value = (i * n + j + 1).toString();
      grid.appendChild(inp);
    }
  }
}

function renderizarMatrizB() {
  const r = parseInt(document.getElementById("mat-b-r").value, 10) || 3;
  const p = parseInt(document.getElementById("mat-b-p").value, 10) || 2;
  const grid = document.getElementById("mat-b-grid");
  grid.style.gridTemplateColumns = `repeat(${p}, auto)`;
  grid.innerHTML = "";

  for (let i = 0; i < r; i++) {
    for (let j = 0; j < p; j++) {
      const inp = document.createElement("input");
      inp.type = "text";
      inp.className = "cell-input";
      inp.id = `mat-b-${i}-${j}`;
      inp.value = (i + j + 1).toString();
      grid.appendChild(inp);
    }
  }
}

function obtenerMatrizValores(prefijo, filas, cols) {
  const M = [];
  for (let i = 0; i < filas; i++) {
    const fila = [];
    for (let j = 0; j < cols; j++) {
      const el = document.getElementById(`mat-${prefijo}-${i}-${j}`);
      fila.push(el ? el.value.trim() || "0" : "0");
    }
    M.push(fila);
  }
  return M;
}

function cargarEjemploMatrices(tipo) {
  if (tipo === 1) {
    // Multiplicación A(2x3) x B(3x2)
    document.getElementById("mat-a-m").value = 2;
    document.getElementById("mat-a-n").value = 3;
    document.getElementById("mat-b-r").value = 3;
    document.getElementById("mat-b-p").value = 2;
    renderizarMatrizA();
    renderizarMatrizB();
    const aVals = [["1", "2", "3"], ["4", "5", "6"]];
    const bVals = [["7", "8"], ["9", "1"], ["2", "3"]];
    for (let i = 0; i < 2; i++) for (let j = 0; j < 3; j++) document.getElementById(`mat-a-${i}-${j}`).value = aVals[i][j];
    for (let i = 0; i < 3; i++) for (let j = 0; j < 2; j++) document.getElementById(`mat-b-${i}-${j}`).value = bVals[i][j];
  } else {
    // Suma A(3x3) + B(3x3)
    document.getElementById("mat-a-m").value = 3;
    document.getElementById("mat-a-n").value = 3;
    document.getElementById("mat-b-r").value = 3;
    document.getElementById("mat-b-p").value = 3;
    renderizarMatrizA();
    renderizarMatrizB();
  }
}

async function operarMatrices(operacion) {
  const m = parseInt(document.getElementById("mat-a-m").value, 10);
  const n = parseInt(document.getElementById("mat-a-n").value, 10);
  const r = parseInt(document.getElementById("mat-b-r").value, 10);
  const p = parseInt(document.getElementById("mat-b-p").value, 10);

  const A = obtenerMatrizValores("a", m, n);
  const B = obtenerMatrizValores("b", r, p);
  const k = document.getElementById("mat-scalar-k").value.trim() || "2";

  const badge = document.getElementById("mat-badge-status");
  const resultBox = document.getElementById("mat-result-content");
  badge.className = "badge badge-dim";
  badge.innerText = "Calculando...";

  try {
    const res = await fetch("/api/matrices/operar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ operacion, A, B, k })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Error al realizar la operación matricial");

    badge.className = "badge badge-success";
    badge.innerText = "Completado";

    let html = `
      <div class="result-card-highlight">
        <div class="result-formula">${data.titulo_operacion}</div>
        <pre class="result-formula" style="font-size: 0.95rem; margin-top: 0.5rem; color:#f8fafc;">${data.matriz_formateada}</pre>
        <div class="result-explanation">${data.explicacion_teorica}</div>
      </div>
    `;

    if (data.pasos_multiplicacion && data.pasos_multiplicacion.length > 0) {
      html += `<div class="steps-container"><h4>Cálculo de cada entrada c_ij (Producto Punto Renglón · Columna):</h4>`;
      data.pasos_multiplicacion.forEach(paso => {
        html += `<div class="step-item"><div class="step-item-desc">${paso}</div></div>`;
      });
      html += `</div>`;
    }

    resultBox.innerHTML = html;
  } catch (err) {
    badge.className = "badge badge-error";
    badge.innerText = "Error";
    resultBox.innerHTML = `<div class="result-card-highlight" style="border-color: rgba(244,63,94,0.4);"><div class="result-formula" style="color:#fda4af;">Error Dimensional:</div><p>${err.message}</p></div>`;
  }
}

/* ==========================================================================
   5. Módulo de Ecuaciones Matriciales Ax = b
   ========================================================================== */
let eqM = 3;
let eqN = 3;

function inicializarModuloEcuaciones() {
  renderizarEcuacionMatricial();
  cargarEjemploEcuacion(1);
}

function cambiarDimEqM(delta) {
  const el = document.getElementById("eq-rows-m");
  let val = Math.max(1, Math.min(10, (parseInt(el.value, 10) || 3) + delta));
  el.value = val;
  renderizarEcuacionMatricial();
}

function cambiarDimEqN(delta) {
  const el = document.getElementById("eq-cols-n");
  let val = Math.max(1, Math.min(10, (parseInt(el.value, 10) || 3) + delta));
  el.value = val;
  renderizarEcuacionMatricial();
}

function renderizarEcuacionMatricial() {
  eqM = parseInt(document.getElementById("eq-rows-m").value, 10) || 3;
  eqN = parseInt(document.getElementById("eq-cols-n").value, 10) || 3;

  const grid = document.getElementById("eq-augmented-grid");
  grid.style.gridTemplateColumns = `repeat(${eqN}, auto) 24px auto`;
  grid.innerHTML = "";

  for (let i = 0; i < eqM; i++) {
    // Columnas de A
    for (let j = 0; j < eqN; j++) {
      const inp = document.createElement("input");
      inp.type = "text";
      inp.className = "cell-input";
      inp.id = `eq-a-${i}-${j}`;
      inp.value = (i === j ? "1" : "0");
      grid.appendChild(inp);
    }
    // Separador visual |
    const sep = document.createElement("div");
    sep.style.display = "flex";
    sep.style.alignItems = "center";
    sep.style.justifyContent = "center";
    sep.style.color = "#64748b";
    sep.style.fontWeight = "bold";
    sep.innerText = "│";
    grid.appendChild(sep);

    // Columna de b
    const inpB = document.createElement("input");
    inpB.type = "text";
    inpB.className = "cell-input augmented-cell-b";
    inpB.id = `eq-b-${i}`;
    inpB.value = (i + 1).toString();
    grid.appendChild(inpB);
  }
}

function cargarEjemploEcuacion(caso) {
  if (caso === 1) {
    // SCD: 3x3 único
    document.getElementById("eq-rows-m").value = 3;
    document.getElementById("eq-cols-n").value = 3;
    renderizarEcuacionMatricial();
    const A = [["1", "1", "1"], ["0", "2", "5"], ["2", "5", "-1"]];
    const b = ["6", "-4", "27"];
    for (let i = 0; i < 3; i++) {
      for (let j = 0; j < 3; j++) document.getElementById(`eq-a-${i}-${j}`).value = A[i][j];
      document.getElementById(`eq-b-${i}`).value = b[i];
    }
  } else if (caso === 2) {
    // SI: Sin solución
    document.getElementById("eq-rows-m").value = 2;
    document.getElementById("eq-cols-n").value = 2;
    renderizarEcuacionMatricial();
    document.getElementById("eq-a-0-0").value = "1";
    document.getElementById("eq-a-0-1").value = "2";
    document.getElementById("eq-b-0").value = "3";
    document.getElementById("eq-a-1-0").value = "2";
    document.getElementById("eq-a-1-1").value = "4";
    document.getElementById("eq-b-1").value = "10";
  } else {
    // SCI: Infinitas soluciones
    document.getElementById("eq-rows-m").value = 2;
    document.getElementById("eq-cols-n").value = 3;
    renderizarEcuacionMatricial();
    document.getElementById("eq-a-0-0").value = "1";
    document.getElementById("eq-a-0-1").value = "2";
    document.getElementById("eq-a-0-2").value = "3";
    document.getElementById("eq-b-0").value = "5";
    document.getElementById("eq-a-1-0").value = "2";
    document.getElementById("eq-a-1-1").value = "4";
    document.getElementById("eq-a-1-2").value = "6";
    document.getElementById("eq-b-1").value = "10";
  }
}

async function resolverEcuacionMatricialUI() {
  const A = [];
  const b = [];
  for (let i = 0; i < eqM; i++) {
    const fila = [];
    for (let j = 0; j < eqN; j++) {
      const el = document.getElementById(`eq-a-${i}-${j}`);
      fila.push(el ? el.value.trim() || "0" : "0");
    }
    A.push(fila);
    const elB = document.getElementById(`eq-b-${i}`);
    b.push(elB ? elB.value.trim() || "0" : "0");
  }

  const metodoEl = document.querySelector('input[name="eq-method"]:checked');
  const usar_gauss_jordan = metodoEl ? (metodoEl.value === "gauss_jordan") : true;

  const badge = document.getElementById("eq-badge-status");
  const resultBox = document.getElementById("eq-result-content");
  badge.className = "badge badge-dim";
  badge.innerText = "Resolviendo...";

  try {
    const res = await fetch("/api/ecuaciones/resolver", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ A, b, usar_gauss_jordan })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Error al resolver la ecuación");

    if (data.tipo_sistema === "SCD") {
      badge.className = "badge badge-success";
      badge.innerText = "Solución Única (SCD)";
    } else if (data.tipo_sistema === "SCI") {
      badge.className = "badge badge-warning";
      badge.innerText = "Infinitas Soluciones (SCI)";
    } else {
      badge.className = "badge badge-error";
      badge.innerText = "Sin Solución (SI)";
    }

    let html = `
      <div class="result-card-highlight">
        <div class="result-formula">Sistema: ${data.tipo_sistema}</div>
        <div class="result-explanation" style="white-space: pre-line;">${data.descripcion_sistema}</div>
        <div style="margin-top: 0.75rem; font-family: var(--font-mono); color: #38bdf8;">
          Vector Solución x: [ ${data.vector_solucion.join(", ")} ]
        </div>
      </div>
    `;

    if (data.verificacion && data.verificacion.length > 0) {
      html += `
        <div class="verification-box">
          <h4>Comprobación de Residuo Ax = b:</h4>
          ${data.verificacion.map(v => `<div>${v}</div>`).join("")}
        </div>
      `;
    }

    if (data.pasos && data.pasos.length > 0) {
      html += `<div class="steps-container"><h4>Pasos de Eliminación por Renglones:</h4>`;
      data.pasos.forEach(p => {
        html += `
          <div class="step-item">
            <div class="step-item-title">Paso ${p.step_number}: ${p.title}</div>
            <div class="step-item-desc">${p.description}</div>
          </div>
        `;
      });
      html += `</div>`;
    }

    resultBox.innerHTML = html;
  } catch (err) {
    badge.className = "badge badge-error";
    badge.innerText = "Error";
    resultBox.innerHTML = `<div class="result-card-highlight" style="border-color: rgba(244,63,94,0.4);"><div class="result-formula" style="color:#fda4af;">Error al resolver:</div><p>${err.message}</p></div>`;
  }
}

/* ==========================================================================
   6. Botón de Invocación del Programa Anterior (Semana #3)
   ========================================================================== */
function inicializarBotonProgramaAnterior() {
  const btn = document.getElementById("btn-launch-previous");
  if (!btn) return;
  btn.addEventListener("click", async () => {
    btn.disabled = true;
    mostrarToast("Iniciando programa anterior (Semana #3)...");
    try {
      const res = await fetch("/api/programa-anterior/lanzar", { method: "POST" });
      const data = await res.json();
      if (data.exito) {
        mostrarToast("¡Programa anterior iniciado exitosamente!");
      } else {
        mostrarToast("Aviso: " + data.mensaje, 5000);
      }
    } catch (e) {
      mostrarToast("Error al invocar programa anterior: " + e.message);
    } finally {
      btn.disabled = false;
    }
  });
}
