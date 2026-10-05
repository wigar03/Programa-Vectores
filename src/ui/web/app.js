/**
 * Lógica de la Interfaz Web Interactiva - Calculadora de Álgebra Lineal
 * UAM - Facultad de Ingeniería y Arquitectura (FIA)
 * 
 * Incluye formateador y renderizador dinámico de LaTeX mediante KaTeX.
 */

document.addEventListener("DOMContentLoaded", () => {
  inicializarTema();
  inicializarNavegacion();
  inicializarModuloVectores();
  inicializarModuloCombinacion();
  inicializarModuloMatrices();
  inicializarModuloInversa();
  inicializarModuloEcuaciones();
  inicializarModuloDeterminante();
  refrescarIconosLucide();
});

function refrescarIconosLucide() {
  if (window.lucide && window.lucide.createIcons) {
    try {
      window.lucide.createIcons();
    } catch (e) {
      console.warn("Lucide icons warning:", e);
    }
  }
}

/* ==========================================================================
   1. Utilidades de Renderizado LaTeX (KaTeX) Adaptativo y Multilínea
   ========================================================================== */
let notacionCombinacion = "transpuesta"; // "transpuesta" por defecto para combinación lineal
let ultimoCalculoVector = null;
let ultimoCalculoCombinacion = null;

function cambiarNotacionCombinacion(modo) {
  notacionCombinacion = modo;
  if (ultimoCalculoCombinacion) {
    renderizarResultadoCombinacionUI(ultimoCalculoCombinacion);
  }
}

function formatScalarCoeff(cVal) {
  const s = formatLatexFrac(cVal);
  // Si contiene suma o resta interna (ej: "3 - 2t", "1 + s"), envolver en paréntesis
  const innerOp = s.slice(1).includes("+") || s.slice(1).includes("-");
  if (innerOp && !s.startsWith("(") && !s.startsWith("\\left(")) {
    return `(${s})`;
  }
  return s;
}

function formatLatexFrac(val) {
  if (val === undefined || val === null) return "0";
  let s = String(val).trim();
  if (s.includes("/")) {
    const parts = s.split("/");
    if (parts.length === 2) {
      const isNeg = parts[0].startsWith("-");
      const num = parts[0].replace("-", "").trim();
      const den = parts[1].trim();
      return isNeg ? `-\\frac{${num}}{${den}}` : `\\frac{${num}}{${den}}`;
    }
  }
  if (s.includes("_")) {
    s = s.replace(/_([0-9a-zA-Z]+)/g, "_{$1}");
  }
  return s;
}

/**
 * Formatea un vector de forma inteligente:
 * - En modo 'transpuesta' o si n > 4 en modo 'auto': produce (v1, v2, ..., vn)^T (compacto, sin scroll).
 * - En modo 'columna' o si n <= 4 en modo 'auto': produce matriz columna pmatrix.
 */
function formatVectorSmart(vec, modo = "auto") {
  if (!vec || vec.length === 0) return "(0)";
  const n = vec.length;
  const usarTranspuesta = (modo === "transpuesta") || (modo === "auto" && n > 4);

  if (usarTranspuesta) {
    return `(${vec.map(formatLatexFrac).join(",\\; ")})^T`;
  }
  return `\\begin{pmatrix} ${vec.map(formatLatexFrac).join(" \\\\ ")} \\end{pmatrix}`;
}

function vectorToLatexCol(vec) {
  if (!vec || vec.length === 0) return "\\begin{pmatrix} 0 \\end{pmatrix}";
  return "\\begin{pmatrix} " + vec.map(formatLatexFrac).join(" \\\\ ") + " \\end{pmatrix}";
}

function vectorToLatexRow(vec) {
  if (!vec || vec.length === 0) return "(0)";
  return "(" + vec.map(formatLatexFrac).join(",\\; ") + ")";
}

function matrixToLatex(mat) {
  if (!mat || mat.length === 0) return "\\begin{pmatrix} 0 \\end{pmatrix}";
  const rows = mat.map(row => row.map(formatLatexFrac).join(" & "));
  return "\\begin{pmatrix} " + rows.join(" \\\\ ") + " \\end{pmatrix}";
}

function augmentedMatrixToLatex(mat, splitCol) {
  if (!mat || mat.length === 0) return "\\begin{pmatrix} 0 \\end{pmatrix}";
  const nCols = mat[0].length;
  const split = splitCol !== undefined ? splitCol : Math.floor(nCols / 2);
  const leftSpec = "c".repeat(split);
  const rightSpec = "c".repeat(nCols - split);
  const alignSpec = `${leftSpec}|${rightSpec}`;
  const rows = mat.map(row => row.map(formatLatexFrac).join(" & "));
  return `\\left[\\begin{array}{${alignSpec}} ${rows.join(" \\\\ ")} \\end{array}\\right]`;
}

function renderLatexElement(element, latexCode, displayMode = true) {
  if (!element) return;
  if (window.katex) {
    try {
      katex.render(latexCode, element, {
        displayMode: displayMode,
        throwOnError: false,
      });
      return;
    } catch (err) {
      console.warn("KaTeX render error:", err);
    }
  }
  element.innerText = latexCode;
}

/**
 * Renderiza texto mixto que contiene fórmulas matemáticas en LaTeX delimitadas por $...$ o $$...$$.
 * Soporta renderMathInElement (KaTeX contrib) y dispone de un fallback regex nativo
 * con katex.renderToString() que garantiza visualización matemática universal.
 */
function renderMixedLatex(element, text) {
  if (!element) return;
  if (!text) {
    element.innerHTML = "";
    return;
  }

  // Tokenización matemática directa con katex.renderToString
  if (window.katex && window.katex.renderToString) {
    try {
      const parts = text.split(/(\$\$[\s\S]*?\$\$|\$[\s\S]*?\$)/g);
      let html = "";
      for (const part of parts) {
        if (part.startsWith("$$") && part.endsWith("$$") && part.length >= 4) {
          const math = part.slice(2, -2).trim();
          html += katex.renderToString(math, { displayMode: true, throwOnError: false });
        } else if (part.startsWith("$") && part.endsWith("$") && part.length >= 2) {
          const math = part.slice(1, -1).trim();
          html += katex.renderToString(math, { displayMode: false, throwOnError: false });
        } else {
          const safe = part
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/\n/g, "<br>");
          html += safe;
        }
      }
      element.innerHTML = html;
      return;
    } catch (e) {
      console.warn("KaTeX mixed render warning:", e);
    }
  }

  // Fallback si KaTeX no está disponible
  element.innerText = text;
}

/* ==========================================================================
   2. Control de Tema (Modo Claro por Defecto con Toggle a Modo Oscuro)
   ========================================================================== */
function inicializarTema() {
  const savedTheme = localStorage.getItem("algebra_theme") || "light";
  aplicarTema(savedTheme);

  const btnToggle = document.getElementById("btn-theme-toggle");
  if (btnToggle) {
    btnToggle.addEventListener("click", () => {
      const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
      const newTheme = currentTheme === "light" ? "dark" : "light";
      aplicarTema(newTheme);
      localStorage.setItem("algebra_theme", newTheme);
    });
  }
}

function aplicarTema(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  const btnToggle = document.getElementById("btn-theme-toggle");
  const textEl = document.getElementById("theme-btn-text");
  const iconContainer = btnToggle ? btnToggle.querySelector(".icon") : null;
  if (btnToggle && textEl && iconContainer) {
    if (theme === "dark") {
      iconContainer.innerHTML = '<i data-lucide="sun"></i>';
      textEl.innerText = "Modo Claro";
    } else {
      iconContainer.innerHTML = '<i data-lucide="moon"></i>';
      textEl.innerText = "Modo Oscuro";
    }
  }
  refrescarIconosLucide();
}

