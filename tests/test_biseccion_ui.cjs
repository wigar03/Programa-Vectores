/* Ejecutar: node --test tests/test_biseccion_ui.cjs (sin paquetes externos). */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { datosGrafica, formatear, numeroLatex, EJEMPLOS } = require('../src/ui/web/biseccion.js');

test('formato distingue error indefinido, cero y valores pequeños', () => {
  assert.equal(formatear(null), '—');
  assert.equal(formatear(0), '0');
  assert.equal(formatear(1e-15), '1e-15');
  assert.equal(formatear(0.76392822265625), '0.7639282227');
});

test('notación científica en LaTeX conserva signo, exponente y precisión solicitada', () => {
  assert.equal(numeroLatex(-1e-15), String.raw`-1 \times 10^{-15}`);
  assert.equal(numeroLatex(1e21), String.raw`1 \times 10^{21}`);
  assert.equal(numeroLatex(0.76392822265625), '0.7639282227');
  assert.equal(numeroLatex(0.76392822265625, true), '0.76392822265625');
  assert.equal(numeroLatex(0), '0');
  assert.equal(numeroLatex(null), String.raw`\text{—}`);
});

test('gráfica separa segmentos fuera del dominio sin unirlos', () => {
  const datos = datosGrafica({ intervalo_inicial: [-1, 1], intervalo_final: [-.1, .1], raiz: 0, f_raiz: 0,
    grafica: [{ x: -1, y: -1 }, { x: 0, y: null }, { x: 1, y: 1 }] });
  assert.equal((datos.camino.match(/M/g) || []).length, 2);
  assert.ok(!datos.camino.includes('L'));
  assert.equal(datos.raizX, 315);
});

test('gráfica evita desbordamiento al escalar números grandes de signos opuestos', () => {
  const datos = datosGrafica({ intervalo_inicial: [0, 1], intervalo_final: [.4, .6], raiz: .5, f_raiz: 0,
    grafica: [{ x: 0, y: -1e308 }, { x: .5, y: 0 }, { x: 1, y: 1e308 }] });
  assert.ok(!/NaN|Infinity/.test(datos.camino));
  assert.ok(Number.isFinite(datos.eje));
  assert.equal(datos.maximo, 1e308);
  assert.equal(datos.minimo, -1e308);
});

test('ejemplos definen criterio y unidades de tolerancia', () => {
  assert.equal(EJEMPLOS.hoja.criterio, 'residuo');
  assert.equal(EJEMPLOS.hoja.a, '0.6');
  assert.equal(EJEMPLOS.potencia.criterio, 'relativo');
});

test('datosGrafica admite opciones de intervalo y reescalado para zoom interactivo', () => {
  const caso = { intervalo_inicial: [0, 10], intervalo_final: [4.8, 5.2], raiz: 5, f_raiz: 0,
    grafica: [{ x: 0, y: 0 }, { x: 5, y: 0 }, { x: 10, y: 10 }] };
  const base = datosGrafica(caso);
  const zoomIn = datosGrafica(caso, { intervalo: [4, 6] });
  assert.equal(base.raizX, 315);
  assert.equal(zoomIn.raizX, 315);
  // En zoom in sobre [4, 6], la franja de ancho 0.4 ocupa mayor proporción que en [0, 10]
  assert.ok(zoomIn.bandaAncho > base.bandaAncho);
});
