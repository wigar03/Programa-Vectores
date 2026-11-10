/* Ejecutar: node --test tests/test_regla_falsa_ui.cjs (sin paquetes externos). */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const rf = require('../src/ui/web/regla-falsa.js');

const { MARCO, formatear, numeroLatex, marcas, rangoVertical, crearEscala, caminoCurva,
  interpolar, redondearSegunVista } = rf;

test('formato con cifras configurables y notación científica en LaTeX', () => {
  assert.equal(formatear(null), '—');
  assert.equal(formatear(5.236055081129443), '5.236055081');
  assert.equal(formatear(5.236055081129443, 6), '5.23606');
  assert.equal(formatear(0.30000000000000004, 6), '0.3');
  assert.equal(numeroLatex(-1e-15), String.raw`-1 \times 10^{-15}`);
  assert.equal(numeroLatex(-38.263118749999975, 6), '-38.2631');
  assert.equal(numeroLatex(null), String.raw`\text{—}`);
});

test('marcas de los ejes usan pasos redondos y cubren la vista', () => {
  assert.deepEqual(marcas(0, 6), [0, 1, 2, 3, 4, 5, 6]);
  assert.deepEqual(marcas(-10, 10), [-10, -5, 0, 5, 10]);
  assert.deepEqual(marcas(0, 1.3), [0, 0.2, 0.4, 0.6, 0.8, 1, 1.2]);
  assert.deepEqual(marcas(-98.7, 187.2, 5), [-50, 0, 50, 100, 150]);
  assert.deepEqual(marcas(1e-9, 2e-9, 4), [1e-9, 1.2e-9, 1.4e-9, 1.6e-9, 1.8e-9, 2e-9]);
  assert.deepEqual(marcas(3, 3), []);
  assert.deepEqual(marcas(0, Infinity), []);
});

test('rango vertical incluye el eje X y deja margen', () => {
  const [minimo, maximo] = rangoVertical([{ x: 0, y: 2 }, { x: 1, y: 10 }]);
  assert.ok(minimo < 0 && minimo > -1);
  assert.ok(maximo > 10 && maximo < 11);
  assert.deepEqual(rangoVertical([]), [-1, 1]);
  assert.deepEqual(rangoVertical([{ x: 0, y: null }]), [-1, 1]);
  assert.deepEqual(rangoVertical([{ x: 0, y: 0 }, { x: 1, y: 0 }]), [-1, 1]);
  assert.deepEqual(rangoVertical([{ x: 0, y: -1e308 }, { x: 1, y: 1e308 }]), [-1e308, 1e308]);
});

test('rango vertical recorta los valores extremos junto a una asíntota', () => {
  // tan(x) muestreada: casi todos los valores son moderados y unos pocos, enormes.
  const puntos = Array.from({ length: 401 }, (_, i) => {
    const x = -5 + i / 40;
    return { x, y: Math.tan(x) };
  });
  const [minimo, maximo] = rangoVertical(puntos);
  assert.ok(Math.max(...puntos.map(p => Math.abs(p.y))) > 100);
  assert.ok(minimo > -40 && maximo < 40);
  assert.ok(minimo < -5 && maximo > 5);
});

test('la escala lleva la vista al marco y es invertible', () => {
  const escala = crearEscala({ xMin: 0, xMax: 6, yMin: -100, yMax: 200 });
  assert.equal(escala.x(0), MARCO.x);
  assert.equal(escala.x(6), MARCO.x + MARCO.ancho);
  assert.equal(escala.y(200), MARCO.y);
  assert.equal(escala.y(-100), MARCO.y + MARCO.alto);
  assert.ok(Math.abs(escala.xInversa(escala.x(2.5)) - 2.5) < 1e-12);
  assert.ok(Math.abs(escala.yInversa(escala.y(42)) - 42) < 1e-9);
  const enorme = crearEscala({ xMin: 0, xMax: 1, yMin: -1e308, yMax: 1e308 });
  assert.equal(enorme.y(0), MARCO.y + MARCO.alto / 2);
});

