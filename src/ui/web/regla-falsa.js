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

  // Exporta solo las utilidades puras para verificarlas con el runner estándar de Node.
  if (typeof module !== "undefined" && module.exports) {
    module.exports = {
      MARCO, formatear, numeroLatex, marcas, rangoVertical, crearEscala, caminoCurva,
      interpolar, redondearSegunVista,
    };
  }
  if (typeof document === "undefined") return;
})();
