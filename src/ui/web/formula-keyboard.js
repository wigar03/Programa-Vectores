/* Teclado de bisección: edita la expresión del formulario sin traducir ni evaluar LaTeX. */
document.addEventListener("DOMContentLoaded", () => {
  "use strict";
  const input = document.getElementById("bis-funcion");
  const keyboard = document.getElementById("bis-keyboard");
  const toggle = document.getElementById("bis-keyboard-toggle");
  const status = document.getElementById("bis-keyboard-status");
  if (!input || !keyboard || !toggle) return;

  // Las plantillas mantienen la sintaxis admitida por el servidor y sitúan el cursor
  // dentro del argumento. Una selección se conserva como argumento de la función.
  const functions = [
    ["x", "Variable x", "x", "atom"],
    ["x^2", "Elevar al cuadrado", "square"],
    ["x^n", "Elevar a una potencia", "power"],
    [String.raw`\frac{a}{b}`, "Fracción", "fraction"],
    [String.raw`\sqrt{x}`, "Raíz cuadrada", "sqrt", "function"],
    ["|x|", "Valor absoluto", "abs", "function"],
    [String.raw`\pi`, "Constante pi", "pi", "atom"],
    ["e", "Constante e", "e", "atom"],
    [String.raw`\sin`, "Seno, en radianes", "sin", "function"],
    [String.raw`\cos`, "Coseno, en radianes", "cos", "function"],
    [String.raw`\tan`, "Tangente, en radianes", "tan", "function"],
    [String.raw`\ln`, "Logaritmo natural", "ln", "function"],
    [String.raw`\log_{10}`, "Logaritmo en base diez", "log", "function"],
    ["e^x", "Exponencial", "exp", "function"],
    ["(", "Abrir paréntesis", "(", "atom"],
    [")", "Cerrar paréntesis", ")", "literal"],
  ];
  const numbers = [
    ["7", "Siete", "7", "digit"], ["8", "Ocho", "8", "digit"], ["9", "Nueve", "9", "digit"], [String.raw`\div`, "Dividir", "/", "literal"],
    ["4", "Cuatro", "4", "digit"], ["5", "Cinco", "5", "digit"], ["6", "Seis", "6", "digit"], [String.raw`\times`, "Multiplicar", "*", "literal"],
    ["1", "Uno", "1", "digit"], ["2", "Dos", "2", "digit"], ["3", "Tres", "3", "digit"], ["-", "Restar", "-", "literal"],
    ["0", "Cero", "0", "digit"], [".", "Punto decimal", ".", "literal"], ["⌫", "Borrar selección o carácter anterior", "backspace", "action"], ["+", "Sumar", "+", "literal"],
  ];

  function change(text, start, end, cursorStart, cursorEnd = cursorStart) {
    if (input.value.length - (end - start) + text.length > input.maxLength) {
      status.textContent = `La función admite hasta ${input.maxLength} caracteres.`;
      return;
    }
    input.setRangeText(text, start, end, "end");
    input.focus({ preventScroll: true });
    input.setSelectionRange(cursorStart, cursorEnd);
    // El módulo invalida los resultados anteriores y actualiza KaTeX por su ruta habitual.
    input.dispatchEvent(new Event("input", { bubbles: true }));
    status.textContent = "";
  }

  function press(value, kind) {
    const start = input.selectionStart, end = input.selectionEnd;
    const selected = input.value.slice(start, end);
    const left = input.value.slice(0, start).trimEnd();
    const atomBefore = /(?:\d|\)|\bx|\bpi|\be)$/.test(left);
    const variableBefore = /(?:\)|\bx|\bpi|\be)$/.test(left);
    let text = value, cursor;
    if (kind === "action") {
      input.focus({ preventScroll: true });
      if (value === "left" || value === "right") {
        const position = value === "left" ? (start !== end ? start : Math.max(0, start - 1)) : (start !== end ? end : Math.min(input.value.length, end + 1));
        input.setSelectionRange(position, position);
      } else if (value === "select") input.select();
      else if (value === "backspace") change("", start === end ? Math.max(0, start - 1) : start, end, start === end ? Math.max(0, start - 1) : start);
      return;
    }
    if (kind === "function") {
      text = `${value}(${selected})`;
      cursor = selected ? text.length : value.length + 1;
    } else if (value === "fraction") {
      text = `(${selected})/()`;
      cursor = selected ? text.length - 1 : 1;
    } else if (value === "power") {
      text = selected ? `(${selected})^()` : "^()";
      cursor = text.length - 1;
    } else if (value === "square") {
      text = selected ? `(${selected})^2` : "^2";
    }
    // Multiplicación explícita al concatenar átomos: 2×x, 2×sin(x), x×3.
    if (((kind === "atom" || kind === "function" || value === "fraction") && atomBefore) || (kind === "digit" && variableBefore)) {
      text = "*" + text;
      if (cursor !== undefined) cursor++;
    }
    change(text, start, end, start + (cursor ?? text.length));
  }

  function group(label, keys, className) {
    const group = document.createElement("div");
    group.className = className;
    group.setAttribute("role", "group");
    group.setAttribute("aria-label", label);
    for (const [latex, label, value, kind] of keys) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "bis-key";
      button.dataset.key = value;
      button.title = label;
      button.setAttribute("aria-label", label);
      if (kind === "action") button.textContent = latex;
      else renderLatexElement(button, latex, false);
      button.addEventListener("pointerdown", event => event.preventDefault());
      button.addEventListener("click", () => press(value, kind));
      group.append(button);
    }
    keyboard.append(group);
  }
  group("Funciones y símbolos", functions, "bis-key-functions");
  group("Números y operaciones", numbers, "bis-key-numbers");
  group("Edición de la expresión", [
    ["←", "Mover cursor a la izquierda", "left", "action"],
    ["→", "Mover cursor a la derecha", "right", "action"],
    ["Seleccionar todo", "Seleccionar toda la expresión", "select", "action"],
  ], "bis-key-edit");

  function show(visible) {
    keyboard.hidden = !visible;
    toggle.setAttribute("aria-expanded", String(visible));
    toggle.textContent = visible ? "Ocultar teclas" : "Mostrar teclas";
  }
  toggle.addEventListener("click", () => show(keyboard.hidden));
  input.closest(".bis-formula-editor").addEventListener("keydown", event => {
    if (event.key === "Escape" && !keyboard.hidden) {
      event.preventDefault();
      show(false);
      input.focus({ preventScroll: true });
    }
  });
});
