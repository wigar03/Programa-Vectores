/* Interfaz aislada del módulo de bisección. Los cálculos pertenecen al servidor. */
(() => {
  "use strict";

  const EJEMPLOS = {
    hoja: { funcion: "x^4 - 5*x^3 + 0.5*x^2 - 11*x + 10", a: "0.6", b: "1", criterio: "residuo", tolerancia: "0.0001" },
    coseno: { funcion: "cos(x) - x", a: "0", b: "1", criterio: "intervalo", tolerancia: "0.0001" },
    potencia: { funcion: "x^10 - 1", a: "0", b: "1.3", criterio: "relativo", tolerancia: "0.01" },
  };
  const AYUDA = {
    intervalo: String.raw`Detiene cuando $b-a \leq \varepsilon$. La cota del error en el punto medio es $\frac{b-a}{2}$. Aquí, $\varepsilon$ es la tolerancia.`,
    relativo: String.raw`Detiene cuando $\varepsilon_a = \left|\frac{c_i-c_{i-1}}{c_i}\right|\cdot 100\% \leq \varepsilon$. Aquí, $\varepsilon$ es la tolerancia porcentual: $1$ significa $1\%$. No se define en la primera iteración ni cuando $c_i=0$.`,
    residuo: String.raw`Detiene cuando $|f(c)| \leq \varepsilon$, donde $\varepsilon$ es la tolerancia. Un residuo pequeño no garantiza por sí solo un error pequeño en $x$; consulte también la cota del intervalo.`,
  };
  const MOTIVOS = {
    tolerancia: "Se alcanzó la tolerancia del criterio seleccionado.",
    raiz_en_extremo: "La función se evaluó como cero en un extremo del intervalo; no se requieren iteraciones.",
    raiz_evaluada: "$f(c)$ se evaluó como cero con la precisión de punto flotante utilizada.",
    max_iteraciones: "Se alcanzó el máximo de iteraciones sin cumplir la tolerancia. Puede aumentar el límite o revisar la tolerancia.",
    precision_agotada: "La precisión de punto flotante impide seguir reduciendo el intervalo. Revise la tolerancia o la escala de la función.",
  };

  function formatear(valor) {
    return valor === null || valor === undefined ? "—" : Number(valor.toPrecision(10)).toString();
  }

  function numeroLatex(valor, completo = false) {
    if (valor === null || valor === undefined) return String.raw`\text{—}`;
    const texto = completo ? String(valor) : formatear(valor);
    const partes = texto.toLowerCase().split("e");
    return partes.length === 2 ? `${partes[0]} \\times 10^{${Number(partes[1])}}` : texto;
  }

  function datosGrafica(res, opciones = {}) {
    const [a, b] = opciones.intervalo || res.intervalo_inicial;
    const puntos = opciones.puntos || res.grafica;
    const valores = puntos.filter(p => Number.isFinite(p.y)).map(p => p.y);
    valores.push(0, res.f_raiz);
    if (opciones.yMin !== undefined) valores.push(opciones.yMin);
    if (opciones.yMax !== undefined) valores.push(opciones.yMax);
    const escala = Math.max(...valores.map(Math.abs)) || 1;
    const minimo = opciones.yMin !== undefined ? (opciones.yMin / escala) : Math.min(...valores.map(v => v / escala));
    const maximo = opciones.yMax !== undefined ? (opciones.yMax / escala) : Math.max(...valores.map(v => v / escala));
    const amplitud = maximo - minimo || 1;
    const x = valor => 60 + ((valor - a) / (b - a)) * 510;
    const y = valor => 28 + (maximo - valor / escala) / amplitud * 220;
    let camino = "";
    let continuar = false;
    for (const punto of puntos) {
      if (!Number.isFinite(punto.y)) { continuar = false; continue; }
      const cy = y(punto.y);
      const cyClamped = Math.max(-5000, Math.min(5000, cy));
      camino += `${continuar ? "L" : "M"}${x(punto.x).toFixed(2)},${cyClamped.toFixed(2)} `;
      continuar = true;
    }
    const bx1 = x(res.intervalo_final[0]);
    const bx2 = x(res.intervalo_final[1]);
    return { camino, eje: y(0), raizX: x(res.raiz), raizY: y(res.f_raiz),
      bandaX: bx1,
      bandaAncho: Math.max(2, Math.abs(bx2 - bx1)),
      minimo: minimo * escala, maximo: maximo * escala,
      xScale: x, yScale: y };
  }

  // Exporta solo las utilidades puras para verificarlas con el runner estándar de Node.
  if (typeof module !== "undefined" && module.exports) {
    module.exports = { formatear, numeroLatex, datosGrafica, EJEMPLOS };
  }
  if (typeof document === "undefined") return;

  function crear(tag, texto, clase) {
    const nodo = document.createElement(tag);
    if (texto !== undefined) nodo.textContent = texto;
    if (clase) nodo.className = clase;
    return nodo;
  }

  function crearMixto(tag, texto, clase) {
    const nodo = crear(tag, undefined, clase);
    renderMixedLatex(nodo, texto);
    return nodo;
  }

  let controladorGraficaActual = null;

  function dibujarGrafica(contenedor, res) {
    if (controladorGraficaActual) {
      controladorGraficaActual.destruir();
      controladorGraficaActual = null;
    }

    const [initA, initB] = res.intervalo_inicial;
    const datosBase = datosGrafica(res);
    let initYMin = datosBase.minimo;
    let initYMax = datosBase.maximo;
    if (initYMin === initYMax) {
      initYMin -= 1;
      initYMax += 1;
    }

    let xMin = initA;
    let xMax = initB;
    let yMin = initYMin;
    let yMax = initYMax;
    let zoom = 1.0;
    let puntosActuales = res.grafica;
    let muestreoTimer = null;
    let muestreoAbort = null;
    let muestreoVersion = 0;

    const controles = document.getElementById("bis-graph-controls");
    const zoomInBtn = document.getElementById("bis-zoom-in");
    const zoomOutBtn = document.getElementById("bis-zoom-out");
    const zoomFocusBtn = document.getElementById("bis-zoom-focus");
    const zoomResetBtn = document.getElementById("bis-zoom-reset");
    const zoomLevelEl = document.getElementById("bis-zoom-level");

    if (controles) {
      controles.hidden = false;
      if (window.lucide && window.lucide.createIcons) {
        window.lucide.createIcons();
      }
    }

    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 600 300");
    svg.setAttribute("role", "img");
    svg.setAttribute("tabindex", "0");
    svg.setAttribute("aria-label", `Gráfica interactiva de f(x). Intervalo [${formatear(xMin)}, ${formatear(xMax)}]. Raíz aproximada c = ${res.raiz}. Use controles, rueda del ratón o arrastre para hacer zoom.`);

    function crearElemento(tag, atributos, texto) {
      const nodo = document.createElementNS(svg.namespaceURI, tag);
      for (const [clave, valor] of Object.entries(atributos)) nodo.setAttribute(clave, valor);
      if (texto !== undefined) nodo.textContent = texto;
      return nodo;
    }

    const defs = crearElemento("defs", {});
    const clip = crearElemento("clipPath", { id: "bis-graph-clip" });
    const clipRect = crearElemento("rect", { x: "60", y: "28", width: "510", height: "220" });
    clip.append(clipRect);
    defs.append(clip);
    svg.append(defs);

    const hitArea = crearElemento("rect", { x: "60", y: "28", width: "510", height: "220", fill: "transparent" });
    svg.append(hitArea);

    const titulo = crearElemento("title", {}, `f(x) = ${res.funcion}`);
    svg.append(titulo);

    const grupoGrafica = crearElemento("g", { "clip-path": "url(#bis-graph-clip)" });

    const bandaRect = crearElemento("rect", { x: datosBase.bandaX, y: 28, width: datosBase.bandaAncho, height: 220, class: "bis-band" });
    grupoGrafica.append(bandaRect);

    const ejeXZero = crearElemento("line", { x1: 60, x2: 570, y1: datosBase.eje, y2: datosBase.eje, class: "bis-axis-zero", "vector-effect": "non-scaling-stroke" });
    grupoGrafica.append(ejeXZero);

    const ejeYZero = crearElemento("line", { x1: 60, x2: 60, y1: 28, y2: 248, class: "bis-axis-zero-v", "stroke-dasharray": "3 3", "vector-effect": "non-scaling-stroke" });
    grupoGrafica.append(ejeYZero);

    const curvaPath = crearElemento("path", { d: datosBase.camino, fill: "none", "stroke-width": "2", class: "bis-curve", "vector-effect": "non-scaling-stroke" });
    grupoGrafica.append(curvaPath);

    const raizLinea = crearElemento("line", { x1: datosBase.raizX, x2: datosBase.raizX, y1: 28, y2: 248, "stroke-dasharray": "5 4", class: "bis-root", "vector-effect": "non-scaling-stroke" });
    grupoGrafica.append(raizLinea);

    const raizPunto = crearElemento("circle", { cx: datosBase.raizX, cy: datosBase.raizY, r: "4", class: "bis-root" });
    grupoGrafica.append(raizPunto);

    svg.append(grupoGrafica);

    const ejeXMarco = crearElemento("line", { x1: 60, x2: 570, y1: 248, y2: 248, stroke: "currentColor", "stroke-opacity": ".4" });
    const ejeYMarco = crearElemento("line", { x1: 60, x2: 60, y1: 28, y2: 248, stroke: "currentColor", "stroke-opacity": ".4" });
    svg.append(ejeXMarco, ejeYMarco);

    const estiloTexto = { fill: "currentColor", "font-size": "11", "font-family": "sans-serif" };
    const lblXMin = crearElemento("text", { ...estiloTexto, x: 60, y: 270 }, formatear(xMin));
    const lblXMax = crearElemento("text", { ...estiloTexto, x: 570, y: 270, "text-anchor": "end" }, formatear(xMax));
    const lblXAxis = crearElemento("text", { ...estiloTexto, x: 580, y: 270 }, "x");
    const lblYMax = crearElemento("text", { ...estiloTexto, x: 54, y: 22, "text-anchor": "end" }, formatear(yMax));
    const lblYMin = crearElemento("text", { ...estiloTexto, x: 54, y: 287, "text-anchor": "end" }, `Mín. f(x): ${formatear(yMin)}`);
    const lblYAxis = crearElemento("text", { ...estiloTexto, x: 60, y: 12 }, "f(x)");
    svg.append(lblXMin, lblXMax, lblXAxis, lblYMax, lblYMin, lblYAxis);

    function actualizarRender() {
      const spanInicial = initB - initA;
      const spanActual = xMax - xMin;
      zoom = spanInicial / spanActual;

      if (zoomLevelEl) {
        zoomLevelEl.textContent = `${Math.round(zoom * 100)}%`;
      }

      const datos = datosGrafica(res, { intervalo: [xMin, xMax], yMin, yMax, puntos: puntosActuales });
      curvaPath.setAttribute("d", datos.camino);

      if (datos.eje >= 28 && datos.eje <= 248) {
        ejeXZero.setAttribute("y1", datos.eje.toFixed(2));
        ejeXZero.setAttribute("y2", datos.eje.toFixed(2));
        ejeXZero.style.display = "";
      } else {
        ejeXZero.style.display = "none";
      }

      const x0 = 60 + ((0 - xMin) / (xMax - xMin)) * 510;
      if (x0 >= 60 && x0 <= 570) {
        ejeYZero.setAttribute("x1", x0.toFixed(2));
        ejeYZero.setAttribute("x2", x0.toFixed(2));
        ejeYZero.style.display = "";
      } else {
        ejeYZero.style.display = "none";
      }

      const fa = res.intervalo_final[0];
      const fb = res.intervalo_final[1];
      const bx1 = 60 + ((Math.min(fa, fb) - xMin) / (xMax - xMin)) * 510;
      const bx2 = 60 + ((Math.max(fa, fb) - xMin) / (xMax - xMin)) * 510;
      const bLeft = Math.max(60, bx1);
      const bRight = Math.min(570, bx2);
      const bWidth = Math.max(2, bRight - bLeft);
      if (bx2 >= 60 && bx1 <= 570) {
        bandaRect.setAttribute("x", bLeft.toFixed(2));
        bandaRect.setAttribute("width", bWidth.toFixed(2));
        bandaRect.style.display = "";
      } else {
        bandaRect.style.display = "none";
      }

      if (datos.raizX >= 60 && datos.raizX <= 570) {
        raizLinea.setAttribute("x1", datos.raizX.toFixed(2));
        raizLinea.setAttribute("x2", datos.raizX.toFixed(2));
        raizLinea.style.display = "";
      } else {
        raizLinea.style.display = "none";
      }

      if (datos.raizX >= 56 && datos.raizX <= 574 && datos.raizY >= 24 && datos.raizY <= 252) {
        raizPunto.setAttribute("cx", datos.raizX.toFixed(2));
        raizPunto.setAttribute("cy", datos.raizY.toFixed(2));
        raizPunto.style.display = "";
      } else {
        raizPunto.style.display = "none";
      }

      lblXMin.textContent = formatear(xMin);
      lblXMax.textContent = formatear(xMax);
      lblYMax.textContent = formatear(yMax);
      lblYMin.textContent = `Mín. f(x): ${formatear(yMin)}`;
    }

    function solicitarMuestreo() {
      clearTimeout(muestreoTimer);
      muestreoAbort?.abort();
      const versionActual = ++muestreoVersion;
      muestreoTimer = setTimeout(async () => {
        const controlador = new AbortController();
        muestreoAbort = controlador;
        try {
          const resp = await fetch("/api/biseccion/muestrear", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              funcion: res.funcion,
              a: xMin,
              b: xMax,
              cantidad: 201
            }),
            signal: controlador.signal
          });
          const datos = await resp.json();
          if (versionActual !== muestreoVersion) return;
          if (resp.ok && Array.isArray(datos.grafica)) {
            puntosActuales = datos.grafica;
            actualizarRender();
          }
        } catch (_) {}
      }, 120);
    }

    function hacerZoom(factor, focoPx = 315, focoPy = 138) {
      const nuevoZoom = zoom * factor;
      if (nuevoZoom < 0.1 || nuevoZoom > 50000) return;

      const tx = Math.max(0, Math.min(1, (focoPx - 60) / 510));
      const ty = Math.max(0, Math.min(1, (focoPy - 28) / 220));

      const xFoco = xMin + tx * (xMax - xMin);
      const yFoco = yMax - ty * (yMax - yMin);

      const nuevoXSpan = (xMax - xMin) / factor;
      const nuevoYSpan = (yMax - yMin) / factor;

      xMin = xFoco - tx * nuevoXSpan;
      xMax = xMin + nuevoXSpan;
      yMax = yFoco + ty * nuevoYSpan;
      yMin = yMax - nuevoYSpan;

      actualizarRender();
      solicitarMuestreo();
    }

    function desplazar(deltaPx, deltaPy) {
      const dx = -(deltaPx / 510) * (xMax - xMin);
      const dy = +(deltaPy / 220) * (yMax - yMin);
      xMin += dx;
      xMax += dx;
      yMin += dy;
      yMax += dy;
      actualizarRender();
    }

    function restablecer() {
      clearTimeout(muestreoTimer);
      muestreoAbort?.abort();
      xMin = initA;
      xMax = initB;
      yMin = initYMin;
      yMax = initYMax;
      puntosActuales = res.grafica;
      actualizarRender();
    }

    function enfocarRaiz() {
      clearTimeout(muestreoTimer);
      muestreoAbort?.abort();
      const r = res.raiz;
      const fr = res.f_raiz;
      const rSpanX = Math.max((initB - initA) * 0.08, Math.abs(res.cota_error) * 8, 1e-6);
      const rSpanY = Math.max((initYMax - initYMin) * 0.08, Math.abs(fr) * 8, 1e-6);
      xMin = r - rSpanX;
      xMax = r + rSpanX;
      yMin = fr - rSpanY;
      yMax = fr + rSpanY;
      actualizarRender();
      solicitarMuestreo();
    }

    const onZoomIn = () => hacerZoom(1.3);
    const onZoomOut = () => hacerZoom(1 / 1.3);
    const onZoomFocus = () => enfocarRaiz();
    const onZoomReset = () => restablecer();

    zoomInBtn?.addEventListener("click", onZoomIn);
    zoomOutBtn?.addEventListener("click", onZoomOut);
    zoomFocusBtn?.addEventListener("click", onZoomFocus);
    zoomResetBtn?.addEventListener("click", onZoomReset);

    function onWheel(e) {
      e.preventDefault();
      const rect = svg.getBoundingClientRect();
      const px = (e.clientX - rect.left) / rect.width * 600;
      const py = (e.clientY - rect.top) / rect.height * 300;
      const factor = e.deltaY < 0 ? 1.25 : (1 / 1.25);
      hacerZoom(factor, px, py);
    }
    svg.addEventListener("wheel", onWheel, { passive: false });

    let arrastrando = false;
    let ultX = 0, ultY = 0;
    const punteros = new Map();

    function onPointerDown(e) {
      if (e.pointerType === "mouse" && e.button !== 0) return;
      punteros.set(e.pointerId, { x: e.clientX, y: e.clientY });
      if (punteros.size === 1) {
        arrastrando = true;
        ultX = e.clientX;
        ultY = e.clientY;
        svg.setPointerCapture(e.pointerId);
        svg.classList.add("bis-panning");
      }
    }

    function onPointerMove(e) {
      if (!punteros.has(e.pointerId)) return;
      punteros.set(e.pointerId, { x: e.clientX, y: e.clientY });

      if (punteros.size === 2) {
        const pts = Array.from(punteros.values());
        const dist = Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y);
        if (svg._lastDist) {
          const ratio = dist / svg._lastDist;
          if (Math.abs(ratio - 1) > 0.01) {
            const midX = (pts[0].x + pts[1].x) / 2;
            const midY = (pts[0].y + pts[1].y) / 2;
            const rect = svg.getBoundingClientRect();
            const px = (midX - rect.left) / rect.width * 600;
            const py = (midY - rect.top) / rect.height * 300;
            hacerZoom(ratio, px, py);
          }
        }
        svg._lastDist = dist;
        return;
      }

      if (arrastrando) {
        const dx = e.clientX - ultX;
        const dy = e.clientY - ultY;
        ultX = e.clientX;
        ultY = e.clientY;
        desplazar(dx, dy);
      }
    }

    function onPointerUp(e) {
      punteros.delete(e.pointerId);
      svg._lastDist = null;
      if (arrastrando && punteros.size === 0) {
        arrastrando = false;
        try { svg.releasePointerCapture(e.pointerId); } catch (_) {}
        svg.classList.remove("bis-panning");
        solicitarMuestreo();
      }
    }

    svg.addEventListener("pointerdown", onPointerDown);
    svg.addEventListener("pointermove", onPointerMove);
    svg.addEventListener("pointerup", onPointerUp);
    svg.addEventListener("pointercancel", onPointerUp);

    function onDblClick() {
      restablecer();
    }
    svg.addEventListener("dblclick", onDblClick);

    function onKeyDown(e) {
      if (e.key === "+" || e.key === "=") {
        e.preventDefault();
        hacerZoom(1.25);
      } else if (e.key === "-" || e.key === "_") {
        e.preventDefault();
        hacerZoom(1 / 1.25);
      } else if (e.key === "0" || e.key.toLowerCase() === "r") {
        e.preventDefault();
        restablecer();
      } else if (e.key === "ArrowLeft") {
        e.preventDefault();
        desplazar(25, 0);
        solicitarMuestreo();
      } else if (e.key === "ArrowRight") {
        e.preventDefault();
        desplazar(-25, 0);
        solicitarMuestreo();
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        desplazar(0, 25);
        solicitarMuestreo();
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        desplazar(0, -25);
        solicitarMuestreo();
      }
    }
    svg.addEventListener("keydown", onKeyDown);

    controladorGraficaActual = {
      destruir() {
        clearTimeout(muestreoTimer);
        muestreoAbort?.abort();
        zoomInBtn?.removeEventListener("click", onZoomIn);
        zoomOutBtn?.removeEventListener("click", onZoomOut);
        zoomFocusBtn?.removeEventListener("click", onZoomFocus);
        zoomResetBtn?.removeEventListener("click", onZoomReset);
        svg.removeEventListener("wheel", onWheel);
        svg.removeEventListener("pointerdown", onPointerDown);
        svg.removeEventListener("pointermove", onPointerMove);
        svg.removeEventListener("pointerup", onPointerUp);
        svg.removeEventListener("pointercancel", onPointerUp);
        svg.removeEventListener("dblclick", onDblClick);
        svg.removeEventListener("keydown", onKeyDown);
      }
    };

    contenedor.replaceChildren(svg,
      crearMixto("p", "Azul: $f(x)$. Verde: aproximación y franja del intervalo final. Navegación: use los controles (+ / − / ↺ / 🎯), la rueda del ratón o arrastre para hacer zoom y explorar la gráfica.", "bis-help"));
    contenedor.hidden = false;
  }

  function renderizarResultado(contenedor, res) {
    const funcion = crear("p", `f(x) = ${res.funcion}`, "bis-function");
    if (res.funcion_latex) renderLatexElement(funcion, `f(x) = ${res.funcion_latex}`, true);
    const mensaje = crearMixto("p", MOTIVOS[res.motivo], "bis-message");
    const resumen = crear("dl", undefined, "bis-summary");
    for (const [etiqueta, valor] of [
      [res.convergio ? "Raíz aproximada ($c$)" : "Última aproximación ($c$)", res.raiz],
      ["Residuo $|f(c)|$", res.residuo], ["Cota del error en $x$", res.cota_error],
      ["Iteraciones", res.iteraciones],
    ]) {
      const grupo = crear("div", undefined, "bis-stat");
      const cifra = crear("dd", formatear(valor));
      cifra.title = String(valor);
      if (etiqueta !== "Iteraciones") renderLatexElement(cifra, numeroLatex(valor), false);
      const titulo = crearMixto("dt", etiqueta);
      if (etiqueta.startsWith("Cota")) titulo.append(crear("sup", "*"));
      grupo.append(titulo, cifra);
      resumen.append(grupo);
    }
    const [a, b] = res.intervalo_final;
    const verificacion = crearMixto("p", `Verificación: $f(${numeroLatex(res.raiz)}) = ${numeroLatex(res.f_raiz)}$.`, "bis-message");
    const intervalo = crearMixto("p", `Intervalo final: $[${numeroLatex(a)},\\; ${numeroLatex(b)}]$.`, "bis-message");
    const criterio = crearMixto("p", `Criterio: ${res.criterio}. Tolerancia: $${numeroLatex(res.tolerancia)}${res.criterio === "relativo" ? "\\%" : ""}$.`, "bis-help");
    contenedor.replaceChildren(funcion, mensaje, resumen, verificacion, intervalo, criterio,
      crearMixto("p", "*La cota del intervalo supone continuidad en $[a,b]$. Un cambio de signo no garantiza una raíz si la función es discontinua. Los valores se calculan en punto flotante y se redondean solo para mostrarlos; sitúe el cursor sobre una cifra para ver su valor completo.", "bis-help"));
  }

  function renderizarTabla(contenedor, res) {
    const tabla = crear("table");
    tabla.append(crear("caption", `Procedimiento de bisección: ${res.iteraciones} iteraciones.`));
    const cabecera = crear("thead");
    const fila = crear("tr");
    const columnas = [["numero", "i"], ["a", "a"], ["b", "b"], ["c", "c"],
      ["fc", "f(c)"], ["error_relativo", "εa (%)"]];
    for (const texto of ["$i$", "$a$", "$b$", "$c$", "$f(c)$", "$\\varepsilon_a\\;(\\%)$", "Detalle"]) {
      const celda = crearMixto("th", texto);
      celda.scope = "col";
      fila.append(celda);
    }
    cabecera.append(fila);
    const cuerpo = crear("tbody");
    for (const paso of res.pasos) {
      const fila = crear("tr");
      for (const [clave, etiqueta] of columnas) {
        const valor = paso[clave];
        const celda = crear("td", undefined, "bis-cell");
        celda.dataset.label = etiqueta === "i" ? "Iteración" : etiqueta;
        const etiquetaMovil = crearMixto("span", clave === "numero" ? "Iteración" : clave === "error_relativo" ? "$\\varepsilon_a\\;(\\%)$" : `$${etiqueta}$`, "bis-cell-label");
        const cifra = crear("span", formatear(valor));
        if (typeof valor === "number" && /e/i.test(formatear(valor))) renderLatexElement(cifra, numeroLatex(valor), false);
        celda.append(etiquetaMovil, cifra);
        if (typeof valor === "number") celda.title = String(valor);
        fila.append(celda);
      }
      const celdaDetalle = crear("td", undefined, "bis-detail-cell");
      const detalle = crear("details", undefined, "bis-iteration-detail");
      const botonDetalle = crear("summary", "Ver detalle");
      botonDetalle.setAttribute("aria-label", `Ver detalle de la iteración ${paso.numero}`);
      detalle.append(botonDetalle);
      celdaDetalle.append(detalle);
      fila.append(celdaDetalle);
      cuerpo.append(fila);

      const filaDetalle = crear("tr", undefined, "bis-detail-row");
      filaDetalle.id = `bis-iteration-${paso.numero}`;
      botonDetalle.setAttribute("aria-controls", filaDetalle.id);
      filaDetalle.hidden = true;
      const contenidoDetalle = crear("td");
      contenidoDetalle.colSpan = columnas.length + 1;
      const medidas = crear("dl", undefined, "bis-iteration-values");
      for (const [clave, etiqueta] of [["a", "$a$"], ["b", "$b$"], ["c", "$c$"],
        ["fa", "$f(a)$"], ["fb", "$f(b)$"], ["fc", "$f(c)$"], ["signo_ac", "Signo $f(a)\\,f(c)$"],
        ["ancho", "Ancho $b-a$"], ["cota_error", "Cota del error"],
        ["error_absoluto", "$|c_i-c_{i-1}|$"], ["error_relativo", "$\\varepsilon_a\\;(\\%)$"], ["decision", "Acción"]]) {
        const grupo = crear("div");
        const valor = paso[clave];
        const cifra = crear("dd", valor === null ? "—" : String(valor));
        if (clave === "decision" && valor !== "Finalizar") renderLatexElement(cifra, valor === "b ← c" ? "b \\leftarrow c" : "a \\leftarrow c", false);
        else if (typeof valor === "number" && /e/i.test(String(valor))) renderLatexElement(cifra, numeroLatex(valor, true), false);
        grupo.append(crearMixto("dt", etiqueta), cifra);
        medidas.append(grupo);
      }
      contenidoDetalle.append(crear("p", `Detalle de la iteración ${paso.numero} · valores completos`, "bis-detail-title"), medidas);
      filaDetalle.append(contenidoDetalle);
      cuerpo.append(filaDetalle);
      detalle.addEventListener("toggle", () => {
        filaDetalle.hidden = !detalle.open;
        botonDetalle.textContent = detalle.open ? "Ocultar" : "Ver detalle";
        botonDetalle.setAttribute("aria-label", `${detalle.open ? "Ocultar" : "Ver"} detalle de la iteración ${paso.numero}`);
      });
    }
    tabla.append(cabecera, cuerpo);
    contenedor.replaceChildren(tabla);
  }

  document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("bis-form");
    if (!form) return;
    const estado = document.getElementById("bis-status");
    const resultado = document.getElementById("bis-result");
    const grafica = document.getElementById("bis-plot");
    const tabla = document.getElementById("bis-table");
    const tarjetaTabla = document.getElementById("bis-table-card");
    const boton = document.getElementById("bis-submit");
    const preview = document.getElementById("bis-preview-math");
    const previewEstado = document.getElementById("bis-preview-status");
    let controlador = null;
    let version = 0;
    let previewControlador = null;
    let previewVersion = 0;
    let previewTemporizador;

    function actualizarPreview() {
      clearTimeout(previewTemporizador);
      previewControlador?.abort();
      const actual = ++previewVersion;
      const funcion = form.elements.funcion.value.trim();
      preview.replaceChildren();
      if (!funcion) {
        previewEstado.textContent = "Escriba una función para ver su representación matemática.";
        return;
      }
      previewEstado.textContent = "Actualizando vista matemática…";
      previewTemporizador = setTimeout(async () => {
        previewControlador = new AbortController();
        try {
          const respuesta = await fetch("/api/biseccion/preview", {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ funcion }), signal: previewControlador.signal,
          });
          const datos = await respuesta.json();
          if (actual !== previewVersion) return;
          if (!respuesta.ok || datos.error) {
            previewEstado.textContent = "Complete la expresión para actualizar la vista matemática.";
            return;
          }
          renderLatexElement(preview, `f(x) = ${datos.latex}`, true);
          previewEstado.textContent = window.katex ? "Vista de la función escrita; no verifica su dominio ni su continuidad." : "Representación LaTeX. KaTeX no está disponible; la función puede calcularse igualmente.";
        } catch (error) {
          if (actual !== previewVersion || error.name === "AbortError") return;
          previewEstado.textContent = "Vista matemática no disponible en este momento. Puede seguir escribiendo o calcular.";
        }
      }, 200);
    }

    function ayuda() {
      renderMixedLatex(document.getElementById("bis-criterion-help"), AYUDA[form.elements.criterio.value]);
      document.getElementById("bis-tolerance-label").textContent = form.elements.criterio.value === "relativo" ? "Tolerancia (%)" : "Tolerancia";
    }

    function limpiarResultado(mensaje = "Ingrese la función y un intervalo para calcular su raíz aproximada.") {
      version++;
      controlador?.abort();
      controlador = null;
      if (controladorGraficaActual) {
        controladorGraficaActual.destruir();
        controladorGraficaActual = null;
      }
      const controles = document.getElementById("bis-graph-controls");
      if (controles) controles.hidden = true;
      boton.disabled = false;
      form.setAttribute("aria-busy", "false");
      estado.className = "badge";
      estado.textContent = "Pendiente";
      resultado.replaceChildren(crear("p", mensaje, "placeholder-text"));
      grafica.replaceChildren();
      grafica.hidden = true;
      tabla.replaceChildren();
      tarjetaTabla.hidden = true;
    }

    form.addEventListener("input", () => { limpiarResultado("Parámetros modificados. Calcule para actualizar el resultado."); ayuda(); });
    form.elements.funcion.addEventListener("input", actualizarPreview);
    document.getElementById("bis-clear").addEventListener("click", () => {
      form.reset();
      for (const nombre of ["funcion", "a", "b"]) form.elements[nombre].value = "";
      limpiarResultado();
      ayuda();
      actualizarPreview();
      form.elements.funcion.focus();
    });
    document.querySelectorAll("[data-bis-example]").forEach(botonEjemplo => {
      botonEjemplo.addEventListener("click", () => {
        for (const [nombre, valor] of Object.entries(EJEMPLOS[botonEjemplo.dataset.bisExample])) form.elements[nombre].value = valor;
        form.elements.max_iteraciones.value = "100";
        limpiarResultado("Ejemplo cargado. Presione Calcular raíz por bisección.");
        ayuda();
        actualizarPreview();
      });
    });
    form.addEventListener("submit", async evento => {
      evento.preventDefault();
      limpiarResultado("Calculando iteraciones…");
      const actual = version;
      controlador = new AbortController();
      boton.disabled = true;
      form.setAttribute("aria-busy", "true");
      estado.textContent = "Calculando…";
      try {
        const respuesta = await fetch("/api/biseccion/resolver", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify(Object.fromEntries(new FormData(form))),
          signal: controlador.signal,
        });
        const datos = await respuesta.json();
        if (actual !== version) return;
        if (!respuesta.ok || datos.error) throw new Error(datos.error || "No se pudo completar el cálculo.");
        estado.className = `badge ${datos.convergio ? "badge-success" : "badge-warning"}`;
        estado.textContent = datos.convergio ? "Cálculo completado" : "Tolerancia no alcanzada";
        renderizarResultado(resultado, datos);
        dibujarGrafica(grafica, datos);
        if (datos.pasos.length) {
          renderizarTabla(tabla, datos);
          tarjetaTabla.hidden = false;
        }
      } catch (error) {
        if (actual !== version || error.name === "AbortError") return;
        estado.className = "badge badge-error";
        estado.textContent = "Revise los datos";
        resultado.replaceChildren(crear("p", error.message, "bis-message bis-error"));
      } finally {
        if (actual === version) {
          boton.disabled = false;
          form.setAttribute("aria-busy", "false");
          controlador = null;
        }
      }
    });
    ayuda();
    actualizarPreview();
  });
})();
