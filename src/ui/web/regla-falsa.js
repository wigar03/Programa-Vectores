/* Interfaz del módulo de regla falsa: guía el flujo en cuatro pasos.
   Los cálculos, el análisis de continuidad y la validación pertenecen al servidor. */
(() => {
  "use strict";

  // Área de trazado dentro del viewBox 600 × 330 del SVG.
  const MARCO = { x: 58, y: 14, ancho: 528, alto: 270 };

  function formatear(valor, cifras = 10) {
    return valor === null || valor === undefined ? "—" : Number(valor.toPrecision(cifras)).toString();
  }

  function numeroLatex(valor, cifras = 10) {
    if (valor === null || valor === undefined) return String.raw`\text{—}`;
    const partes = formatear(valor, cifras).toLowerCase().split("e");
    return partes.length === 2 ? `${partes[0]} \\times 10^{${Number(partes[1])}}` : partes[0];
  }

  /* Marcas "redondas" (1, 2 o 5 por una potencia de diez) para leer intervalos en los ejes. */
  function marcas(minimo, maximo, cantidad = 6) {
    const tramo = maximo - minimo;
    if (!(tramo > 0) || !Number.isFinite(tramo)) return [];
    const bruto = tramo / cantidad;
    const potencia = 10 ** Math.floor(Math.log10(bruto));
    // De los pasos candidatos, el que deja la cantidad de marcas más cercana a la pedida.
    const paso = [1, 2, 5, 10].map(multiplo => multiplo * potencia)
      .reduce((mejor, p) => (Math.abs(tramo / p - cantidad) < Math.abs(tramo / mejor - cantidad) ? p : mejor));
    const decimales = Math.min(100, Math.max(0, -Math.floor(Math.log10(paso))));
    const lista = [];
    for (let k = Math.ceil(minimo / paso - 1e-9); k * paso <= maximo + paso * 1e-9; k++) {
      lista.push(Number((k * paso).toFixed(decimales)) + 0);
    }
    return lista;
  }

  /* Rango vertical que incluye el eje X. Junto a una asíntota, unos pocos valores
     enormes aplastarían el resto de la curva: en ese caso se recorta por cuantiles. */
  function rangoVertical(puntos) {
    const ys = puntos.map(p => p.y).filter(Number.isFinite).sort((u, v) => u - v);
    if (!ys.length) return [-1, 1];
    const cuantil = q => ys[Math.round(q * (ys.length - 1))];
    let minimo = ys[0], maximo = ys[ys.length - 1];
    const bajo = cuantil(0.03), alto = cuantil(0.97);
    if (alto > bajo && maximo - minimo > 6 * (alto - bajo)) {
      minimo = bajo - (alto - bajo) * 0.25;
      maximo = alto + (alto - bajo) * 0.25;
    }
    minimo = Math.min(minimo, 0);
    maximo = Math.max(maximo, 0);
    if (maximo === minimo) return [-1, 1];
    const margen = (maximo - minimo) * 0.06;
    return Number.isFinite(margen) ? [minimo - margen, maximo + margen] : [minimo, maximo];
  }

  function crearEscala(vista) {
    const { xMin, xMax, yMin, yMax } = vista;
    return {
      x: valor => MARCO.x + (valor - xMin) / (xMax - xMin) * MARCO.ancho,
      // Las mitades evitan el desbordamiento con valores cercanos al máximo representable.
      y: valor => MARCO.y + (yMax / 2 - valor / 2) / (yMax / 2 - yMin / 2) * MARCO.alto,
      xInversa: px => xMin + (px - MARCO.x) / MARCO.ancho * (xMax - xMin),
      yInversa: py => yMax - (py - MARCO.y) / MARCO.alto * (yMax - yMin),
    };
  }

  /* Trazo de la curva. No une puntos separados por un valor fuera del dominio, por una
     discontinuidad conocida (cortes) ni por un salto que atraviesa toda la vista. */
  function caminoCurva(puntos, escala, cortes = []) {
    const arriba = MARCO.y, abajo = MARCO.y + MARCO.alto;
    let camino = "", previo = null;
    for (const punto of puntos) {
      if (!Number.isFinite(punto.y)) { previo = null; continue; }
      const px = escala.x(punto.x);
      const py = Math.max(arriba - 4000, Math.min(abajo + 4000, escala.y(punto.y)));
      let unir = previo !== null;
      if (unir) {
        const atraviesa = (previo.py < arriba && py > abajo) || (previo.py > abajo && py < arriba);
        unir = !atraviesa && !cortes.some(corte => corte > previo.x && corte <= punto.x);
      }
      camino += `${unir ? "L" : "M"}${px.toFixed(2)},${py.toFixed(2)} `;
      previo = { x: punto.x, py };
    }
    return camino.trim();
  }

  /* Valor aproximado de f en x a partir de las muestras; null fuera del dominio. */
  function interpolar(puntos, x) {
    let i = 0, j = puntos.length - 1;
    if (j < 1 || x < puntos[0].x || x > puntos[j].x) return null;
    while (j - i > 1) {
      const medio = (i + j) >> 1;
      if (puntos[medio].x <= x) i = medio; else j = medio;
    }
    const p = puntos[i], q = puntos[j];
    for (const muestra of [p, q]) {
      if (muestra.x === x) return Number.isFinite(muestra.y) ? muestra.y : null;
    }
    if (!Number.isFinite(p.y) || !Number.isFinite(q.y)) return null;
    return p.y + (q.y - p.y) * (x - p.x) / (q.x - p.x);
  }

  /* Redondea una posición marcada con el puntero a una cifra legible para el ancho visible. */
  function redondearSegunVista(x, tramo) {
    const decimales = Math.min(12, Math.max(0, 3 - Math.floor(Math.log10(tramo))));
    return Number(x.toFixed(decimales)) + 0;
  }

  function describirDiscontinuidad(d) {
    const x = numeroLatex(d.x, 8);
    if (d.tipo === "asintota") return `Asíntota vertical en $x \\approx ${x}$.`;
    if (d.tipo === "salto") return `Salto en $x \\approx ${x}$.`;
    if (d.tipo === "punto_indefinido") return `$f$ no está definida en $x = ${x}$.`;
    return `$f$ no está definida entre $x = ${numeroLatex(d.desde, 8)}$ y $x = ${numeroLatex(d.hasta, 8)}$.`;
  }

  function textoTramos(tramos) {
    return tramos.map(t => `${t.abierto_izquierda ? "(" : "["}${numeroLatex(t.desde, 8)},\\; ${numeroLatex(t.hasta, 8)}${t.abierto_derecha ? ")" : "]"}`).join(" \\cup ");
  }

  // Exporta solo las utilidades puras para verificarlas con el runner estándar de Node.
  if (typeof module !== "undefined" && module.exports) {
    module.exports = {
      MARCO, formatear, numeroLatex, marcas, rangoVertical, crearEscala, caminoCurva,
      interpolar, redondearSegunVista,
      describirDiscontinuidad, textoTramos,
    };
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

  function svg(tag, atributos = {}, texto) {
    const nodo = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (const [clave, valor] of Object.entries(atributos)) nodo.setAttribute(clave, valor);
    if (texto !== undefined) nodo.textContent = texto;
    return nodo;
  }

  /* Texto SVG "base_sub resto": el subíndice se dibuja con tspan para no depender de la fuente. */
  function svgConSubindice(atributos, base, sub, resto = "") {
    const nodo = svg("text", atributos, base);
    nodo.append(svg("tspan", { dy: 3, "font-size": "75%" }, sub), svg("tspan", { dy: -3 }, resto));
    return nodo;
  }

  async function pedir(ruta, datos, signal) {
    const respuesta = await fetch(`/api/regla-falsa/${ruta}`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos), signal,
    });
    const cuerpo = await respuesta.json();
    if (!respuesta.ok || cuerpo.error) throw new Error(cuerpo.error || "No se pudo completar la operación.");
    return cuerpo;
  }

  function insignia(nodo, texto, clase = "") {
    nodo.className = `badge ${clase}`.trim();
    nodo.textContent = texto;
  }

  /* Gráfica interactiva compartida por los cuatro pasos. Cada paso añade una capa:
     la curva (1), discontinuidades e intervalos (2-3) y secantes con la raíz (4). */
  function crearGrafica({ contenedor, controles, lectura, leyenda, nivelZoom, botones }, avisos = {}) {
    const lienzo = svg("svg", { viewBox: "0 0 600 330", role: "img", tabindex: "0" });
    const titulo = svg("title");
    const defs = svg("defs");
    const recorte = svg("clipPath", { id: "rf-plot-clip" });
    recorte.append(svg("rect", { x: MARCO.x, y: MARCO.y, width: MARCO.ancho, height: MARCO.alto }));
    defs.append(recorte);
    const capaRejilla = svg("g");
    const capaFondo = svg("g", { "clip-path": "url(#rf-plot-clip)" });
    const curva = svg("path", { fill: "none", "stroke-width": "2", class: "bis-curve", "clip-path": "url(#rf-plot-clip)" });
    const capaMarcas = svg("g", { "clip-path": "url(#rf-plot-clip)" });
    lienzo.append(titulo, defs, capaRejilla, capaFondo, curva, capaMarcas);
    contenedor.replaceChildren(lienzo);

    const g = { funcion: null, puntos: [], vista: null, base: null, analisis: null,
      intervalo: null, resultado: null, marcando: false, provisional: null };
    const abajo = MARCO.y + MARCO.alto, derecha = MARCO.x + MARCO.ancho;
    let temporizador = null, aborto = null, turno = 0;

    function dibujar() {
      if (!g.vista) return;
      const e = crearEscala(g.vista);
      const { xMin, xMax, yMin, yMax } = g.vista;

      const rejilla = [];
      for (const valor of marcas(xMin, xMax, 6)) {
        const px = e.x(valor);
        rejilla.push(svg("line", { x1: px, x2: px, y1: MARCO.y, y2: abajo, class: "rf-grid" }),
          svg("text", { x: px, y: abajo + 16, "text-anchor": "middle", class: "rf-tick" }, formatear(valor, 6)));
      }
      for (const valor of marcas(yMin, yMax, 5)) {
        const py = e.y(valor);
        rejilla.push(svg("line", { x1: MARCO.x, x2: derecha, y1: py, y2: py, class: "rf-grid" }),
          svg("text", { x: MARCO.x - 6, y: py + 3.5, "text-anchor": "end", class: "rf-tick" }, formatear(valor, 4)));
      }
      if (yMin <= 0 && yMax >= 0) {
        rejilla.push(svg("line", { x1: MARCO.x, x2: derecha, y1: e.y(0), y2: e.y(0), class: "bis-axis-zero" }));
      }
      if (xMin <= 0 && xMax >= 0) {
        rejilla.push(svg("line", { x1: e.x(0), x2: e.x(0), y1: MARCO.y, y2: abajo, class: "bis-axis-zero" }));
      }
      rejilla.push(svg("rect", { x: MARCO.x, y: MARCO.y, width: MARCO.ancho, height: MARCO.alto, fill: "none", stroke: "currentColor", "stroke-opacity": ".4" }),
        svg("text", { x: derecha, y: abajo + 34, "text-anchor": "end", class: "rf-tick" }, "x"),
        svg("text", { x: MARCO.x, y: 9, "text-anchor": "end", class: "rf-tick" }, "f(x)"));
      capaRejilla.replaceChildren(...rejilla);

      const fondo = [], marcasResultado = [];
      const banda = (desde, hasta, clase, alto = MARCO.alto) => {
        const x1 = Math.max(MARCO.x, e.x(desde)), x2 = Math.min(derecha, e.x(hasta));
        if (x2 > x1) fondo.push(svg("rect", { x: x1, y: abajo - alto, width: x2 - x1, height: alto, class: clase }));
      };
      const vertical = (x, clase, destino = fondo) => {
        const px = e.x(x);
        if (px >= MARCO.x && px <= derecha) destino.push(svg("line", { x1: px, x2: px, y1: MARCO.y, y2: abajo, class: clase }));
        return px;
      };
      let cortes = [];
      if (g.analisis) {
        for (const d of g.analisis.continuidad.discontinuidades) {
          if (d.hasta > d.desde) banda(d.desde, d.hasta, "rf-break-band");
          else vertical(d.x, "rf-break-line");
        }
        cortes = g.analisis.continuidad.discontinuidades.filter(d => d.hasta === d.desde).map(d => d.x);
        // Franja inferior: un tramo por cada intervalo sugerido (se pulsa para elegirlo).
        if (!g.resultado) {
          for (const i of g.analisis.intervalos) {
            const x1 = Math.max(MARCO.x, e.x(i.xl)) + 1, x2 = Math.min(derecha, e.x(i.xu)) - 1;
            if (x2 > x1) fondo.push(svg("rect", { x: x1, y: abajo - 9, width: x2 - x1, height: 9, class: "rf-candidate-band" }));
          }
        }
      }
      const elegido = g.provisional || g.intervalo;
      if (elegido) {
        banda(elegido[0], elegido[1], "rf-interval-band");
        for (const [x, subindice, ancla] of [[elegido[0], "l", "end"], [elegido[1], "u", "start"]]) {
          const px = vertical(x, "rf-interval-edge");
          if (px >= MARCO.x && px <= derecha) {
            fondo.push(svgConSubindice({ x: px + (ancla === "end" ? -4 : 4), y: MARCO.y + 13, "text-anchor": ancla, class: "rf-interval-label" }, "x", subindice));
          }
        }
      }
      capaFondo.replaceChildren(...fondo);
      curva.setAttribute("d", caminoCurva(g.puntos, e, cortes));
      capaMarcas.replaceChildren(...marcasResultado);

      nivelZoom.textContent = `${Math.round((g.base.xMax - g.base.xMin) / (xMax - xMin) * 100)}%`;
      const descripcion = `Gráfica de f(x) = ${g.funcion} para x entre ${formatear(xMin, 6)} y ${formatear(xMax, 6)}.`;
      titulo.textContent = descripcion;
      lienzo.setAttribute("aria-label", descripcion);
    }

    /* Pide al servidor las muestras de la vista actual tras un zoom o un desplazamiento. */
    function muestrear(ajustarVertical = false) {
      clearTimeout(temporizador);
      aborto?.abort();
      const actual = ++turno;
      temporizador = setTimeout(async () => {
        aborto = new AbortController();
        try {
          const datos = await pedir("graficar", { funcion: g.funcion, a: g.vista.xMin, b: g.vista.xMax, cantidad: 401 }, aborto.signal);
          if (actual !== turno || !g.vista) return;
          g.puntos = datos.grafica;
          if (ajustarVertical) [g.vista.yMin, g.vista.yMax] = rangoVertical(g.puntos);
          dibujar();
        } catch (_) { /* se conserva el trazo anterior */ }
      }, 120);
    }

    function posicion(evento) {
      const caja = lienzo.getBoundingClientRect();
      return [(evento.clientX - caja.left) / caja.width * 600, (evento.clientY - caja.top) / caja.height * 330];
    }

    function acercar(factor, px = MARCO.x + MARCO.ancho / 2, py = MARCO.y + MARCO.alto / 2) {
      if (!g.vista) return;
      const ampliacion = (g.base.xMax - g.base.xMin) / (g.vista.xMax - g.vista.xMin) * factor;
      if (ampliacion < 0.05 || ampliacion > 1e6) return;
      const e = crearEscala(g.vista);
      const tx = Math.max(0, Math.min(1, (px - MARCO.x) / MARCO.ancho));
      const ty = Math.max(0, Math.min(1, (py - MARCO.y) / MARCO.alto));
      const fx = e.xInversa(MARCO.x + tx * MARCO.ancho), fy = e.yInversa(MARCO.y + ty * MARCO.alto);
      const anchoX = (g.vista.xMax - g.vista.xMin) / factor, anchoY = (g.vista.yMax - g.vista.yMin) / factor;
      g.vista.xMin = fx - tx * anchoX;
      g.vista.xMax = g.vista.xMin + anchoX;
      g.vista.yMax = fy + ty * anchoY;
      g.vista.yMin = g.vista.yMax - anchoY;
      dibujar();
      muestrear();
    }

    function desplazar(dx, dy) {
      const mx = -(dx / MARCO.ancho) * (g.vista.xMax - g.vista.xMin);
      const my = (dy / MARCO.alto) * (g.vista.yMax - g.vista.yMin);
      g.vista.xMin += mx; g.vista.xMax += mx; g.vista.yMin += my; g.vista.yMax += my;
      dibujar();
    }

    function restablecer() {
      if (!g.base) return;
      g.vista = { ...g.base };
      dibujar();
      muestrear(true);
    }

    let arrastre = null;
    lienzo.addEventListener("pointerdown", evento => {
      if (!g.vista || (evento.pointerType === "mouse" && evento.button !== 0)) return;
      const [px, py] = posicion(evento);
      arrastre = { px, py, inicioX: px, movido: false };
      try { lienzo.setPointerCapture(evento.pointerId); } catch (_) { /* puntero sin captura */ }
      if (!g.marcando) lienzo.classList.add("bis-panning");
    });
    lienzo.addEventListener("pointermove", evento => {
      if (!g.vista) return;
      const [px, py] = posicion(evento);
      const e = crearEscala(g.vista);
      const x = e.xInversa(Math.max(MARCO.x, Math.min(derecha, px)));
      const y = interpolar(g.puntos, x);
      lectura.textContent = `x = ${formatear(x, 6)} · f(x) ≈ ${y === null ? "—" : formatear(y, 6)}`;
      if (!arrastre) return;
      if (Math.abs(px - arrastre.inicioX) > 3) arrastre.movido = true;
      if (g.marcando) {
        const tramo = g.vista.xMax - g.vista.xMin;
        const extremos = [e.xInversa(arrastre.inicioX), x].map(v => redondearSegunVista(v, tramo)).sort((u, v) => u - v);
        g.provisional = arrastre.movido && extremos[1] > extremos[0] ? extremos : null;
        dibujar();
        return;
      }
      desplazar(px - arrastre.px, py - arrastre.py);
      arrastre.px = px; arrastre.py = py;
    });
    function soltar(evento) {
      if (!arrastre) return;
      const { movido } = arrastre;
      arrastre = null;
      lienzo.classList.remove("bis-panning");
      try { lienzo.releasePointerCapture(evento.pointerId); } catch (_) { /* ya liberado */ }
      if (g.marcando) {
        const marcado = g.provisional;
        g.provisional = null;
        if (marcado) avisos.alMarcar?.(marcado[0], marcado[1]);
        else dibujar();
        return;
      }
      if (!movido && g.analisis && !g.resultado && evento.type === "pointerup") {
        // Un clic sin arrastre sobre la franja inferior elige ese intervalo sugerido.
        const [px, py] = posicion(evento);
        const x = crearEscala(g.vista).xInversa(px);
        const indice = py >= abajo - 14 && py <= abajo ? g.analisis.intervalos.findIndex(i => x >= i.xl && x <= i.xu) : -1;
        if (indice >= 0) { avisos.alElegir?.(indice); return; }
      }
      if (movido) muestrear();
    }
    lienzo.addEventListener("pointerup", soltar);
    lienzo.addEventListener("pointercancel", soltar);
    lienzo.addEventListener("pointerleave", () => { if (!arrastre) lectura.textContent = ""; });
    lienzo.addEventListener("wheel", evento => {
      if (!g.vista) return;
      evento.preventDefault();
      acercar(evento.deltaY < 0 ? 1.25 : 1 / 1.25, ...posicion(evento));
    }, { passive: false });
    lienzo.addEventListener("dblclick", restablecer);
    lienzo.addEventListener("keydown", evento => {
      if (!g.vista) return;
      const teclas = {
        "+": () => acercar(1.25), "=": () => acercar(1.25), "-": () => acercar(1 / 1.25),
        "0": restablecer,
        ArrowLeft: () => { desplazar(25, 0); muestrear(); }, ArrowRight: () => { desplazar(-25, 0); muestrear(); },
        ArrowUp: () => { desplazar(0, 25); muestrear(); }, ArrowDown: () => { desplazar(0, -25); muestrear(); },
      };
      if (teclas[evento.key]) { evento.preventDefault(); teclas[evento.key](); }
    });
    botones.acercar.addEventListener("click", () => acercar(1.3));
    botones.alejar.addEventListener("click", () => acercar(1 / 1.3));
    botones.restablecer.addEventListener("click", restablecer);

    return {
      /* Paso 1: muestra la curva en la región de interés. */
      mostrar(datos) {
        const [a, b] = datos.intervalo;
        const [yMin, yMax] = rangoVertical(datos.grafica);
        Object.assign(g, { funcion: datos.funcion, puntos: datos.grafica, analisis: null, intervalo: null,
          resultado: null, provisional: null, base: { xMin: a, xMax: b, yMin, yMax } });
        g.vista = { ...g.base };
        contenedor.hidden = controles.hidden = leyenda.hidden = false;
        dibujar();
      },
      /* Paso 2: discontinuidades detectadas e intervalos sugeridos. */
      fijarAnalisis(analisis) { g.analisis = analisis; dibujar(); },
      /* Pasos 2 y 3: intervalo [x_l, x_u] elegido; null lo retira. */
      fijarIntervalo(intervalo) { g.intervalo = intervalo; dibujar(); },
      marcar(activo) {
        g.marcando = activo;
        g.provisional = null;
        lienzo.classList.toggle("rf-marking", activo);
      },
      limpiar() {
        clearTimeout(temporizador);
        aborto?.abort();
        turno++;
        g.vista = null;
        lectura.textContent = "";
        contenedor.hidden = controles.hidden = leyenda.hidden = true;
      },
    };
  }

  document.addEventListener("DOMContentLoaded", () => {
    const panel = document.getElementById("tab-regla-falsa");
    if (!panel) return;
    const el = id => document.getElementById(id);
    const formFuncion = el("rf-form-funcion");
    const formIntervalo = el("rf-form-intervalo");
    const tarjetas = [1, 2, 3, 4].map(n => el(`rf-card-${n}`));
    const estados = [1, 2, 3, 4].map(n => el(`rf-status-${n}`));
    const pasos = [...panel.querySelectorAll(".rf-step")];
    const tarjetaTabla = el("rf-table-card");
    const preview = el("rf-preview-math"), previewEstado = el("rf-preview-status");
    const estado = { version: 0, funcion: null, analisis: null, aborto: null };
    // Los errores del paso 1 tienen su propio aviso: la vista previa reescribe su texto de estado.
    const errorFuncion = crear("p", undefined, "bis-message bis-error");
    errorFuncion.setAttribute("role", "alert");
    errorFuncion.hidden = true;
    formFuncion.append(errorFuncion);
    let previewTemporizador = null, previewAborto = null, previewVersion = 0;

    const grafica = crearGrafica({
      contenedor: el("rf-plot"), controles: el("rf-graph-controls"), lectura: el("rf-readout"),
      leyenda: el("rf-legend"), nivelZoom: el("rf-zoom-level"),
      botones: { acercar: el("rf-zoom-in"), alejar: el("rf-zoom-out"), restablecer: el("rf-zoom-reset") },
    }, {
      alElegir: indice => elegirIntervalo(estado.analisis.intervalos[indice]),
      alMarcar: (xl, xu) => { activarMarcado(false); elegirIntervalo({ xl, xu }); },
    });

    /* Muestra las tarjetas hasta el paso alcanzado y actualiza el indicador de progreso.
       "completo" marca también el último paso como terminado. */
    function fijarPaso(alcanzado, completo = false) {
      tarjetas.forEach((tarjeta, i) => { tarjeta.hidden = i + 1 > alcanzado; });
      pasos.forEach((paso, i) => {
        const numero = i + 1;
        paso.classList.toggle("is-done", numero < alcanzado || (completo && numero === alcanzado));
        if (numero === alcanzado && !completo) paso.setAttribute("aria-current", "step");
        else paso.removeAttribute("aria-current");
        paso.querySelector("button").disabled = numero > alcanzado;
      });
    }

    /* Cualquier cambio en un paso invalida los posteriores: se ocultan y se cancela lo pendiente.
       "visible" es el último paso que sigue a la vista (por defecto, el anterior al reiniciado). */
    function reiniciarDesde(paso, visible = Math.max(1, paso - 1)) {
      estado.version++;
      estado.aborto?.abort();
      estado.aborto = null;
      panel.querySelectorAll(".rf-action").forEach(boton => { boton.disabled = false; });
      for (let n = paso; n <= 4; n++) insignia(estados[n - 1], "Pendiente");
      tarjetaTabla.hidden = true;
      el("rf-table").replaceChildren();
      el("rf-result").replaceChildren();
      if (paso <= 2) {
        estado.funcion = estado.analisis = null;
        errorFuncion.hidden = true;
        grafica.limpiar();
        activarMarcado(false);
        estado.alAnalizar = null;
        el("rf-continuity").replaceChildren();
        el("rf-candidates").replaceChildren();
        formIntervalo.reset();
        insignia(estados[0], "Pendiente");
      }
      fijarPaso(visible);
    }

    /* Ejecuta la petición de un paso con su botón deshabilitado; descarta respuestas obsoletas. */
    async function ejecutar(numero, boton, ruta, datos, alTerminar) {
      const version = estado.version;
      estado.aborto = new AbortController();
      boton.disabled = true;
      insignia(estados[numero - 1], "Calculando…");
      try {
        const respuesta = await pedir(ruta, datos, estado.aborto.signal);
        if (version !== estado.version) return;
        alTerminar(respuesta);
      } catch (error) {
        if (version !== estado.version || error.name === "AbortError") return;
        insignia(estados[numero - 1], "Revise los datos", "badge-error");
        mostrarError(numero, error.message);
      } finally {
        if (version === estado.version) boton.disabled = false;
      }
    }

    function mostrarError(numero, mensaje) {
      if (numero === 1) {
        errorFuncion.textContent = mensaje;
        errorFuncion.hidden = false;
        return;
      }
      const destino = { 2: el("rf-continuity"), 3: el("rf-validation"), 4: el("rf-result") }[numero];
      destino.replaceChildren(crear("p", mensaje, "bis-message bis-error"));
    }

    function revelar(nodo) {
      requestAnimationFrame(() => nodo.scrollIntoView?.({ block: "nearest", behavior: "smooth" }));
    }

    function actualizarPreview() {
      clearTimeout(previewTemporizador);
      previewAborto?.abort();
      const actual = ++previewVersion;
      const funcion = formFuncion.elements.funcion.value.trim();
      preview.replaceChildren();
      if (!funcion) {
        previewEstado.textContent = "Escriba una función para ver su representación matemática.";
        return;
      }
      previewEstado.textContent = "Actualizando vista matemática…";
      previewTemporizador = setTimeout(async () => {
        previewAborto = new AbortController();
        try {
          const datos = await pedir("preview", { funcion }, previewAborto.signal);
          if (actual !== previewVersion) return;
          renderLatexElement(preview, `f(x) = ${datos.latex}`, true);
          previewEstado.textContent = "Vista de la función escrita. Presione «Graficar función» para estudiarla en la región.";
        } catch (error) {
          if (actual !== previewVersion || error.name === "AbortError") return;
          previewEstado.textContent = "Complete la expresión para actualizar la vista matemática.";
        }
      }, 200);
    }

    /* PASO 1: la función se grafica en la región de interés. */
    formFuncion.addEventListener("input", () => reiniciarDesde(2));
    formFuncion.elements.funcion.addEventListener("input", actualizarPreview);
    formFuncion.addEventListener("submit", evento => {
      evento.preventDefault();
      reiniciarDesde(2);
      const datos = Object.fromEntries(new FormData(formFuncion));
      ejecutar(1, el("rf-graficar"), "graficar", datos, respuesta => {
        estado.funcion = respuesta.funcion;
        estado.region = respuesta.intervalo;
        grafica.mostrar(respuesta);
        insignia(estados[0], "Gráfica lista", "badge-success");
        previewEstado.textContent = `Gráfica de la función en la región [${formatear(respuesta.intervalo[0], 6)}, ${formatear(respuesta.intervalo[1], 6)}].`;
        analizar();
      });
    });

    /* PASO 2: el sistema analiza la continuidad y propone intervalos; el usuario elige o define uno. */
    function analizar() {
      fijarPaso(2);
      el("rf-continuity").replaceChildren(crear("p", "Analizando la continuidad en la región…", "placeholder-text"));
      const [a, b] = estado.region;
      ejecutar(2, el("rf-enviar"), "analizar", { funcion: estado.funcion, a, b }, analisis => {
        estado.analisis = analisis;
        grafica.fijarAnalisis(analisis);
        renderizarContinuidad(analisis);
        renderizarCandidatos(analisis);
        const continua = analisis.continuidad.continua;
        insignia(estados[1], continua ? "Continua en la región" : "Discontinua en la región", continua ? "badge-success" : "badge-warning");
        if (estado.alAnalizar) estado.alAnalizar();
        else if (analisis.intervalos.length === 1) elegirIntervalo(analisis.intervalos[0]);
      });
    }

    function renderizarContinuidad({ continuidad }) {
      const [a, b] = continuidad.intervalo;
      const region = `$[${numeroLatex(a, 8)},\\; ${numeroLatex(b, 8)}]$`;
      const dictamen = crear("div", undefined, `rf-verdict${continuidad.continua ? "" : " is-warning"}`);
      const cantidad = continuidad.discontinuidades.length;
      dictamen.append(crear("strong", continuidad.continua ? "Sin discontinuidades detectadas"
        : `${cantidad === 1 ? "Se detectó una discontinuidad" : `Se detectaron ${cantidad} discontinuidades`}`));
      dictamen.append(crearMixto("span", continuidad.continua
        ? `$f$ se comporta como una función continua en ${region}. El análisis es numérico (${continuidad.muestras} muestras): confírmelo observando la gráfica.`
        : `$f$ no es continua en toda la región ${region}. Elija un intervalo que no contenga las discontinuidades señaladas en la gráfica.`));
      const nodos = [dictamen];
      if (cantidad) {
        const lista = crear("ul", undefined, "rf-list");
        continuidad.discontinuidades.slice(0, 8).forEach(d => lista.append(crearMixto("li", describirDiscontinuidad(d))));
        if (cantidad > 8) lista.append(crear("li", `… y ${cantidad - 8} más.`));
        nodos.push(lista);
        if (continuidad.tramos.length && continuidad.tramos.length <= 9) {
          nodos.push(crearMixto("p", `Tramos continuos: $${textoTramos(continuidad.tramos)}$.`, "rf-empty"));
        }
      }
      el("rf-continuity").replaceChildren(...nodos);
    }

    function renderizarCandidatos({ intervalos, raices_exactas: raices }) {
      const contenedor = el("rf-candidates");
      const nodos = intervalos.slice(0, 12).map((intervalo, indice) => {
        const boton = crear("button", `[${formatear(intervalo.xl, 8)}, ${formatear(intervalo.xu, 8)}]`, "rf-candidate");
        boton.type = "button";
        boton.dataset.indice = indice;
        boton.setAttribute("aria-pressed", "false");
        boton.append(crear("small", `Raíz cerca de x ≈ ${formatear(intervalo.raiz_aprox, 6)}`));
        boton.addEventListener("click", () => elegirIntervalo(intervalo));
        return boton;
      });
      if (intervalos.length > 12) nodos.push(crear("p", `Se muestran 12 de ${intervalos.length} intervalos. Reduzca la región para estudiar los demás.`, "rf-empty"));
      if (!intervalos.length) {
        nodos.push(crear("p", "No se detectó ningún cambio de signo de una función continua en la región. Amplíe la región en el paso 1 o defina el intervalo manualmente.", "rf-empty"));
      }
      const sinCruce = raices.filter(x => !intervalos.some(i => i.raiz_aprox === x));
      if (sinCruce.length) {
        nodos.push(crearMixto("p", `$f(x) = 0$ exactamente en $x = ${sinCruce.slice(0, 4).map(x => numeroLatex(x, 8)).join(",\\; ")}$${sinCruce.length > 4 ? ", …" : ""}; sin cambio de signo alrededor, la regla falsa no puede encerrar esa raíz.`, "rf-empty"));
      }
      contenedor.replaceChildren(...nodos);
    }

    function leerIntervalo() {
      const [xl, xu] = ["xl", "xu"].map(nombre => {
        const texto = formIntervalo.elements[nombre].value.trim();
        const partes = texto.split("/");
        return partes.length === 2 ? Number(partes[0]) / Number(partes[1]) : (texto === "" ? NaN : Number(texto));
      });
      return Number.isFinite(xl) && Number.isFinite(xu) && xl < xu ? [xl, xu] : null;
    }

    /* Refleja en la gráfica y en los botones el intervalo escrito en los campos. */
    function sincronizarIntervalo() {
      const intervalo = leerIntervalo();
      grafica.fijarIntervalo(intervalo);
      el("rf-candidates").querySelectorAll(".rf-candidate").forEach(boton => {
        const candidato = estado.analisis.intervalos[boton.dataset.indice];
        boton.setAttribute("aria-pressed", String(!!intervalo && candidato.xl === intervalo[0] && candidato.xu === intervalo[1]));
      });
    }

    function elegirIntervalo({ xl, xu }) {
      formIntervalo.elements.xl.value = String(xl);
      formIntervalo.elements.xu.value = String(xu);
      reiniciarDesde(3);
      sincronizarIntervalo();
    }

    function activarMarcado(activo) {
      el("rf-mark").setAttribute("aria-pressed", String(activo));
      grafica.marcar(activo);
    }

    el("rf-mark").addEventListener("click", () => activarMarcado(el("rf-mark").getAttribute("aria-pressed") !== "true"));
    formIntervalo.addEventListener("input", () => { reiniciarDesde(3); sincronizarIntervalo(); });
    formIntervalo.addEventListener("submit", evento => evento.preventDefault()); // el envío se conecta en el paso 3

    fijarPaso(1);
    actualizarPreview();
  });
})();