test('la curva no une puntos separados por el dominio, un corte o un salto de toda la vista', () => {
  const escala = crearEscala({ xMin: -1, xMax: 1, yMin: -10, yMax: 10 });
  const tramos = camino => (camino.match(/M/g) || []).length;
  const continua = [{ x: -1, y: -5 }, { x: 0, y: 0 }, { x: 1, y: 5 }];
  assert.equal(tramos(caminoCurva(continua, escala)), 1);
  assert.equal(tramos(caminoCurva([{ x: -1, y: -5 }, { x: 0, y: null }, { x: 1, y: 5 }], escala)), 2);
  assert.equal(tramos(caminoCurva(continua, escala, [0.5])), 2);
  // 1/x alrededor de 0: de muy abajo a muy arriba entre dos muestras vecinas.
  const asintota = [{ x: -1, y: -1 }, { x: -0.01, y: -100 }, { x: 0.01, y: 100 }, { x: 1, y: 1 }];
  assert.equal(tramos(caminoCurva(asintota, escala)), 2);
  assert.ok(!/NaN|Infinity/.test(caminoCurva([{ x: -1, y: -1e308 }, { x: 1, y: 1e308 }], escala)));
});

test('interpolación lineal de f para la lectura del cursor', () => {
  const puntos = [{ x: 0, y: 0 }, { x: 1, y: 2 }, { x: 2, y: null }, { x: 3, y: 6 }];
  assert.equal(interpolar(puntos, 0.25), 0.5);
  assert.equal(interpolar(puntos, 1), 2);
  assert.equal(interpolar(puntos, 1.5), null);
  assert.equal(interpolar(puntos, -1), null);
  assert.equal(interpolar(puntos, 4), null);
  assert.equal(interpolar([], 0), null);
});

test('una posición marcada se redondea según el ancho visible', () => {
  assert.equal(redondearSegunVista(4.94987, 6), 4.95);
  assert.equal(redondearSegunVista(0.0123456, 0.02), 0.01235);
  assert.equal(redondearSegunVista(1234.5678, 5000), 1235);
  assert.equal(Object.is(redondearSegunVista(-0.0001, 6), 0), true);
});

test('las discontinuidades se describen según su tipo', () => {
  const { describirDiscontinuidad } = rf;
  assert.equal(describirDiscontinuidad({ tipo: 'asintota', x: 1.5707963, desde: 1.5707963, hasta: 1.5707963 }),
    String.raw`Asíntota vertical en $x \approx 1.5707963$.`);
  assert.equal(describirDiscontinuidad({ tipo: 'salto', x: 0, desde: 0, hasta: 0 }), String.raw`Salto en $x \approx 0$.`);
  assert.equal(describirDiscontinuidad({ tipo: 'punto_indefinido', x: 0, desde: 0, hasta: 0 }), '$f$ no está definida en $x = 0$.');
  assert.equal(describirDiscontinuidad({ tipo: 'fuera_de_dominio', x: -0.5, desde: -1, hasta: 0 }),
    '$f$ no está definida entre $x = -1$ y $x = 0$.');
});

test('los tramos continuos se escriben como unión de intervalos abiertos o cerrados', () => {
  const tramos = [
    { desde: -1, hasta: 0, abierto_izquierda: false, abierto_derecha: true },
    { desde: 0, hasta: 1.3, abierto_izquierda: true, abierto_derecha: false },
  ];
  assert.equal(rf.textoTramos(tramos), String.raw`[-1,\; 0) \cup (0,\; 1.3]`);
  assert.equal(rf.textoTramos([]), '');
});

test('los ejemplos guiados definen región, intervalo y tolerancia', () => {
  for (const ejemplo of Object.values(rf.EJEMPLOS)) {
    assert.deepEqual(Object.keys(ejemplo), ['funcion', 'a', 'b', 'xl', 'xu', 'tolerancia']);
    assert.ok(Number(ejemplo.a) <= Number(ejemplo.xl) && Number(ejemplo.xu) <= Number(ejemplo.b));
  }
  assert.equal(rf.EJEMPLOS.referencia.xl, '4.95');
  assert.equal(rf.EJEMPLOS.potencia.funcion, 'x^10 - 1');
});
