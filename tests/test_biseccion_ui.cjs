/* Ejecutar: node --test tests/test_biseccion_ui.cjs (sin paquetes externos). */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { datosGrafica, formatear, EJEMPLOS } = require('../src/ui/web/biseccion.js');

test('formato distingue error indefinido, cero y valores pequeños', () => {
  assert.equal(formatear(null), '—');
  assert.equal(formatear(0), '0');
  assert.equal(formatear(1e-15), '1e-15');
  assert.equal(formatear(0.76392822265625), '0.7639282227');
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