/* ==========================================================================
   3. Navegación por Pestañas
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
      refrescarIconosLucide();
    });
  });
}

function mostrarToast(mensaje, duracion = 3000) {
  const toast = document.getElementById("notification-toast");
  const msgEl = document.getElementById("toast-message");
  if (!toast || !msgEl) return;
  msgEl.innerHTML = `<i data-lucide="check-circle-2" class="toast-icon"></i> <span>${mensaje}</span>`;
  refrescarIconosLucide();
  toast.classList.remove("hidden");
  setTimeout(() => {
    toast.classList.add("hidden");
  }, duracion);
}

// =============================================================================
// =============================================================================
// APARTADO 1: OPERACIONES CON VECTORES EN R^n
// Operaciones: Suma (u + v), Resta (u - v), Producto por Escalar (c · u),
// Producto Punto Euclídeo (u · v) y Norma / Magnitud Vectorial (||u||, ||u||²)
// =============================================================================
// =============================================================================
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
    // Casilla u_i
    const wrapU = document.createElement("div");
    wrapU.className = "cell-wrapper";
    const subU = document.createElement("span");
    subU.className = "cell-sublabel";
    subU.innerText = `u${i + 1}`;
    const inpU = document.createElement("input");
    inpU.type = "text";
    inpU.className = "cell-input";
    inpU.id = `vec-u-${i}`;
    inpU.value = (i + 1).toString();
    wrapU.appendChild(subU);
    wrapU.appendChild(inpU);
    contU.appendChild(wrapU);

    // Casilla v_i
    const wrapV = document.createElement("div");
    wrapV.className = "cell-wrapper";
    const subV = document.createElement("span");
    subV.className = "cell-sublabel";
    subV.innerText = `v${i + 1}`;
    const inpV = document.createElement("input");
    inpV.type = "text";
    inpV.className = "cell-input";
    inpV.id = `vec-v-${i}`;
    inpV.value = (vectorDim - i).toString();
    wrapV.appendChild(subV);
    wrapV.appendChild(inpV);
    contV.appendChild(wrapV);
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

function limpiarModuloVectores() {
  for (let i = 0; i < vectorDim; i++) {
    const elU = document.getElementById(`vec-u-${i}`);
    const elV = document.getElementById(`vec-v-${i}`);
    if (elU) elU.value = "0";
    if (elV) elV.value = "0";
  }
  const elC = document.getElementById("vec-scalar-c");
  if (elC) elC.value = "1";

  const badge = document.getElementById("vec-badge-status");
  const resultBox = document.getElementById("vec-result-content");
  if (badge) {
    badge.className = "badge";
    badge.innerText = "Casillas limpias";
  }
  if (resultBox) {
    resultBox.innerHTML = '<p class="placeholder-text">Seleccione una operación vectorial para ver la expresión matemática y su desglose algebraico.</p>';
  }
  mostrarToast("Casillas de vectores limpiadas.");
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
  } else if (tipo === 2) {
    input.value = 4;
    actualizarEntradasVectores();
    const uVals = ["1/2", "-3/4", "1", "5/2"];
    const vVals = ["3/2", "1/4", "-2", "0"];
    uVals.forEach((val, i) => document.getElementById(`vec-u-${i}`).value = val);
    vVals.forEach((val, i) => document.getElementById(`vec-v-${i}`).value = val);
    document.getElementById("vec-scalar-c").value = "-2";
  } else if (tipo === 20) {
    input.value = 20;
    actualizarEntradasVectores();
    for (let i = 0; i < 20; i++) {
      document.getElementById(`vec-u-${i}`).value = (i + 1).toString();
      document.getElementById(`vec-v-${i}`).value = (20 - i).toString();
    }
    document.getElementById("vec-scalar-c").value = "2";
    mostrarToast("Cargado ejemplo responsivo con dimensión n = 20");
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

    // Guardar para permitir cambio de notación en tiempo real
    ultimoCalculoVector = { data, u, v, c, operacion };
    renderizarResultadoVectorUI(ultimoCalculoVector);
  } catch (err) {
    badge.className = "badge badge-error";
    badge.innerText = "Error";
    resultBox.innerHTML = `
      <div class="latex-equation-card" style="border-color: rgba(225,29,72,0.4);">
        <div class="latex-header" style="color:var(--accent-rose);">Error:</div>
        <p>${err.message}</p>
      </div>
    `;
  }
}

function renderizarResultadoVectorUI(calc) {
  const { data, u, v, c, operacion } = calc;
  const resultBox = document.getElementById("vec-result-content");
  if (!resultBox) return;

  // Desglose de componentes del resultado
  const wRaw = data.resultado_str.replace(/[()]/g, "").split(",").map(x => x.trim());

  // Construcción de la Expresión Matemática en formato columna
  let latexStr = "";
  if (operacion === "suma") {
    latexStr = `\\vec{u} + \\vec{v} = ${vectorToLatexCol(u)} + ${vectorToLatexCol(v)} = ${vectorToLatexCol(wRaw)}`;
  } else if (operacion === "resta") {
    latexStr = `\\vec{u} - \\vec{v} = ${vectorToLatexCol(u)} - ${vectorToLatexCol(v)} = ${vectorToLatexCol(wRaw)}`;
  } else if (operacion === "escalar_u") {
    const cLatex = formatLatexFrac(c);
    latexStr = `${cLatex} \\cdot \\vec{u} = ${cLatex} ${vectorToLatexCol(u)} = ${vectorToLatexCol(wRaw)}`;
  } else if (operacion === "producto_punto") {
    latexStr = `\\vec{u} \\cdot \\vec{v} = ${vectorToLatexRow(u)} \\cdot ${vectorToLatexCol(v)} = ${formatLatexFrac(data.resultado_str)}`;
  }

  resultBox.innerHTML = `
    <div class="latex-equation-card">
      <div class="latex-header">${data.titulo_operacion}</div>
      <div id="vec-latex-target" class="latex-display-box"></div>
      <div class="result-explanation" id="vec-explanation" style="white-space: pre-line; margin-top: 0.5rem;"></div>
    </div>
  `;

  const targetEl = document.getElementById("vec-latex-target");
  renderLatexElement(targetEl, latexStr);

  const expEl = document.getElementById("vec-explanation");
  if (expEl && data.explicacion_teorica) {
    renderMixedLatex(expEl, data.explicacion_teorica);
  }

  if (data.desglose_componentes && data.desglose_componentes.length > 0) {
    const stepsWrapper = document.createElement("div");
    stepsWrapper.className = "steps-container";
    stepsWrapper.innerHTML = `<h4>Desglose componente a componente:</h4>`;
    data.desglose_componentes.forEach(paso => {
      const item = document.createElement("div");
      item.className = "step-item";
      const desc = document.createElement("div");
      desc.className = "step-item-desc";
      renderMixedLatex(desc, paso);
      item.appendChild(desc);
      stepsWrapper.appendChild(item);
    });
    resultBox.appendChild(stepsWrapper);
  }
  refrescarIconosLucide();
}

// =============================================================================
// =============================================================================
// APARTADO 2: EVALUACIÓN DE COMBINACIÓN LINEAL Y SUBESPACIOS
// Problema: c₁·v₁ + c₂·v₂ + ... + cₖ·vₖ = b en R^n
// Solucionador: Eliminación Gaussiana, Rouché-Capelli (SCD / SCI / SI) y comprobación
// =============================================================================
// =============================================================================
let combN = 2;
let combK = 2;

function inicializarModuloCombinacion() {
  actualizarEntradasCombinacion();
  cargarEjemploCombinacion(1);
}

function cambiarDimCombN(delta) {
  const el = document.getElementById("comb-dim-n");
  let val = Math.max(1, Math.min(15, (parseInt(el.value, 10) || 2) + delta));
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
  combN = parseInt(document.getElementById("comb-dim-n").value, 10) || 2;
  combK = parseInt(document.getElementById("comb-num-k").value, 10) || 2;

  const listContainer = document.getElementById("comb-vectors-list");
  listContainer.innerHTML = "";

  for (let j = 0; j < combK; j++) {
    const block = document.createElement("div");
    block.className = "vec-block";
    block.style.marginBottom = "0.75rem";
    block.innerHTML = `
      <div class="vec-label-row">
        <span class="vec-label">Vector v_${j + 1} en R^${combN}:</span>
      </div>
    `;

    const row = document.createElement("div");
    row.className = "cells-row cells-wrap";
    for (let i = 0; i < combN; i++) {
      const wrap = document.createElement("div");
      wrap.className = "cell-wrapper";
      const sub = document.createElement("span");
      sub.className = "cell-sublabel";
      sub.innerText = `c_${i + 1}`;
      const inp = document.createElement("input");
      inp.type = "text";
      inp.className = "cell-input";
      inp.id = `comb-v-${j}-${i}`;
      inp.value = (i === j ? "1" : "0");
      wrap.appendChild(sub);
      wrap.appendChild(inp);
      row.appendChild(wrap);
    }
    block.appendChild(row);
    listContainer.appendChild(block);
  }

  const targetContainer = document.getElementById("comb-target-inputs");
  targetContainer.innerHTML = "";
  for (let i = 0; i < combN; i++) {
    const wrap = document.createElement("div");
    wrap.className = "cell-wrapper";
    const sub = document.createElement("span");
    sub.className = "cell-sublabel";
    sub.innerText = `b_${i + 1}`;
    const inp = document.createElement("input");
    inp.type = "text";
    inp.className = "cell-input";
    inp.id = `comb-b-${i}`;
    inp.value = "1";
    wrap.appendChild(sub);
    wrap.appendChild(inp);
    targetContainer.appendChild(wrap);
  }
}

function limpiarModuloCombinacion() {
  for (let j = 0; j < combK; j++) {
    for (let i = 0; i < combN; i++) {
      const el = document.getElementById(`comb-v-${j}-${i}`);
      if (el) el.value = "0";
    }
  }
  for (let i = 0; i < combN; i++) {
    const elB = document.getElementById(`comb-b-${i}`);
    if (elB) elB.value = "0";
  }
  const badge = document.getElementById("comb-badge-status");
  const resultBox = document.getElementById("comb-result-content");
  if (badge) {
    badge.className = "badge";
    badge.innerText = "Pendiente";
  }
  if (resultBox) {
    resultBox.innerHTML = '<p class="placeholder-text">Configure los vectores y presione "Evaluar Combinación Lineal".</p>';
  }
  mostrarToast("Casillas de combinación lineal limpiadas.");
}

function cargarEjemploCombinacion(caso) {
  if (caso === 1) {
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
    document.getElementById("comb-b-2").value = "7";
  } else {
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

    // Guardar estado para reactividad al alternar modo de notación
    ultimoCalculoCombinacion = { data, vectores, b };
    renderizarResultadoCombinacionUI(ultimoCalculoCombinacion);
  } catch (err) {
    badge.className = "badge badge-error";
    badge.innerText = "Error";
    resultBox.innerHTML = `
      <div class="latex-equation-card" style="border-color: rgba(225,29,72,0.4);">
        <div class="latex-header" style="color:var(--accent-rose);">Error:</div>
        <p>${err.message}</p>
      </div>
    `;
  }
}

function renderizarResultadoCombinacionUI(calc) {
  const { data, vectores, b } = calc;
  const resultBox = document.getElementById("comb-result-content");
  if (!resultBox) return;

  const k = vectores.length;
  const n = b.length;
  const usarTranspuesta = (notacionCombinacion === "transpuesta");

  function vectorFmt(v) {
    if (usarTranspuesta) {
      return `(${v.map(formatLatexFrac).join(",\\; ")})^T`;
    }
    return vectorToLatexCol(v);
  }

  // Generación de expresión matemática adaptativa y multilínea (sin scroll horizontal)
  let latexComb = "";
  if (data.es_combinacion) {
    const terminos = [];
    for (let j = 0; j < k; j++) {
      const cCoeff = formatScalarCoeff(data.escalares_vector[j]);
      terminos.push(`${cCoeff} ${vectorFmt(vectores[j])}`);
    }

    if (k <= 3 && usarTranspuesta && n <= 4) {
      // Para pocos vectores en transpuesta, una sola línea es limpia y sin scroll
      latexComb = `\\vec{b} = \\sum_{j=1}^{${k}} c_j \\vec{v}_j \\implies ${vectorFmt(b)} = ${terminos.join(" + ")}`;
    } else {
      // Chunking multilínea: en transpuesta 3 por línea (o 2 si n > 5), en columna 2 por línea
      const chunkSize = usarTranspuesta ? (n > 5 ? 2 : 3) : 2;
      const chunks = [];
      for (let i = 0; i < terminos.length; i += chunkSize) {
        chunks.push(terminos.slice(i, i + chunkSize));
      }

      const lineasAligned = [];
      lineasAligned.push(`\\vec{b} &= \\sum_{j=1}^{${k}} c_j \\vec{v}_j`);
      lineasAligned.push(`${vectorFmt(b)} &= ${chunks[0].join(" + ")}`);
      for (let c = 1; c < chunks.length; c++) {
        lineasAligned.push(`&\\quad + ${chunks[c].join(" + ")}`);
      }

      latexComb = `\\begin{aligned}\n${lineasAligned.join(" \\\\[6pt]\n")}\n\\end{aligned}`;
    }
  } else {
    latexComb = `\\vec{b} = ${vectorFmt(b)} \\notin \\operatorname{gen}\\left\\{ \\vec{v}_1, \\dots, \\vec{v}_${k} \\right\\}`;
  }

  // Resumen compacto de escalares
  let scalarsHtml = "";
  if (data.es_combinacion && data.escalares_vector) {
    const tipoTexto = (data.tipo_solucion === "UNICA") ? "Solución Única" : "Solución Paramétrica (Infinitas Soluciones)";
    scalarsHtml = `
      <div class="latex-scalars-summary">
        <div style="font-size: 0.78rem; font-weight: 700; color: var(--accent-cyan); margin-bottom: 0.35rem; text-transform: uppercase;">
          Escalares de la Combinación (${tipoTexto}):
        </div>
        <div id="comb-scalars-latex" style="overflow-x: auto; padding: 0.2rem 0;"></div>
      </div>
    `;
  }

  resultBox.innerHTML = `
    <div class="latex-equation-card">
      <div class="notation-bar">
        <span class="latex-header">Ecuación Vectorial</span>
        <div class="notation-toggle-group">
          <button type="button" class="btn-not-toggle ${notacionCombinacion==='transpuesta'?'active':''}" onclick="cambiarNotacionCombinacion('transpuesta')" title="Notación matemática ( )ᵀ compacta">Transpuesta ( )ᵀ</button>
          <button type="button" class="btn-not-toggle ${notacionCombinacion==='columna'?'active':''}" onclick="cambiarNotacionCombinacion('columna')" title="Notación vertical en columnas">Columna ( )</button>
        </div>
      </div>
      ${scalarsHtml}
      <div id="comb-latex-target" class="latex-display-box"></div>
      <div class="result-explanation" id="comb-explanation" style="white-space: pre-line; margin-top: 0.5rem;"></div>
    </div>
  `;

  // Renderizar la ecuación principal
  const targetEl = document.getElementById("comb-latex-target");
  renderLatexElement(targetEl, latexComb);

  // Renderizar la justificación teórica con soporte LaTeX
  const expEl = document.getElementById("comb-explanation");
  if (expEl && data.justificacion_teorica) {
    renderMixedLatex(expEl, data.justificacion_teorica);
  }

  // Renderizar los escalares
  if (data.es_combinacion && data.escalares_vector) {
    const scalarsTarget = document.getElementById("comb-scalars-latex");
    if (scalarsTarget) {
      const scalarsLatex = data.escalares_vector.map((val, idx) => `c_{${idx + 1}} = ${formatLatexFrac(val)}`).join(",\\quad ");
      renderLatexElement(scalarsTarget, scalarsLatex, false);
    }
  }

  // Desglose de Comprobación
  if (data.comprobacion && data.comprobacion.length > 0) {
    const verifEl = document.createElement("div");
    verifEl.className = "verification-box";
    verifEl.innerHTML = `<h4>Comprobación Componente por Componente:</h4>`;
    data.comprobacion.forEach(c => {
      const row = document.createElement("div");
      renderMixedLatex(row, c);
      verifEl.appendChild(row);
    });
    resultBox.appendChild(verifEl);
  }

  // Pasos de Gauss-Jordan
  if (data.pasos && data.pasos.length > 0) {
    const stepsWrapper = document.createElement("div");
    stepsWrapper.className = "steps-container";
    stepsWrapper.innerHTML = `<h4>Pasos de Reducción por Filas (Gauss-Jordan):</h4>`;
    data.pasos.forEach(p => {
      const stepItem = document.createElement("div");
      stepItem.className = "step-item";
      const t = document.createElement("div");
      t.className = "step-item-title";
      renderMixedLatex(t, `Paso ${p.step_number}: ${p.title}`);
      const d = document.createElement("div");
      d.className = "step-item-desc";
      renderMixedLatex(d, p.description);
      stepItem.appendChild(t);
      stepItem.appendChild(d);
      stepsWrapper.appendChild(stepItem);
    });
    resultBox.appendChild(stepsWrapper);
  }
  refrescarIconosLucide();
}

// =============================================================================
// =============================================================================
// APARTADO 3: OPERACIONES MATRICIALES BÁSICAS
// Operaciones: Suma (A + B), Resta (A - B), Producto por Escalar (k · A),
// Multiplicación Matricial (A · B) y Transpuesta de Matrices (A^T, B^T)
// =============================================================================
// =============================================================================
function inicializarModuloMatrices() {
  renderizarMatrizA();
  renderizarMatrizB();
  cargarEjemploMatrices(1);
}

function cambiarDimMatA(dm, dn) {
  const elM = document.getElementById("mat-a-m");
  const elN = document.getElementById("mat-a-n");
  if (dm !== 0) elM.value = Math.max(1, Math.min(8, (parseInt(elM.value, 10) || 2) + dm));
  if (dn !== 0) elN.value = Math.max(1, Math.min(8, (parseInt(elN.value, 10) || 3) + dn));
  renderizarMatrizA();
}

function cambiarDimMatB(dr, dp) {
  const elR = document.getElementById("mat-b-r");
  const elP = document.getElementById("mat-b-r_col");
  if (dr !== 0) elR.value = Math.max(1, Math.min(8, (parseInt(elR.value, 10) || 3) + dr));
  if (dp !== 0) elP.value = Math.max(1, Math.min(8, (parseInt(elP.value, 10) || 2) + dp));
  renderizarMatrizB();
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
  const p = parseInt(document.getElementById("mat-b-r_col").value, 10) || 2;
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

function limpiarModuloMatrices() {
  const m = parseInt(document.getElementById("mat-a-m").value, 10) || 2;
  const n = parseInt(document.getElementById("mat-a-n").value, 10) || 3;
  const r = parseInt(document.getElementById("mat-b-r").value, 10) || 3;
  const p = parseInt(document.getElementById("mat-b-r_col").value, 10) || 2;

  for (let i = 0; i < m; i++) {
    for (let j = 0; j < n; j++) {
      const el = document.getElementById(`mat-a-${i}-${j}`);
      if (el) el.value = "0";
    }
  }
  for (let i = 0; i < r; i++) {
    for (let j = 0; j < p; j++) {
      const el = document.getElementById(`mat-b-${i}-${j}`);
      if (el) el.value = "0";
    }
  }
  const elK = document.getElementById("mat-scalar-k");
  if (elK) elK.value = "1";

  const badge = document.getElementById("mat-badge-status");
  const resultBox = document.getElementById("mat-result-content");
  if (badge) {
    badge.className = "badge";
    badge.innerText = "Casillas limpias";
  }
  if (resultBox) {
    resultBox.innerHTML = '<p class="placeholder-text">Seleccione una operación matricial para calcular.</p>';
  }
  mostrarToast("Matrices A y B limpiadas.");
}

function cargarEjemploMatrices(tipo) {
  if (tipo === 1) {
    document.getElementById("mat-a-m").value = 2;
    document.getElementById("mat-a-n").value = 3;
    document.getElementById("mat-b-r").value = 3;
    document.getElementById("mat-b-r_col").value = 2;
    renderizarMatrizA();
    renderizarMatrizB();
    const aVals = [["1", "2", "3"], ["4", "5", "6"]];
    const bVals = [["7", "8"], ["9", "1"], ["2", "3"]];
    for (let i = 0; i < 2; i++) for (let j = 0; j < 3; j++) document.getElementById(`mat-a-${i}-${j}`).value = aVals[i][j];
    for (let i = 0; i < 3; i++) for (let j = 0; j < 2; j++) document.getElementById(`mat-b-${i}-${j}`).value = bVals[i][j];
  } else {
    document.getElementById("mat-a-m").value = 3;
    document.getElementById("mat-a-n").value = 3;
    document.getElementById("mat-b-r").value = 3;
    document.getElementById("mat-b-r_col").value = 3;
    renderizarMatrizA();
    renderizarMatrizB();
  }
}

async function operarMatrices(operacion) {
  const m = parseInt(document.getElementById("mat-a-m").value, 10);
  const n = parseInt(document.getElementById("mat-a-n").value, 10);
  const r = parseInt(document.getElementById("mat-b-r").value, 10);
  const p = parseInt(document.getElementById("mat-b-r_col").value, 10);

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

    // Formulación LaTeX de matrices con la matriz resultante
    let latexMat = "";
    const C = data.matriz_resultado;
    if (operacion === "suma") {
      latexMat = `A + B = ${matrixToLatex(A)} + ${matrixToLatex(B)} = ${matrixToLatex(C)}`;
    } else if (operacion === "resta") {
      latexMat = `A - B = ${matrixToLatex(A)} - ${matrixToLatex(B)} = ${matrixToLatex(C)}`;
    } else if (operacion === "multiplicacion") {
      latexMat = `A \\cdot B = ${matrixToLatex(A)} \\cdot ${matrixToLatex(B)} = ${matrixToLatex(C)}`;
    } else if (operacion === "escalar_a") {
      latexMat = `${formatLatexFrac(k)} \\cdot A = ${formatLatexFrac(k)} ${matrixToLatex(A)} = ${matrixToLatex(C)}`;
    } else if (operacion === "transpuesta_a") {
      latexMat = `A^T = ${matrixToLatex(A)}^T = ${matrixToLatex(C)}`;
    } else if (operacion === "transpuesta_b") {
      latexMat = `B^T = ${matrixToLatex(B)}^T = ${matrixToLatex(C)}`;
    }

    resultBox.innerHTML = `
      <div class="latex-equation-card">
        <div class="latex-header">${data.titulo_operacion}</div>
        <div id="mat-latex-target" class="latex-display-box"></div>
        <div class="latex-header" style="margin-top: 0.85rem;">Matriz Resultante:</div>
        <pre class="result-formula" style="font-size: 0.95rem; color: var(--text-main); font-family: 'JetBrains Mono', monospace; overflow-x: auto;">${data.matriz_formateada}</pre>
        <div class="result-explanation" id="mat-explanation" style="white-space: pre-line; margin-top: 0.5rem;"></div>
      </div>
    `;

    const targetEl = document.getElementById("mat-latex-target");
    renderLatexElement(targetEl, latexMat);

    const expEl = document.getElementById("mat-explanation");
    if (expEl && data.explicacion_teorica) {
      renderMixedLatex(expEl, data.explicacion_teorica);
    }

    if (data.pasos_multiplicacion && data.pasos_multiplicacion.length > 0) {
      const stepsWrapper = document.createElement("div");
      stepsWrapper.className = "steps-container";
      const h4 = document.createElement("h4");
      renderMixedLatex(h4, "Cálculo de cada entrada $c_{ij}$ (Producto Renglón · Columna):");
      stepsWrapper.appendChild(h4);
      data.pasos_multiplicacion.forEach(paso => {
        const item = document.createElement("div");
        item.className = "step-item";
        const desc = document.createElement("div");
        desc.className = "step-item-desc";
        renderMixedLatex(desc, `$${paso}$`);
        item.appendChild(desc);
        stepsWrapper.appendChild(item);
      });
      resultBox.appendChild(stepsWrapper);
    }

    // -------------------------------------------------------------------------
    // SUB-APARTADO: RESULTADOS Y PROPIEDADES DE LA TRANSPUESTA (A^T o B^T)
    // Muestra: Análisis dimensional, simetría, traza y mapeo de filas a columnas
    // -------------------------------------------------------------------------
    if (data.propiedades && data.propiedades.length > 0) {
      const propsWrapper = document.createElement("div");
      propsWrapper.className = "steps-container";
      propsWrapper.style.marginTop = "0.75rem";
      const h4 = document.createElement("h4");
      renderMixedLatex(h4, "Propiedades Algebraicas de la Transpuesta:");
      propsWrapper.appendChild(h4);
      data.propiedades.forEach(prop => {
        const item = document.createElement("div");
        item.className = "step-item";
        const desc = document.createElement("div");
        desc.className = "step-item-desc";
        renderMixedLatex(desc, `$\\bullet\\quad$ ${prop}`);
        item.appendChild(desc);
        propsWrapper.appendChild(item);
      });
      resultBox.appendChild(propsWrapper);
    }

    if (data.pasos_mapeo && data.pasos_mapeo.length > 0) {
      const mapWrapper = document.createElement("div");
      mapWrapper.className = "steps-container";
      mapWrapper.style.marginTop = "0.75rem";
      const h4 = document.createElement("h4");
      renderMixedLatex(h4, "Mapeo Fila $\\rightarrow$ Columna $(A^T)_{ji} = a_{ij}$:");
      mapWrapper.appendChild(h4);
      data.pasos_mapeo.forEach(mPaso => {
        const item = document.createElement("div");
        item.className = "step-item";
        const desc = document.createElement("div");
        desc.className = "step-item-desc";
        renderMixedLatex(desc, `$${mPaso}$`);
        item.appendChild(desc);
        mapWrapper.appendChild(item);
      });
      resultBox.appendChild(mapWrapper);
    }
    refrescarIconosLucide();
  } catch (err) {
    badge.className = "badge badge-error";
    badge.innerText = "Error";
    resultBox.innerHTML = `
      <div class="latex-equation-card" style="border-color: rgba(225,29,72,0.4);">
        <div class="latex-header" style="color:var(--accent-rose);">Error Dimensional:</div>
        <p>${err.message}</p>
      </div>
    `;
  }
}

// =============================================================================
// =============================================================================
// APARTADO 4: INVERSA DE UNA MATRIZ A⁻¹
// Algoritmos: Reducción por Renglones [A | I_n] ~ [I_n | A⁻¹] (Gauss / Gauss-Jordan)
// Teoremas: Inversión 2×2, Detección de Singularidad y Doble Verificación A·A⁻¹ = I_n
// =============================================================================
// =============================================================================
let invN = 2;

function inicializarModuloInversa() {
  renderizarMatrizInversaInput();
  cargarEjemploInversa(1);
}

function cambiarDimInversa(delta) {
  const el = document.getElementById("inv-dim-n");
  let val = Math.max(2, Math.min(6, (parseInt(el.value, 10) || 2) + delta));
  el.value = val;
  invN = val;
  renderizarMatrizInversaInput();
}

function renderizarMatrizInversaInput() {
  const el = document.getElementById("inv-dim-n");
  invN = parseInt(el.value, 10) || 2;
  const grid = document.getElementById("inv-matrix-grid");
  if (!grid) return;
  grid.style.gridTemplateColumns = `repeat(${invN}, auto)`;
  grid.innerHTML = "";

  for (let i = 0; i < invN; i++) {
    for (let j = 0; j < invN; j++) {
      const inp = document.createElement("input");
      inp.type = "text";
      inp.className = "cell-input";
      inp.id = `inv-a-${i}-${j}`;
      inp.value = i === j ? "1" : "0";
      grid.appendChild(inp);
    }
  }
}

function obtenerMatrizInversaValores() {
  const M = [];
  for (let i = 0; i < invN; i++) {
    const fila = [];
    for (let j = 0; j < invN; j++) {
      const el = document.getElementById(`inv-a-${i}-${j}`);
      fila.push(el ? el.value.trim() || "0" : "0");
    }
    M.push(fila);
  }
  return M;
}

function limpiarModuloInversa() {
  for (let i = 0; i < invN; i++) {
    for (let j = 0; j < invN; j++) {
      const el = document.getElementById(`inv-a-${i}-${j}`);
      if (el) el.value = "0";
    }
  }
  const badge = document.getElementById("inv-badge-status");
  const resultBox = document.getElementById("inv-result-content");
  if (badge) {
    badge.className = "badge";
    badge.innerText = "Casillas limpias";
  }
  if (resultBox) {
    resultBox.innerHTML = '<p class="placeholder-text">Ingrese una matriz cuadrada y presione "Calcular Inversa A⁻¹".</p>';
  }
  mostrarToast("Matriz A limpiada.");
}

function cargarEjemploInversa(tipo) {
  if (tipo === 1) {
    // Ejemplo 1: 2x2
    // A = [[2, 5], [-3, -7]]
    document.getElementById("inv-dim-n").value = 2;
    invN = 2;
    renderizarMatrizInversaInput();
    const vals = [["2", "5"], ["-3", "-7"]];
    for (let i = 0; i < 2; i++) {
      for (let j = 0; j < 2; j++) {
        const el = document.getElementById(`inv-a-${i}-${j}`);
        if (el) el.value = vals[i][j];
      }
    }
    mostrarToast("Ejemplo 1 (2x2) cargado.");
  } else if (tipo === 2) {
    // Ejemplo 2: 3x3
    // A = [[0, 1, 2], [1, 0, 3], [4, -3, 8]]
    document.getElementById("inv-dim-n").value = 3;
    invN = 3;
    renderizarMatrizInversaInput();
    const vals = [
      ["0", "1", "2"],
      ["1", "0", "3"],
      ["4", "-3", "8"]
    ];
    for (let i = 0; i < 3; i++) {
      for (let j = 0; j < 3; j++) {
        const el = document.getElementById(`inv-a-${i}-${j}`);
        if (el) el.value = vals[i][j];
      }
    }
    mostrarToast("Ejemplo 2 (3x3) cargado.");
  } else if (tipo === 3) {
    // Ejemplo 3: 3x3
    // A = [[1, 2, 3], [0, 1, 4], [5, 6, 0]]
    document.getElementById("inv-dim-n").value = 3;
    invN = 3;
    renderizarMatrizInversaInput();
    const vals = [
      ["1", "2", "3"],
      ["0", "1", "4"],
      ["5", "6", "0"]
    ];
    for (let i = 0; i < 3; i++) {
      for (let j = 0; j < 3; j++) {
        const el = document.getElementById(`inv-a-${i}-${j}`);
        if (el) el.value = vals[i][j];
      }
    }
    mostrarToast("Ejemplo 3 (3x3) cargado.");
  } else if (tipo === 4) {
    // Ejemplo 4: Singular
    // A = [[2, 3, 4], [2, 3, 4], [2, 3, 4]]
    document.getElementById("inv-dim-n").value = 3;
    invN = 3;
    renderizarMatrizInversaInput();
    const vals = [
      ["2", "3", "4"],
      ["2", "3", "4"],
      ["2", "3", "4"]
    ];
    for (let i = 0; i < 3; i++) {
      for (let j = 0; j < 3; j++) {
        const el = document.getElementById(`inv-a-${i}-${j}`);
        if (el) el.value = vals[i][j];
      }
    }
    mostrarToast("Ejemplo 4 (Singular) cargado.");
  }
}

async function calcularInversaUI() {
  const badge = document.getElementById("inv-badge-status");
  const resultBox = document.getElementById("inv-result-content");
  badge.className = "badge badge-dim";
  badge.innerText = "Calculando...";

  const A = obtenerMatrizInversaValores();
  const metodoInput = document.querySelector('input[name="inv-method"]:checked');
  const metodo = metodoInput ? metodoInput.value : "gauss_jordan";

  try {
    const res = await fetch("/api/matrices/inversa", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ A, metodo })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Error al calcular la matriz inversa");

    if (data.es_invertible) {
      badge.className = "badge badge-success";
      badge.innerText = "Invertible (No Singular)";
    } else {
      badge.className = "badge badge-error";
      badge.innerText = "Matriz Singular (No Invertible)";
    }

    let latexPrincipal = "";
    if (data.es_invertible && data.matriz_inversa) {
      latexPrincipal = `A^{-1} = ${matrixToLatex(data.matriz_inversa)}`;
    } else {
      latexPrincipal = `\\nexists \\; A^{-1} \\quad (\\det(A) = 0 \\text{ o } \\mathrm{rg}(A) < ${data.orden_n})`;
    }

    let htmlContenido = `
      <div class="latex-equation-card">
        <div class="latex-header">${data.es_invertible ? "Matriz Inversa Calculada A⁻¹:" : "Dictamen de Singularidad:"}</div>
        <div id="inv-latex-target" class="latex-display-box"></div>
    `;

    // Si es matriz 2x2, mostrar el Teorema 2x2
    if (data.orden_n === 2 && data.determinante_2x2 !== null) {
      htmlContenido += `
        <div class="verification-box" style="margin-top: 0.85rem; background: rgba(2, 132, 199, 0.05); border-color: rgba(2, 132, 199, 0.2);">
          <h4 style="color: var(--accent-cyan);">Teorema de Inversión 2 × 2:</h4>
          <div id="inv-latex-teorema-2x2"></div>
        </div>
      `;
    }

    // Diagnóstico teórico / Algoritmo
    if (data.mensaje_diagnostico) {
      htmlContenido += `
        <div class="result-explanation" id="inv-diagnostic" style="white-space: pre-line; margin-top: 0.75rem;"></div>
      `;
    }

    htmlContenido += `</div>`; // fin latex-equation-card
    resultBox.innerHTML = htmlContenido;

    // Render KaTeX principal
    renderLatexElement(document.getElementById("inv-latex-target"), latexPrincipal);

    // Render Teorema 2x2 si aplica
    if (data.orden_n === 2 && data.determinante_2x2 !== null) {
      const el2x2 = document.getElementById("inv-latex-teorema-2x2");
      if (el2x2) {
        const detLatex = formatLatexFrac(data.determinante_2x2);
        const a_val = formatLatexFrac(A[0][0]);
        const b_val = formatLatexFrac(A[0][1]);
        const c_val = formatLatexFrac(A[1][0]);
        const d_val = formatLatexFrac(A[1][1]);
        const neg_b = formatLatexFrac(b_val.startsWith("-") ? b_val.slice(1) : (b_val === "0" ? "0" : "-" + b_val));
        const neg_c = formatLatexFrac(c_val.startsWith("-") ? c_val.slice(1) : (c_val === "0" ? "0" : "-" + c_val));
        const form2x2 = detLatex === "0" 
          ? `\\det(A) = ad - bc = (${a_val})(${d_val}) - (${b_val})(${c_val}) = 0 \\implies \\text{Matriz singular (no invertible)}`
          : `\\det(A) = ad - bc = (${a_val})(${d_val}) - (${b_val})(${c_val}) = ${detLatex} \\neq 0 \\implies A^{-1} = \\frac{1}{${detLatex}} \\begin{pmatrix} ${d_val} & ${neg_b} \\\\ ${neg_c} & ${a_val} \\end{pmatrix}`;
        renderLatexElement(el2x2, form2x2);
      }
    }

    // Render diagnóstico teórico
    const diagEl = document.getElementById("inv-diagnostic");
    if (diagEl && data.mensaje_diagnostico) {
      renderMixedLatex(diagEl, data.mensaje_diagnostico);
    }

    // Verificación Dual A·A⁻¹ = I y A⁻¹·A = I
    if (data.es_invertible) {
      const verifContainer = document.createElement("div");
      verifContainer.className = "verification-box";
      verifContainer.style.marginTop = "1rem";
      verifContainer.innerHTML = `<h4>Verificación Algebraica Dual:</h4>`;
      
      const v1Title = document.createElement("div");
      v1Title.style.fontWeight = "600";
      v1Title.style.marginTop = "0.4rem";
      renderMixedLatex(v1Title, "1. Comprobación directa: $A \\cdot A^{-1} = I_{" + data.orden_n + "}$");
      verifContainer.appendChild(v1Title);

      (data.verificacion_A_por_Ainv || []).forEach(v => {
        const row = document.createElement("div");
        row.style.margin = "0.25rem 0";
        row.style.lineHeight = "1.6";
        renderMixedLatex(row, v);
        verifContainer.appendChild(row);
      });

      const v2Title = document.createElement("div");
      v2Title.style.fontWeight = "600";
      v2Title.style.marginTop = "0.6rem";
      renderMixedLatex(v2Title, "2. Comprobación conmutativa: $A^{-1} \\cdot A = I_{" + data.orden_n + "}$");
      verifContainer.appendChild(v2Title);

      (data.verificacion_Ainv_por_A || []).forEach(v => {
        const row = document.createElement("div");
        row.style.margin = "0.25rem 0";
        row.style.lineHeight = "1.6";
        renderMixedLatex(row, v);
        verifContainer.appendChild(row);
      });

      resultBox.appendChild(verifContainer);
    }

    // Pasos de Reducción por Renglones de la Matriz Aumentada [A | I_n]
    if (data.pasos && data.pasos.length > 0) {
      const stepsWrapper = document.createElement("div");
      stepsWrapper.className = "steps-container";
      stepsWrapper.style.marginTop = "1rem";
      const h4 = document.createElement("h4");
      renderMixedLatex(h4, `Pasos de Reducción por Renglones (${data.metodo_utilizado === "gauss" ? "Método de Gauss" : "Método Gauss-Jordan"}):`);
      stepsWrapper.appendChild(h4);

      data.pasos.forEach(p => {
        const item = document.createElement("div");
        item.className = "step-item";
        const t = document.createElement("div");
        t.className = "step-item-title";
        renderMixedLatex(t, `Paso ${p.step_number}: ${p.title}`);
        
        const d = document.createElement("div");
        d.className = "step-item-desc";
        renderMixedLatex(d, p.description);
        item.appendChild(t);
        item.appendChild(d);

        if (p.matrix && p.matrix.length > 0) {
          const matBox = document.createElement("div");
          matBox.className = "latex-display-box";
          matBox.style.marginTop = "0.4rem";
          const matLatex = augmentedMatrixToLatex(p.matrix, data.orden_n);
          renderLatexElement(matBox, matLatex);
          item.appendChild(matBox);
        }

        stepsWrapper.appendChild(item);
      });
      resultBox.appendChild(stepsWrapper);
    }

    refrescarIconosLucide();
  } catch (err) {
    badge.className = "badge badge-error";
    badge.innerText = "Error";
    resultBox.innerHTML = `
      <div class="latex-equation-card" style="border-color: rgba(225,29,72,0.4);">
        <div class="latex-header" style="color:var(--accent-rose);">Error en Cálculo:</div>
        <p>${err.message}</p>
      </div>
    `;
  }
}

// =============================================================================
// =============================================================================
// APARTADO 5: ECUACIONES MATRICIALES Ax = b
// Solucionador: Eliminación Gaussiana y Gauss-Jordan con clasificación Rouché-Capelli:
// - Sistema Compatible Determinado (SCD): Solución única y comprobación de residuo cero
// - Sistema Compatible Indeterminado (SCI): Parametrización en función de variables libres
// - Sistema Incompatible (SI): Demostración analítica de inconsistencia (0 = c)
// =============================================================================
// =============================================================================
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
    for (let j = 0; j < eqN; j++) {
      const inp = document.createElement("input");
      inp.type = "text";
      inp.className = "cell-input";
      inp.id = `eq-a-${i}-${j}`;
      inp.value = (i === j ? "1" : "0");
      grid.appendChild(inp);
    }
    const sep = document.createElement("div");
    sep.style.display = "flex";
    sep.style.alignItems = "center";
    sep.style.justifyContent = "center";
    sep.style.color = "var(--text-dim)";
    sep.style.fontWeight = "bold";
    sep.innerText = "│";
    grid.appendChild(sep);

    const inpB = document.createElement("input");
    inpB.type = "text";
    inpB.className = "cell-input augmented-cell-b";
    inpB.id = `eq-b-${i}`;
    inpB.value = (i + 1).toString();
    grid.appendChild(inpB);
  }
}

function limpiarModuloEcuaciones() {
  for (let i = 0; i < eqM; i++) {
    for (let j = 0; j < eqN; j++) {
      const elA = document.getElementById(`eq-a-${i}-${j}`);
      if (elA) elA.value = "0";
    }
    const elB = document.getElementById(`eq-b-${i}`);
    if (elB) elB.value = "0";
  }

  const badge = document.getElementById("eq-badge-status");
  const resultBox = document.getElementById("eq-result-content");
  if (badge) {
    badge.className = "badge";
    badge.innerText = "Casillas limpias";
  }
  if (resultBox) {
    resultBox.innerHTML = '<p class="placeholder-text">Ingrese los coeficientes del sistema y presione "Resolver Ecuación Matricial".</p>';
  }
  mostrarToast("Sistema Ax = b limpiado.");
}

function cargarEjemploEcuacion(caso) {
  if (caso === 1) {
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

    // LaTeX del Sistema y de la Solución
    const xVars = Array.from({ length: eqN }, (_, i) => `x_{${i + 1}}`);
    const latexSystem = `A \\vec{x} = \\vec{b} \\iff ${matrixToLatex(A)} ${vectorToLatexCol(xVars)} = ${vectorToLatexCol(b)}`;
    
    let latexSol = "";
    if (data.tipo_sistema === "SCD") {
      latexSol = `\\vec{x}^* = ${vectorToLatexCol(data.vector_solucion)}`;
    } else if (data.tipo_sistema === "SCI") {
      latexSol = `\\vec{x} = ${vectorToLatexCol(data.vector_solucion)} \\quad (\\text{Infinitas soluciones})`;
    } else {
      latexSol = `\\text{No existe } \\vec{x} \\in \\mathbb{R}^${eqN} \\text{ tal que } A\\vec{x} = \\vec{b}`;
    }

    resultBox.innerHTML = `
      <div class="latex-equation-card">
        <div class="latex-header">Sistema Matricial:</div>
        <div id="eq-latex-system" class="latex-display-box"></div>
        <div class="latex-header" style="margin-top: 0.85rem;">Vector Solución:</div>
        <div id="eq-latex-sol" class="latex-display-box"></div>
        <div class="result-explanation" id="eq-explanation" style="white-space: pre-line; margin-top: 0.5rem;"></div>
      </div>
    `;

    renderLatexElement(document.getElementById("eq-latex-system"), latexSystem);
    renderLatexElement(document.getElementById("eq-latex-sol"), latexSol);

    const expEl = document.getElementById("eq-explanation");
    if (expEl && data.descripcion_sistema) {
      renderMixedLatex(expEl, data.descripcion_sistema);
    }

    if (data.verificacion && data.verificacion.length > 0) {
      const verifEl = document.createElement("div");
      verifEl.className = "verification-box";
      const h4 = document.createElement("h4");
      renderMixedLatex(h4, "Comprobación de Residuo $A\\vec{x} = \\vec{b}$:");
      verifEl.appendChild(h4);
      data.verificacion.forEach(v => {
        const row = document.createElement("div");
        renderMixedLatex(row, v);
        verifEl.appendChild(row);
      });
      resultBox.appendChild(verifEl);
    }

    if (data.pasos && data.pasos.length > 0) {
      const stepsWrapper = document.createElement("div");
      stepsWrapper.className = "steps-container";
      stepsWrapper.innerHTML = `<h4>Pasos de Eliminación por Renglones:</h4>`;
      data.pasos.forEach(p => {
        const stepItem = document.createElement("div");
        stepItem.className = "step-item";
        const t = document.createElement("div");
        t.className = "step-item-title";
        renderMixedLatex(t, `Paso ${p.step_number}: ${p.title}`);
        const d = document.createElement("div");
        d.className = "step-item-desc";
        renderMixedLatex(d, p.description);
        stepItem.appendChild(t);
        stepItem.appendChild(d);
        stepsWrapper.appendChild(stepItem);
      });
      resultBox.appendChild(stepsWrapper);
    }
    refrescarIconosLucide();
  } catch (err) {
    badge.className = "badge badge-error";
    badge.innerText = "Error";
    resultBox.innerHTML = `
      <div class="latex-equation-card" style="border-color: rgba(225,29,72,0.4);">
        <div class="latex-header" style="color:var(--accent-rose);">Error al resolver:</div>
        <p>${err.message}</p>
      </div>
    `;
  }
}

// =============================================================================
// =============================================================================
// APARTADO 6: DETERMINANTE DE MATRICES CUADRADAS |A|
// Algoritmos: Expansión de Laplace por Cofactores vs Descomposición / Eliminación LU
// Análisis: Complejidad Temporal O(n!) vs O(n³), Dictamen de Invertibilidad y Regla de Sarrus
// =============================================================================
// =============================================================================

function inicializarModuloDeterminante() {
  const container = document.getElementById("det-matrix-grid");
  if (!container) return;
  renderizarMatrizDeterminante();
  cargarEjemploDeterminante(3);
}

function cambiarDimDet(delta) {
  const input = document.getElementById("det-order-n");
  if (!input) return;
  let val = parseInt(input.value) || 3;
  val = Math.max(1, Math.min(8, val + delta));
  input.value = val;
  renderizarMatrizDeterminante();
}

function renderizarMatrizDeterminante() {
  const input = document.getElementById("det-order-n");
  const container = document.getElementById("det-matrix-grid");
  if (!input || !container) return;

  const n = parseInt(input.value) || 3;
  container.innerHTML = "";
  container.style.gridTemplateColumns = `repeat(${n}, 62px)`;

  for (let r = 0; r < n; r++) {
    for (let c = 0; c < n; c++) {
      const cell = document.createElement("input");
      cell.type = "text";
      cell.id = `det-a-${r}-${c}`;
      cell.className = "cell-input";
      cell.value = (r === c) ? "1" : "0";
      cell.placeholder = "0";
      cell.addEventListener("input", actualizarEficienciaDeterminanteUI);
      container.appendChild(cell);
    }
  }

  actualizarEficienciaDeterminanteUI();
}

function obtenerMatrizDeterminanteValores() {
  const input = document.getElementById("det-order-n");
  const n = parseInt(input.value) || 3;
  const A = [];

  for (let r = 0; r < n; r++) {
    const fila = [];
    for (let c = 0; c < n; c++) {
      const el = document.getElementById(`det-a-${r}-${c}`);
      const val = el ? el.value.trim() : "0";
      fila.push(val === "" ? "0" : val);
    }
    A.push(fila);
  }
  return A;
}

function calcularOperacionesTeoricas(n) {
  // Cofactores: n * (ops(n - 1) + 2)
  let opsCof = 1;
  if (n === 2) opsCof = 3;
  else if (n > 2) {
    opsCof = 3;
    for (let k = 3; k <= n; k++) {
      opsCof = k * (opsCof + 2);
    }
  }

  // LU: sum_{k=1}^{n-1} (n - k)*(2*(n - k) + 1) + (n - 1)
  let opsLu = 1;
  if (n > 1) {
    let sum = 0;
    for (let k = 0; k < n - 1; k++) {
      const rem = n - 1 - k;
      sum += rem * (2 * rem + 1);
    }
    opsLu = sum + (n - 1);
  }

  return { opsCof, opsLu };
}

function actualizarEficienciaDeterminanteUI() {
  const input = document.getElementById("det-order-n");
  if (!input) return;
  const n = parseInt(input.value) || 3;

  const { opsCof, opsLu } = calcularOperacionesTeoricas(n);

  const badgeRec = document.getElementById("det-badge-recommendation");
  const compLu = document.getElementById("det-complexity-lu");
  const opsLuEl = document.getElementById("det-ops-lu");
  const badgeLu = document.getElementById("det-badge-lu");
  const cardLu = document.getElementById("stat-card-lu");

  const compCof = document.getElementById("det-complexity-cof");
  const opsCofEl = document.getElementById("det-ops-cof");
  const badgeCof = document.getElementById("det-badge-cof");
  const cardCof = document.getElementById("stat-card-cof");

  const verdictEl = document.getElementById("det-efficiency-verdict");
  const radioLuText = document.getElementById("label-method-lu");
  const radioCofText = document.getElementById("label-method-cof");

  if (compLu) compLu.innerText = `O(n³) = O(${n}³)`;
  if (opsLuEl) opsLuEl.innerText = `~${opsLu.toLocaleString()} operaciones elementales`;

  if (compCof) compCof.innerText = `O(n!) = O(${n}!)`;
  if (opsCofEl) opsCofEl.innerText = `~${opsCof.toLocaleString()} operaciones factoriales`;

  if (n <= 2) {
    if (badgeRec) badgeRec.innerText = "Ambos Métodos Óptimos";
    if (badgeLu) {
      badgeLu.className = "stat-badge stat-badge-best";
      badgeLu.innerText = "Óptimo";
    }
    if (badgeCof) {
      badgeCof.className = "stat-badge stat-badge-best";
      badgeCof.innerText = "Directo (ad - bc)";
    }
    if (cardLu) cardLu.className = "efficiency-stat-card active-recommended";
    if (cardCof) cardCof.className = "efficiency-stat-card active-recommended";
    if (verdictEl) {
      verdictEl.innerText = `Para orden n = ${n}, el número de operaciones es mínimo e idéntico. Cofactores aplica la fórmula directa inmediata (ad - bc) y LU realiza una reducción elemental equivalente.`;
    }
    if (radioLuText) radioLuText.innerHTML = `<strong>Descomposición LU (PA = LU)</strong> — Triangulación Gaussiana [O(n³)]`;
    if (radioCofText) radioCofText.innerHTML = `<strong>Expansión por Cofactores (Laplace)</strong> — Fórmula directa analítica [O(n!)]`;
  } else if (n === 3) {
    if (badgeRec) badgeRec.innerText = "LU Recomendado (Leve Ventaja)";
    if (badgeLu) {
      badgeLu.className = "stat-badge stat-badge-best";
      badgeLu.innerText = "Recomendado";
    }
    if (badgeCof) {
      badgeCof.className = "stat-badge stat-badge-alt";
      badgeCof.innerText = "Didáctico (Sarrus)";
    }
    if (cardLu) cardLu.className = "efficiency-stat-card active-recommended";
    if (cardCof) cardCof.className = "efficiency-stat-card";
    if (verdictEl) {
      verdictEl.innerText = `Para n = 3, ambos métodos son rápidos y exactos. LU requiere ~${opsLu} operaciones elementales, mientras que Cofactores realiza ~${opsCof} operaciones pero permite visualizar el desarrollo por menores y Sarrus.`;
    }
    if (radioLuText) radioLuText.innerHTML = `<strong>Descomposición LU (PA = LU)</strong> — Triangulación [O(3³) ≈ ${opsLu} ops] <span class="badge badge-success" style="font-size:0.65rem; padding:0.1rem 0.4rem;">Más Rápido</span>`;
    if (radioCofText) radioCofText.innerHTML = `<strong>Expansión por Cofactores (Laplace)</strong> — Menores y Sarrus [O(3!) ≈ ${opsCof} ops]`;
  } else {
    // n >= 4: LU drásticamente más eficiente
    const factorRatio = Math.max(1, Math.round(opsCof / Math.max(1, opsLu)));
    if (badgeRec) badgeRec.innerText = `⭐ LU Ampliamente Superior (×${factorRatio.toLocaleString()} más rápido)`;
    if (badgeLu) {
      badgeLu.className = "stat-badge stat-badge-best";
      badgeLu.innerText = "⭐ ALTAMENTE RECOMENDADO";
    }
    if (badgeCof) {
      badgeCof.className = "stat-badge stat-badge-warn";
      badgeCof.innerText = "⚠️ Inviable / Factorial";
    }
    if (cardLu) cardLu.className = "efficiency-stat-card active-recommended";
    if (cardCof) cardCof.className = "efficiency-stat-card";
    if (verdictEl) {
      verdictEl.innerHTML = `<strong>¡Para n = ${n}, la Descomposición LU es drásticamente más eficiente!</strong> Cofactores requiere un orden factorial de ~${opsCof.toLocaleString()} operaciones, mientras que LU resuelve la triangulación en únicamente ~${opsLu.toLocaleString()} operaciones (O(n³)). ¡LU es <strong>${factorRatio.toLocaleString()} veces</strong> más eficiente!`;
    }
    if (radioLuText) radioLuText.innerHTML = `<strong>Descomposición LU (PA = LU)</strong> — [O(${n}³) ≈ ${opsLu.toLocaleString()} ops] <span class="badge badge-success" style="font-size:0.65rem; padding:0.1rem 0.4rem;">⭐ RECOMENDADO</span>`;
    if (radioCofText) radioCofText.innerHTML = `<strong>Expansión por Cofactores (Laplace)</strong> — [O(${n}!) ≈ ${opsCof.toLocaleString()} ops] <span class="badge badge-error" style="font-size:0.65rem; padding:0.1rem 0.4rem;">⚠️ Alto Costo Factorial</span>`;
  }
}

function actualizarPreferenciaMetodo() {
  const input = document.getElementById("det-order-n");
  const n = input ? parseInt(input.value) || 3 : 3;
  const radio = document.querySelector('input[name="det-method"]:checked');
  if (radio && radio.value === "cofactores" && n >= 5) {
    mostrarToast(`Aviso: Para matrices ${n}×${n}, Cofactores tiene orden factorial O(${n}!). Se recomienda usar Descomposición LU.`);
  }
}

function cargarEjemploDeterminante(caso) {
  const input = document.getElementById("det-order-n");
  if (!input) return;

  let matrizDatos = [];
  if (caso === 2) {
    input.value = 2;
    matrizDatos = [
      ["3", "8"],
      ["4", "6"]
    ];
  } else if (caso === 3) {
    input.value = 3;
    matrizDatos = [
      ["1", "2", "3"],
      ["0", "1", "4"],
      ["5", "6", "0"]
    ];
  } else if (caso === 4) {
    input.value = 4;
    matrizDatos = [
      ["2", "1", "0", "4"],
      ["-1", "0", "2", "1"],
      ["3", "-2", "1", "0"],
      ["0", "1", "1", "2"]
    ];
  } else if (caso === "singular") {
    input.value = 3;
    matrizDatos = [
      ["1", "2", "3"],
      ["4", "5", "6"],
      ["5", "7", "9"] // F3 = F1 + F2
    ];
  } else if (caso === "triangular") {
    input.value = 3;
    matrizDatos = [
      ["2", "5", "7"],
      ["0", "3", "-1"],
      ["0", "0", "4"]
    ];
  }

  renderizarMatrizDeterminante();
  const n = matrizDatos.length;
  for (let r = 0; r < n; r++) {
    for (let c = 0; c < n; c++) {
      const el = document.getElementById(`det-a-${r}-${c}`);
      if (el) el.value = matrizDatos[r][c];
    }
  }

  actualizarEficienciaDeterminanteUI();
  mostrarToast(`Ejemplo cargado exitosamente (${caso}).`);
}

function limpiarModuloDeterminante() {
  const input = document.getElementById("det-order-n");
  const n = input ? parseInt(input.value) || 3 : 3;
  for (let r = 0; r < n; r++) {
    for (let c = 0; c < n; c++) {
      const el = document.getElementById(`det-a-${r}-${c}`);
      if (el) el.value = "0";
    }
  }
  actualizarEficienciaDeterminanteUI();
  mostrarToast("Casillas de la matriz restablecidas a cero.");
}

async function calcularDeterminanteUI() {
  const badge = document.getElementById("det-badge-status");
  const resultBox = document.getElementById("det-result-content");
  if (!badge || !resultBox) return;

  badge.className = "badge badge-dim";
  badge.innerText = "Calculando...";

  const A = obtenerMatrizDeterminanteValores();
  const metodoInput = document.querySelector('input[name="det-method"]:checked');
  const metodo = metodoInput ? metodoInput.value : "lu";

  try {
    const res = await fetch("/api/matrices/determinante", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ A, metodo })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Error al calcular el determinante");

    if (data.es_invertible) {
      badge.className = "badge badge-success";
      badge.innerText = "Invertible (No Singular)";
    } else {
      badge.className = "badge badge-error";
      badge.innerText = "Matriz Singular (|A| = 0)";
    }

    const detVal = data.determinante;
    const detDec = data.determinante_decimal;
    const esEntero = !detVal.includes("/");
    const detFmtLatex = formatLatexFrac(detVal);

    let latexPrincipal = "";
    if (esEntero) {
      latexPrincipal = `\\det(A) = |A| = ${detFmtLatex}`;
    } else {
      latexPrincipal = `\\det(A) = |A| = ${detFmtLatex} \\approx ${detDec}`;
    }

    let htmlContenido = `
      <div class="latex-equation-card">
        <div class="latex-header">Valor Escalar del Determinante |A|:</div>
        <div id="det-latex-target" class="latex-display-box"></div>
        <div id="det-dictamen-box"></div>
      </div>
    `;

    // Pasos detallados
    if (data.pasos && data.pasos.length > 0) {
      htmlContenido += `
        <div class="steps-container">
          <h4>Desarrollo Algebraico Paso a Paso (${data.metodo.toUpperCase()}):</h4>
          <div id="det-steps-list"></div>
        </div>
      `;
    }

    resultBox.innerHTML = htmlContenido;

    // Renderizar KaTeX principal
    renderLatexElement(document.getElementById("det-latex-target"), latexPrincipal);

    // Renderizar dictamen teórico de invertibilidad con KaTeX
    const dictamenBox = document.getElementById("det-dictamen-box");
    if (dictamenBox) {
      dictamenBox.className = "verification-box";
      dictamenBox.style.marginTop = "0.85rem";

      if (data.es_invertible) {
        dictamenBox.style.background = "rgba(5, 150, 105, 0.05)";
        dictamenBox.style.borderColor = "rgba(5, 150, 105, 0.25)";

        const h4 = document.createElement("h4");
        h4.style.color = "var(--accent-emerald)";
        h4.innerText = "✓ Matriz No Singular (Invertible):";
        dictamenBox.appendChild(h4);

        const lineas = [
          `Como $\\det(A) \\neq 0$, la matriz posee rango completo: $\\operatorname{rg}(A) = ${data.orden_n}$.`,
          "Sus columnas y filas son linealmente independientes (L.I.).",
          `Existe matriz inversa única $A^{-1}$ tal que $A \\cdot A^{-1} = I_{${data.orden_n}}$.`,
          `La ecuación $A\\vec{x} = \\vec{b}$ tiene solución única $\\vec{x} = A^{-1}\\vec{b}$ para cualquier vector $\\vec{b}$.`,
          `Método aplicado: ${data.metodo.toUpperCase()} (${data.complejidad_teorica} — ~${data.operaciones_estimadas.toLocaleString()} operaciones).`
        ];

        lineas.forEach(txt => {
          const row = document.createElement("div");
          row.style.margin = "0.25rem 0";
          row.style.lineHeight = "1.6";
          renderMixedLatex(row, `• ${txt}`);
          dictamenBox.appendChild(row);
        });
      } else {
        dictamenBox.style.background = "rgba(225, 29, 72, 0.05)";
        dictamenBox.style.borderColor = "rgba(225, 29, 72, 0.25)";

        const h4 = document.createElement("h4");
        h4.style.color = "var(--accent-rose)";
        h4.innerText = "✗ Matriz Singular (No Invertible):";
        dictamenBox.appendChild(h4);

        const lineas = [
          `Como $\\det(A) = 0$, la matriz tiene rango deficiente: $\\operatorname{rg}(A) < ${data.orden_n}$.`,
          "Sus filas y columnas son linealmente dependientes (L.D.).",
          "No existe matriz inversa ($\\nexists A^{-1}$).",
          "El sistema homogéneo $A\\vec{x} = \\vec{0}$ admite soluciones no triviales (infinitas soluciones).",
          `Método aplicado: ${data.metodo.toUpperCase()} (${data.complejidad_teorica}).`
        ];

        lineas.forEach(txt => {
          const row = document.createElement("div");
          row.style.margin = "0.25rem 0";
          row.style.lineHeight = "1.6";
          renderMixedLatex(row, `• ${txt}`);
          dictamenBox.appendChild(row);
        });
      }
    }

    // Renderizar pasos
    if (data.pasos && data.pasos.length > 0) {
      const stepsContainer = document.getElementById("det-steps-list");
      data.pasos.forEach(p => {
        const stepItem = document.createElement("div");
        stepItem.className = "step-item";

        const titleEl = document.createElement("div");
        titleEl.className = "step-item-title";
        renderMixedLatex(titleEl, `Paso ${p.numero}: ${p.titulo}`);
        stepItem.appendChild(titleEl);

        const descEl = document.createElement("div");
        descEl.className = "step-item-desc";
        renderMixedLatex(descEl, p.descripcion);
        stepItem.appendChild(descEl);

        if (p.detalles && p.detalles.length > 0) {
          const detList = document.createElement("div");
          detList.style.marginTop = "0.4rem";
          detList.style.fontSize = "0.82rem";
          detList.style.color = "var(--text-muted)";
          p.detalles.forEach(d => {
            const rowD = document.createElement("div");
            rowD.style.padding = "0.15rem 0";
            renderMixedLatex(rowD, `• ${d}`);
            detList.appendChild(rowD);
          });
          stepItem.appendChild(detList);
        }

        if (p.matriz_estado && p.numero > 1) {
          const matBox = document.createElement("div");
          matBox.className = "latex-display-box";
          matBox.style.marginTop = "0.5rem";
          renderLatexElement(matBox, matrixToLatex(p.matriz_estado));
          stepItem.appendChild(matBox);
        }

        stepsContainer.appendChild(stepItem);
      });
    }

    refrescarIconosLucide();
    mostrarToast(`Determinante calculado: |A| = ${detVal}`);
  } catch (err) {
    badge.className = "badge badge-error";
    badge.innerText = "Error";
    resultBox.innerHTML = `
      <div class="latex-equation-card" style="border-color: rgba(225,29,72,0.4);">
        <div class="latex-header" style="color:var(--accent-rose);">Error al calcular:</div>
        <p>${err.message}</p>
      </div>
    `;
  }
}
