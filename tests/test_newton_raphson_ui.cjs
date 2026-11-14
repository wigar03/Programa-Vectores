const test = require('node:test');
const assert = require('node:assert/strict');
const { leerNumero, primeraLatex, detalleLatex, compararErrores, EJEMPLOS } = require('../src/ui/web/newton-raphson.js');
test('entrada manual admite decimales, fracciones y exponentes sin inventar valores', () => {
  for (const [s,n] of [['3/2',1.5],['1e-3',.001],['-.5',-.5],['0',0]]) assert.equal(leerNumero(s),n);
  for (const s of ['', ' ', 'NaN', 'Infinity', '1/0', '/2', '0x10', '1/2/3']) assert.equal(leerNumero(s),null);
});
test('primera iteración usa la sustitución de la presentación', () => {
  const lines=primeraLatex({x0:1.5,f_x0:-.125,df_x0:5.75,x1:1.5217391304347827});
  assert.equal(lines[1],String.raw`x_1=1.5-\frac{-0.125}{5.75}`);
  assert.match(lines[2],/1\.52173913/);
  assert.deepEqual(primeraLatex({x0:0,f_x0:-4,df_x0:0,x1:null}),[]);
});
test('detalle y comparación de errores contemplan cero y magnitudes menores que uno', () => {
  assert.match(detalleLatex({n:1,x:0,error_absoluto:1,error_relativo:null},{x:1,fx:1,dfx:1})[2],/no definido/);
  assert.match(compararErrores(.1,.05,2),/menor/);
  assert.match(compararErrores(.1,.2,.5),/mayor/);
  assert.match(compararErrores(.1,.1,1),/coinciden/);
  assert.match(compararErrores(0,0,2),/cero/);
});
test('los ejemplos nunca proporcionan un valor inicial al formulario', () => {
  Object.values(EJEMPLOS).forEach(e => { assert.equal(e.x0,undefined); assert.ok(e.funcion); });
});
