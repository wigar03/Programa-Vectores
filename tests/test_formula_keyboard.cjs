/* Ejecutar: node --test tests/test_formula_keyboard.cjs (sin paquetes externos). */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { prepararInsercionFormula } = require('../src/ui/web/formula-keyboard.js');

function insert(expression, start, end, value, kind) {
  const result = prepararInsercionFormula(expression, start, end, value, kind);
  return { expression: expression.slice(0, start) + result.text + expression.slice(end), cursor: result.cursor };
}

test('insertar abs y un número antes del polinomio conserva una expresión válida', () => {
  const polynomial = 'x^4 - 5*x^3 + 0.5*x^2 - 11*x + 10';
  const fn = insert(polynomial, 0, 0, 'abs', 'function');
  assert.equal(fn.expression, 'abs()*' + polynomial);
  assert.equal(fn.cursor, 4);
  const digit = insert(fn.expression, fn.cursor, fn.cursor, '5', 'digit');
  assert.equal(digit.expression, 'abs(5)*' + polynomial);
  assert.equal(digit.cursor, 5);
});

test('insertar coeficientes antes de variables deja el cursor para continuar el número', () => {
  let result = insert('x^2', 0, 0, '5', 'digit');
  assert.equal(result.expression, '5*x^2');
  assert.equal(result.cursor, 1);
  result = insert(result.expression, result.cursor, result.cursor, '2', 'digit');
  assert.equal(result.expression, '52*x^2');
  assert.equal(insert('cos(x)', 0, 0, '3', 'digit').expression, '3*cos(x)');
  assert.equal(insert('(x+1)', 0, 0, '2', 'digit').expression, '2*(x+1)');
});

test('símbolos y funciones insertados en medio se multiplican a ambos lados', () => {
  assert.equal(insert('23', 1, 1, 'x', 'atom').expression, '2*x*3');
  assert.equal(insert('2x', 1, 1, 'sqrt', 'function').expression, '2*sqrt()*x');
  assert.equal(insert('x', 0, 0, 'pi', 'atom').expression, 'pi*x');
  assert.equal(insert('2', 0, 0, 'fraction', undefined).expression, '()/()*2');
});

test('envolver una selección conserva el argumento, operadores y posición del cursor', () => {
  assert.deepEqual(insert('x+1', 0, 3, 'sqrt', 'function'), { expression: 'sqrt(x+1)', cursor: 9 });
  assert.deepEqual(insert('x+1', 0, 3, 'power', undefined), { expression: '(x+1)^()', cursor: 7 });
  assert.deepEqual(insert('x+1', 0, 3, 'fraction', undefined), { expression: '(x+1)/()', cursor: 7 });
  assert.equal(insert('x+1', 2, 3, '2', 'digit').expression, 'x+2');
  assert.equal(insert('x*x', 0, 1, 'abs', 'function').expression, 'abs(x)*x');
});

test('los números, decimales y operadores conservan su significado', () => {
  assert.equal(insert('123', 1, 1, '5', 'digit').expression, '1523');
  assert.equal(insert('0.25', 3, 3, '7', 'digit').expression, '0.275');
  assert.equal(insert('1e-3', 1, 1, '2', 'digit').expression, '12e-3');
  assert.equal(insert('1E+3', 1, 1, '2', 'digit').expression, '12E+3');
  assert.equal(insert('sin()', 4, 4, '3', 'digit').expression, 'sin(3)');
  assert.equal(insert('x+2', 2, 2, '-', 'literal').expression, 'x+-2');
  assert.equal(insert('2', 1, 1, '(', 'atom').expression, '2*(');
});
