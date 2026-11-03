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

  function datosGrafica(res) {
    const [a, b] = res.intervalo_inicial;
    const puntos = res.grafica;
    const valores = puntos.filter(p => Number.isFinite(p.y)).map(p => p.y);
    valores.push(0, res.f_raiz);
    const escala = Math.max(...valores.map(Math.abs)) || 1;
    const minimo = Math.min(...valores.map(v => v / escala));
    const maximo = Math.max(...valores.map(v => v / escala));
    const amplitud = maximo - minimo || 1;
    const x = valor => 60 + ((valor - a) / (b - a)) * 510;
    const y = valor => 28 + (maximo - valor / escala) / amplitud * 220;
    let camino = "";
    let continuar = false;
    for (const punto of puntos) {
      if (!Number.isFinite(punto.y)) { continuar = false; continue; }
      camino += `${continuar ? "L" : "M"}${x(punto.x).toFixed(2)},${y(punto.y).toFixed(2)} `;
      continuar = true;
    }
    return { camino, eje: y(0), raizX: x(res.raiz), raizY: y(res.f_raiz),
      bandaX: x(res.intervalo_final[0]),
      bandaAncho: Math.max(2, x(res.intervalo_final[1]) - x(res.intervalo_final[0])),
      minimo: minimo * escala, maximo: maximo * escala };
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

  function dibujarGrafica(contenedor, res) {
    const datos = datosGrafica(res);
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 600 300");
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", `Gráfica de f(x) en el intervalo inicial. Aproximación c = ${res.raiz}.`);
    function agregar(tag, atributos, texto) {
      const nodo = document.createElementNS(svg.namespaceURI, tag);
      for (const [clave, valor] of Object.entries(atributos)) nodo.setAttribute(clave, valor);
      if (texto !== undefined) nodo.textContent = texto;
      svg.append(nodo);
    }
    agregar("title", {}, `f(x) = ${res.funcion}`);
    agregar("rect", { x: datos.bandaX, y: 28, width: datos.bandaAncho, height: 220, class: "bis-band" });
    agregar("line", { x1: 60, x2: 570, y1: datos.eje, y2: datos.eje, stroke: "currentColor", "stroke-opacity": ".4" });
    agregar("line", { x1: 60, x2: 60, y1: 28, y2: 248, stroke: "currentColor", "stroke-opacity": ".4" });
    agregar("path", { d: datos.camino, fill: "none", "stroke-width": 2, class: "bis-curve" });
    agregar("line", { x1: datos.raizX, x2: datos.raizX, y1: 28, y2: 248, "stroke-dasharray": "5 4", class: "bis-root" });
    agregar("circle", { cx: datos.raizX, cy: datos.raizY, r: 4, class: "bis-root" });
    const texto = { fill: "currentColor", "font-size": 11, "font-family": "sans-serif" };
    agregar("text", { ...texto, x: 60, y: 270 }, formatear(res.intervalo_inicial[0]));
    agregar("text", { ...texto, x: 570, y: 270, "text-anchor": "end" }, formatear(res.intervalo_inicial[1]));
    agregar("text", { ...texto, x: 54, y: 22 }, formatear(datos.maximo));
    agregar("text", { ...texto, x: 54, y: 287 }, `Mín. f(x): ${formatear(datos.minimo)}`);
    agregar("text", { ...texto, x: 580, y: 270 }, "x");
    agregar("text", { ...texto, x: 60, y: 12 }, "f(x)");
    contenedor.replaceChildren(svg,
      crearMixto("p", "Azul: $f(x)$. Verde: aproximación y franja del intervalo final. Muestra orientativa de 201 puntos; la gráfica no certifica continuidad.", "bis-help"));
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
