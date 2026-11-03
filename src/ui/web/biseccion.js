/* Interfaz aislada del módulo de bisección. Los cálculos pertenecen al servidor. */
(() => {
  "use strict";

  const EJEMPLOS = {
    hoja: { funcion: "x^4 - 5*x^3 + 0.5*x^2 - 11*x + 10", a: "0.6", b: "1", criterio: "residuo", tolerancia: "0.0001" },
    coseno: { funcion: "cos(x) - x", a: "0", b: "1", criterio: "intervalo", tolerancia: "0.0001" },
    potencia: { funcion: "x^10 - 1", a: "0", b: "1.3", criterio: "relativo", tolerancia: "0.01" },
  };
  const AYUDA = {
    intervalo: "Detiene cuando b − a ≤ tolerancia. La cota del error en el punto medio es (b − a)/2.",
    relativo: "Detiene cuando |c actual − c anterior| / |c actual| × 100% ≤ tolerancia. Por ejemplo, 1 significa 1%. No se define en la primera iteración ni cuando c = 0.",
    residuo: "Detiene cuando |f(c)| ≤ tolerancia. Un residuo pequeño no garantiza por sí solo un error pequeño en x; consulte también la cota del intervalo.",
  };
  const MOTIVOS = {
    tolerancia: "Se alcanzó la tolerancia del criterio seleccionado.",
    raiz_en_extremo: "La función se evaluó como cero en un extremo del intervalo; no se requieren iteraciones.",
    raiz_evaluada: "f(c) se evaluó como cero con la precisión de punto flotante utilizada.",
    max_iteraciones: "Se alcanzó el máximo de iteraciones sin cumplir la tolerancia. Puede aumentar el límite o revisar la tolerancia.",
    precision_agotada: "La precisión de punto flotante impide seguir reduciendo el intervalo. Revise la tolerancia o la escala de la función.",
  };

  function formatear(valor) {
    return valor === null || valor === undefined ? "—" : Number(valor.toPrecision(10)).toString();
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
    module.exports = { formatear, datosGrafica, EJEMPLOS };
  }
  if (typeof document === "undefined") return;

  function crear(tag, texto, clase) {
    const nodo = document.createElement(tag);
    if (texto !== undefined) nodo.textContent = texto;
    if (clase) nodo.className = clase;
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
      crear("p", "Azul: f(x). Verde: aproximación y franja del intervalo final. Muestra orientativa de 201 puntos; la gráfica no certifica continuidad.", "bis-help"));
    contenedor.hidden = false;
  }

  function renderizarResultado(contenedor, res) {
    const funcion = crear("p", `f(x) = ${res.funcion}`, "bis-function");
    const mensaje = crear("p", MOTIVOS[res.motivo], "bis-message");
    const resumen = crear("dl", undefined, "bis-summary");
    for (const [etiqueta, valor] of [
      [res.convergio ? "Raíz aproximada (c)" : "Última aproximación (c)", res.raiz],
      ["Residuo |f(c)|", res.residuo], ["Cota del error en x*", res.cota_error],
      ["Iteraciones", res.iteraciones],
    ]) {
      const grupo = crear("div", undefined, "bis-stat");
      const cifra = crear("dd", formatear(valor));
      cifra.title = String(valor);
      grupo.append(crear("dt", etiqueta), cifra);
      resumen.append(grupo);
    }
    const [a, b] = res.intervalo_final;
    const verificacion = crear("p", `Verificación: f(${formatear(res.raiz)}) = ${formatear(res.f_raiz)}. Intervalo final: [${formatear(a)}, ${formatear(b)}].`, "bis-message");
    const criterio = crear("p", `Criterio: ${res.criterio}. Tolerancia: ${res.tolerancia}${res.criterio === "relativo" ? "%" : ""}.`, "bis-help");
    contenedor.replaceChildren(funcion, mensaje, resumen, verificacion, criterio,
      crear("p", "*La cota del intervalo supone continuidad en [a, b]. Un cambio de signo no garantiza una raíz si la función es discontinua. Los valores se calculan en punto flotante y se redondean solo para mostrarlos; sitúe el cursor sobre una cifra para ver su valor completo.", "bis-help"));
  }

  function renderizarTabla(contenedor, res) {
    const tabla = crear("table");
    tabla.append(crear("caption", `Procedimiento de bisección: ${res.iteraciones} iteraciones.`));
    const cabecera = crear("thead");
    const fila = crear("tr");
    for (const texto of ["i", "a", "b", "c", "f(a)", "f(b)", "f(c)", "Signo f(a)·f(c)", "b − a", "Cota error", "|c − c anterior|", "εa (%)", "Acción"]) {
      const celda = crear("th", texto);
      celda.scope = "col";
      fila.append(celda);
    }
    cabecera.append(fila);
    const cuerpo = crear("tbody");
    for (const paso of res.pasos) {
      const fila = crear("tr");
      for (const clave of ["numero", "a", "b", "c", "fa", "fb", "fc", "signo_ac", "ancho", "cota_error", "error_absoluto", "error_relativo", "decision"]) {
        const valor = paso[clave];
        const celda = crear("td", typeof valor === "string" ? valor : formatear(valor));
        if (typeof valor === "number") celda.title = String(valor);
        fila.append(celda);
      }
      cuerpo.append(fila);
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
    let controlador = null;
    let version = 0;

    function ayuda() {
      document.getElementById("bis-criterion-help").textContent = AYUDA[form.elements.criterio.value];
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
    document.getElementById("bis-clear").addEventListener("click", () => {
      form.reset();
      for (const nombre of ["funcion", "a", "b"]) form.elements[nombre].value = "";
      limpiarResultado();
      ayuda();
      form.elements.funcion.focus();
    });
    document.querySelectorAll("[data-bis-example]").forEach(botonEjemplo => {
      botonEjemplo.addEventListener("click", () => {
        for (const [nombre, valor] of Object.entries(EJEMPLOS[botonEjemplo.dataset.bisExample])) form.elements[nombre].value = valor;
        form.elements.max_iteraciones.value = "100";
        limpiarResultado("Ejemplo cargado. Presione Calcular raíz por bisección.");
        ayuda();
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
  });
})();
