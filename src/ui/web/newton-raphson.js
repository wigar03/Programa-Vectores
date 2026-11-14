/* Newton-Raphson. El servidor deriva y calcula; la gráfica solo orienta la elección. */
(() => {
  "use strict";
  const G = typeof module !== "undefined" && module.exports ? require("./grafica-funciones.js") : window.GraficaFunciones;
  const { MARCO: M, numeroLatex: num, marcas, rangoVertical, crearEscala, caminoCurva, interpolar, redondearSegunVista } = G;
  const EJEMPLOS = {
    referencia: { funcion: "x^3 - x - 2", a: 0, b: 2.5, ayuda: "En la presentación se parte de $x_0=1.5$. Observe la gráfica y decida su valor inicial." },
    practica: { funcion: "x^3 - 2*x - 5", a: 0, b: 3.5, ayuda: "La práctica propone $x_0=2$ y tolerancia $10^{-6}$. Introduzca el punto que haya elegido." },
    ciclo: { funcion: "x^3 - 2*x + 2", a: -3, b: 2, ayuda: "Pruebe $x_0=0$: la sucesión alterna entre $0$ y $1$. Con $x_0=-2$ converge." },
  };
  const MOTIVOS = {
    valido: "La tangente en $x_0$ corta el eje horizontal en $x_1$. Ya puede iterar el método.",
    raiz_en_x0: "$f(x_0)=0$: el punto elegido ya es una raíz; no se requieren iteraciones.",
    raiz_evaluada: "$f(x_n)$ se evaluó como cero con la precisión de punto flotante utilizada.",
    tolerancia: "Se alcanzó la tolerancia del criterio seleccionado. Revise también el residuo y los otros errores.",
    derivada_nula: "$f'(x_n)=0$: la tangente es horizontal y la fórmula no está definida. Elija otro valor inicial.",
    derivada_no_definida: "La derivada no se puede evaluar en este punto. Elija otro valor inicial.",
    fuera_de_dominio: "Una aproximación queda fuera del dominio real de la función. Elija otro valor inicial.",
    divergencia: "La siguiente aproximación no es finita. Elija otro valor inicial.",
    ciclo: "Las aproximaciones se repiten: el método entró en un ciclo. Elija otro valor inicial.",
    sin_progreso: "La precisión de punto flotante impide seguir avanzando. El criterio elegido no acredita convergencia.",
    max_iteraciones: "Se alcanzó el máximo de iteraciones sin cumplir la tolerancia. Revise el punto inicial o el límite.",
  };
  function leerNumero(texto) {
    if (!String(texto).trim()) return null;
    const partes = String(texto).trim().split("/");
    const decimal = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i;
    if (partes.length > 2 || partes.some(p => !decimal.test(p.trim()))) return null;
    const n = Number(partes[0]) / (partes.length === 2 ? Number(partes[1]) : 1);
    return Number.isFinite(n) ? n : null;
  }
  function primeraLatex(p) {
    if (p.x1 === null || p.df_x0 === null || p.df_x0 === 0) return [];
    return [String.raw`f(${num(p.x0)})=${num(p.f_x0)}\qquad f'(${num(p.x0)})=${num(p.df_x0)}`,
      String.raw`x_1=${num(p.x0)}-\frac{${num(p.f_x0)}}{${num(p.df_x0)}}`,
      String.raw`x_1\approx ${num(p.x1)}`];
  }
  function detalleLatex(p, q) {
    return [String.raw`x_{${p.n}}=${num(q.x)}-\frac{${num(q.fx)}}{${num(q.dfx)}}\approx ${num(p.x)}`,
      String.raw`E_a=\left|${num(p.x)}-(${num(q.x)})\right|=${num(p.error_absoluto)}`,
      p.x === 0 ? String.raw`\varepsilon_r:\;\text{no definido}` : String.raw`\varepsilon_r=\frac{${num(p.error_absoluto)}}{|${num(p.x)}|}=${num(p.error_relativo)}`];
  }
  function compararErrores(ea, er, x) {
    if (ea === null || er === null) return "El error relativo no está definido para esta aproximación.";
    if (ea === 0) return "Ambos cambios son cero con la precisión utilizada.";
    if (Math.abs(x) > 1) return "El error relativo es menor que el absoluto ($\\varepsilon_r<E_a$) porque $|x_n|>1$.";
    if (Math.abs(x) < 1) return "El error relativo es mayor que el absoluto ($\\varepsilon_r>E_a$) porque $|x_n|<1$.";
    return "Ambos errores coinciden porque $|x_n|=1$.";
  }
  if (typeof module !== "undefined" && module.exports) module.exports = { leerNumero, primeraLatex, detalleLatex, compararErrores, EJEMPLOS, MOTIVOS };
  if (typeof document === "undefined") return;

  const el = id => document.getElementById(`nr-${id}`);
  const crear = (tag, texto, clase) => {
    const n = document.createElement(tag);
    if (texto !== undefined) n.textContent = texto;
    if (clase) n.className = clase;
    return n;
  };
  function mixto(tag, texto, clase) { const n = crear(tag, undefined, clase); renderMixedLatex(n, texto); return n; }
  function math(texto, display = true) { const n = crear(display ? "div" : "span"); renderLatexElement(n, texto, display); return n; }
  function svg(tag, attrs = {}, texto) {
    const n = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (const [k,v] of Object.entries(attrs)) n.setAttribute(k,v);
    if (texto !== undefined) n.textContent = texto;
    return n;
  }
  document.addEventListener("DOMContentLoaded", () => {
    const estado = { funcion: null, preparado: null, inicial: null, resultado: null, puntos: [], vista: null, base: null, marcado: false, paso: 1 };
    const solicitudes = new Map();
    let revision = 0, temporizador;
    function cancelar() {
      revision++;
      navegacion.cancelar();
      solicitudes.forEach(c => c.abort()); solicitudes.clear(); clearTimeout(temporizador);
    }
    function mensajeError(texto) { el("error").textContent = texto; el("error").hidden = !texto; }
    async function pedir(ruta, datos, canal = ruta) {
      solicitudes.get(canal)?.abort();
      const control = new AbortController(); solicitudes.set(canal, control);
      const turno = revision;
      try {
        const r = await fetch(`/api/newton-raphson/${ruta}`, { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(datos), signal: control.signal });
        const d = await r.json();
        if (turno !== revision || solicitudes.get(canal) !== control) return null;
        if (!r.ok || d.error) throw new Error(d.error || "No se pudo completar el cálculo.");
        return d;
      } finally { if (solicitudes.get(canal) === control) solicitudes.delete(canal); }
    }
    async function ejecutar(form, accion) {
      const boton = form.querySelector('[type="submit"]'); boton.disabled = true; mensajeError("");
      try { await accion(); } catch(e) { if (e.name !== "AbortError") mensajeError(e.message); }
      finally { boton.disabled = false; }
    }
    function pasos(n) {
      estado.paso = n;
      for (let i = 2; i <= 4; i++) el(`card-${i}`).hidden = i > n;
      document.querySelectorAll("[data-nr-step]").forEach(b => {
        const k = Number(b.dataset.nrStep); b.disabled = k > n;
        b.parentElement.classList.toggle("is-done", k < n);
        if (k === n) b.parentElement.setAttribute("aria-current", "step"); else b.parentElement.removeAttribute("aria-current");
      });
    }
    function limpiarResultado() {
      estado.resultado = null; el("result").replaceChildren(); el("table-card").hidden = true;
      el("focus-root").disabled = true;
    }
    function invalidarInicial() {
      cancelar(); estado.inicial = null; limpiarResultado(); el("first").replaceChildren();
      pasos(estado.preparado ? 2 : 1); dibujar();
    }
    function invalidarFuncion() {
      cancelar(); estado.funcion = null; estado.preparado = null; estado.inicial = null;
      estado.vista = null; estado.base = null; limpiarResultado(); pasos(1);
      el("derivative").replaceChildren(); el("plot").hidden = true; el("graph-controls").hidden = true;
      el("readout").replaceChildren(); el("hint").replaceChildren(); mensajeError(""); marcar(false);
    }
    function marcar(activo) {
      estado.marcado = activo;
      el("mark").setAttribute("aria-pressed",String(activo)); el("plot").classList.toggle("nr-marking",activo);
    }
    function ecoInicial() {
      const x = leerNumero(el("x0").value), y = x === null ? null : interpolar(estado.puntos,x);
      el("initial-preview").replaceChildren(...(x === null ? [] : [math(`x_0=${num(x)}${y === null ? "" : String.raw`\quad f(x_0)\approx ${num(y)}`}`)]));
      dibujar();
    }
    const lienzo = svg("svg", {viewBox:"0 0 600 330",role:"img",tabindex:"0","aria-label":"Función y tangentes de Newton-Raphson. Puede elegir el punto inicial escribiéndolo en el formulario."});
    const defs = svg("defs"), clip = svg("clipPath",{id:"nr-clip"});
    clip.append(svg("rect",{x:M.x,y:M.y,width:M.ancho,height:M.alto})); defs.append(clip);
    const grid = svg("g"), curva = svg("path",{class:"bis-curve",fill:"none","stroke-width":2,"clip-path":"url(#nr-clip)"}), trazos = svg("g",{"clip-path":"url(#nr-clip)"});
    lienzo.append(defs,grid,curva,trazos);
    const etiquetas = crear("div",undefined,"nr-labels"); el("plot").append(lienzo,etiquetas);
    function dibujar() {
      if (!estado.vista) return;
      const v=estado.vista, e=crearEscala(v), der=M.x+M.ancho, abajo=M.y+M.alto;
      grid.replaceChildren(); trazos.replaceChildren(); etiquetas.replaceChildren();
      const usados=[];
      function label(x,y,texto) {
        if (x<20 || x>580 || y<15 || y>320 || usados.some(p=>Math.abs(p[0]-x)<58 && Math.abs(p[1]-y)<18)) return;
        usados.push([x,y]); const n=math(texto,false); n.className="nr-plot-label"; n.style.left=`${x/6}%`; n.style.top=`${y/3.3}%`; etiquetas.append(n);
      }
      function linea(x1,y1,x2,y2,clase) {
        const coords=[e.x(x1),e.y(y1),e.x(x2),e.y(y2)];
        if (coords.every(Number.isFinite)) trazos.append(svg("line",{x1:coords[0],y1:coords[1],x2:coords[2],y2:coords[3],class:clase}));
      }
      function punto(x,y,clase="nr-point") {
        if (Number.isFinite(e.x(x)) && Number.isFinite(e.y(y))) trazos.append(svg("circle",{cx:e.x(x),cy:e.y(y),r:3.5,class:clase}));
      }
      for(const x of marcas(v.xMin,v.xMax)) grid.append(svg("line",{x1:e.x(x),x2:e.x(x),y1:M.y,y2:abajo,class:"rf-grid"}),svg("text",{x:e.x(x),y:abajo+18,"text-anchor":"middle",class:"rf-tick"},G.formatear(x,5)));
      for(const y of marcas(v.yMin,v.yMax,5)) grid.append(svg("line",{x1:M.x,x2:der,y1:e.y(y),y2:e.y(y),class:"rf-grid"}),svg("text",{x:M.x-6,y:e.y(y)+4,"text-anchor":"end",class:"rf-tick"},G.formatear(y,4)));
      linea(v.xMin,0,v.xMax,0,"bis-axis-zero"); linea(0,v.yMin,0,v.yMax,"bis-axis-zero");
      curva.setAttribute("d",caminoCurva(estado.puntos,e));
      label(der,abajo+38,"x"); label(M.x,18,"f(x)");
      const x0=leerNumero(el("x0").value);
      if(x0!==null) {
        const y=estado.inicial?.f_x0 ?? interpolar(estado.puntos,x0);
        linea(x0,v.yMin,x0,v.yMax,"nr-guide"); if(y!==null) punto(x0,y);
        label(e.x(x0),e.y(0)-7,"x_0");
      }
      const p=estado.inicial;
      if(p && p.valido && p.df_x0!==null && p.x1!==null) {
        linea(v.xMin,p.f_x0+p.df_x0*(v.xMin-p.x0),v.xMax,p.f_x0+p.df_x0*(v.xMax-p.x0),"nr-tangent");
        punto(p.x1,0); label(e.x(p.x1),e.y(0)+25,"x_1");
      }
      const res=estado.resultado;
      if(res) {
        res.pasos.slice(1,9).forEach((q,i)=>{
          const a=res.pasos[i]; linea(a.x,a.fx,q.x,0,"nr-tangent"); linea(q.x,0,q.x,q.fx,"nr-guide"); punto(q.x,0);
          label(e.x(q.x),e.y(0)+25,`x_{${q.n}}`);
        });
        linea(res.raiz,v.yMin,res.raiz,v.yMax,"bis-root nr-guide"); punto(res.raiz,0,"bis-root");
        label(e.x(res.raiz),M.y+35,`x_n\\approx ${num(res.raiz)}`);
      }
    }
    async function muestrear() {
      if(!estado.vista || !estado.funcion) return;
      const v=estado.vista;
      try {
        const d=await pedir("graficar",{funcion:estado.funcion,a:v.xMin,b:v.xMax},"grafica");
        if(!d) return;
        estado.puntos=d.grafica; dibujar();
      } catch(e) { if(e.name!=="AbortError") mensajeError(e.message); }
    }
    function cambiarVista(a,b) {
      const nueva=typeof a === "object" ? {...a} : {...estado.vista,xMin:a,xMax:b};
      a=nueva.xMin;b=nueva.xMax;
      if(!Number.isFinite(a) || !Number.isFinite(b) || b-a<1e-12 || b-a>1e12 || !estado.vista) return;
      // Cancelar el muestreo anterior en el momento del cambio, antes del debounce.
      solicitudes.get("grafica")?.abort(); solicitudes.delete("grafica");
      estado.vista=nueva; dibujar(); clearTimeout(temporizador); temporizador=setTimeout(muestrear,140);
    }
    const navegacion=G.crearNavegacionGrafica({
      contenedor:el("plot"), obtenerVista:()=>estado.vista,
      cambiarVista:v=>cambiarVista(v),
      restablecer:()=>{if(estado.baseVista)cambiarVista(estado.baseVista);},
      leer:x=>{const y=interpolar(estado.puntos,x);renderLatexElement(el("readout"),`x=${num(x)}${y===null?"":String.raw`\qquad f(x)\approx ${num(y)}`}`,false);},
      elegir:x=>{if(!estado.marcado)return;el("x0").value=String(redondearSegunVista(x,estado.vista.xMax-estado.vista.xMin));invalidarInicial();ecoInicial();marcar(false);}
    });
    el("zoom-in").addEventListener("click",()=>navegacion.zoom(.7));
    el("zoom-out").addEventListener("click",()=>navegacion.zoom(1/.7));
    el("reset-view").addEventListener("click",()=>{if(estado.baseVista)cambiarVista(estado.baseVista);});
    el("mark").addEventListener("click",()=>marcar(!estado.marcado));
    el("focus-root").addEventListener("click",()=>{
      const r=estado.resultado;if(!r)return;
      const margen=Math.max(Math.abs(r.raiz)*.03,.05);cambiarVista(r.raiz-margen,r.raiz+margen);
    });

    el("function-form").addEventListener("submit",e=>{
      e.preventDefault(); invalidarFuncion();
      ejecutar(e.currentTarget,async()=>{
        const d=await pedir("preparar",{funcion:el("function").value,a:el("a").value,b:el("b").value}); if(!d)return;
        estado.funcion=d.funcion; estado.preparado=d; estado.puntos=d.grafica; estado.base=d.intervalo;
        const [yMin,yMax]=rangoVertical(d.grafica); estado.vista={xMin:d.intervalo[0],xMax:d.intervalo[1],yMin,yMax}; estado.baseVista={...estado.vista};
        el("derivative").replaceChildren(crear("h4","Derivada de la función"),math(`f(x)=${d.funcion_latex}`),math(`f'(x)=${d.derivada_latex}`),crear("p","Derivada lista · Revise la pendiente antes de elegir el valor inicial","bis-help"));
        const sintaxis=crear("details"); sintaxis.append(crear("summary","Ver sintaxis de la derivada"),crear("code",d.derivada)); el("derivative").append(sintaxis);
        pasos(2); el("plot").hidden=false; el("graph-controls").hidden=false; marcar(true); ecoInicial();
      });
    });
    ["function","a","b"].forEach(id=>el(id).addEventListener("input",invalidarFuncion));
    el("x0").addEventListener("input",()=>{invalidarInicial(); ecoInicial();});
    el("initial-form").addEventListener("submit",e=>{
      e.preventDefault(); invalidarInicial();
      ejecutar(e.currentTarget,async()=>{
        const p=await pedir("evaluar",{funcion:estado.funcion,x0:el("x0").value}); if(!p)return;
        estado.inicial=p; marcar(false); pasos(p.valido?4:3);
        const salida=el("first"); salida.replaceChildren(mixto("p",MOTIVOS[p.estado],`rf-verdict${p.valido?"":" is-warning"}`));
        if(p.f_x0!==null)salida.append(math(`x_0=${num(p.x0)}\\qquad f(x_0)=${num(p.f_x0)}`));
        if(p.estado!=="raiz_en_x0") primeraLatex(p).forEach(t=>salida.append(math(t)));
        if(p.derivada_pequena)salida.append(mixto("p","$|f'(x_0)|<10^{-6}$: una tangente casi horizontal puede causar un salto excesivo.","rf-note"));
        if(p.x1!==null && (p.x1<estado.vista.xMin || p.x1>estado.vista.xMax))salida.append(mixto("p","$x_1$ queda fuera de la región graficada. Revise la magnitud del salto.","rf-note"));
        dibujar();
      });
    });
    function tabla(r) {
      const headers=["n","x_n","f(x_n)","f'(x_n)","E_a","\\varepsilon_r"];
      const t=crear("table"), head=crear("thead"), hr=crear("tr"), body=crear("tbody");
      headers.forEach(h=>{const th=crear("th"); th.scope="col"; th.append(math(h,false)); hr.append(th);}); hr.append(crear("th","Detalle")); head.append(hr);
      r.pasos.forEach((p,i)=>{
        const tr=crear("tr"); [p.n,p.x,p.fx,p.dfx,p.error_absoluto,p.error_relativo].forEach((v,j)=>{
          const td=crear("td",undefined,"bis-cell"); td.title=String(v??"No definido");
          const label=crear("span",undefined,"bis-cell-label"); label.append(math(headers[j],false)); td.append(label,math(num(v),false)); tr.append(td);
        });
        const td=crear("td",undefined,"bis-detail-cell");
        const extra=crear("tr",undefined,"bis-detail-row"); extra.hidden=true;
        if(i){const boton=crear("button","Ver detalle","btn-text"); boton.type="button"; boton.setAttribute("aria-expanded","false"); extra.id=`nr-detail-${i}`; boton.setAttribute("aria-controls",extra.id); boton.addEventListener("click",()=>{extra.hidden=!extra.hidden; boton.setAttribute("aria-expanded",String(!extra.hidden));}); td.append(boton);
          const cell=crear("td"); cell.colSpan=7; const box=crear("div",undefined,"nr-detail"); detalleLatex(p,r.pasos[i-1]).forEach(s=>box.append(math(s))); cell.append(box); extra.append(cell);}
        tr.append(td); body.append(tr); if(i)body.append(extra);
      });
      t.append(head,body); el("table").replaceChildren(t); el("table-card").hidden=false;
    }
    function resultado(r) {
      const out=el("result"); out.replaceChildren(crear("p",r.convergio?"Raíz calculada":"Sin convergencia","badge"),mixto("p",MOTIVOS[r.motivo],"rf-verdict"));
      const dl=crear("dl",undefined,"nr-summary");
      [[r.convergio?"Raíz aproximada $x_n$":"Última aproximación $x_n$",r.raiz],["Residuo $|f(x_n)|$",r.residuo],["Error absoluto $E_a$",r.error_absoluto],["Error relativo $\\varepsilon_r$",r.error_relativo],["Iteraciones",r.iteraciones]].forEach(([titulo,valor])=>{const box=crear("div"), dd=crear("dd"); dd.title=String(valor??"No definido"); dd.append(math(num(valor),false)); box.append(mixto("dt",titulo),dd); dl.append(box);}); out.append(dl);
      out.append(crear("strong","Criterios al terminar"));
      const criterios={absoluto:"E_a",relativo:"\\varepsilon_r",residuo:"|f(x_n)|"};
      Object.entries(criterios).forEach(([k,v])=>out.append(mixto("p",`${r.cumple[k]?"✓":"✗"} $${v}<\\varepsilon$${r.criterio===k?" (seleccionado)":""}${k!=="residuo"&&r[k==="absoluto"?"error_absoluto":"error_relativo"]===null?" · no definido":""}`,"bis-help")));
      out.append(mixto("p",compararErrores(r.error_absoluto,r.error_relativo,r.raiz),"bis-help"),math(`f(x_n)\\approx ${num(r.f_raiz)}`));
      const grupos={}; r.advertencias.forEach(a=>(grupos[a.tipo]??=[]).push(a.n));
      if(grupos.derivada_pequena)out.append(mixto("p",`Derivada pequeña en $n=${grupos.derivada_pequena.join(",")}$: puede producir saltos grandes.`,"rf-note"));
      if(grupos.paso_creciente)out.append(mixto("p",`El cambio aumentó en $n=${grupos.paso_creciente.join(",")}$: revise la convergencia.`,"rf-note"));
      if(r.raiz<estado.base[0] || r.raiz>estado.base[1])out.append(crear("p","La aproximación final está fuera de la región graficada inicialmente.","rf-note"));
      const ver=crear("button","Ver la raíz en la gráfica","btn-text"); ver.type="button"; ver.addEventListener("click",()=>el("graph-card").scrollIntoView({block:"start"})); out.append(ver);
      tabla(r); el("focus-root").disabled=false;
    }
    el("solve-form").addEventListener("submit",e=>{
      e.preventDefault(); limpiarResultado();
      ejecutar(e.currentTarget,async()=>{
        const r=await pedir("resolver",{funcion:estado.funcion,x0:el("x0").value,tolerancia:el("tolerance").value,max_iteraciones:el("limit").value,criterio:document.querySelector('[name="nr-criterion"]:checked').value}); if(!r)return;
        estado.resultado=r; resultado(r); dibujar();
        const v=estado.vista;
        if(Math.min(r.x0,r.raiz)<v.xMin || Math.max(r.x0,r.raiz)>v.xMax){const a=Math.min(estado.base[0],r.x0,r.raiz),b=Math.max(estado.base[1],r.x0,r.raiz),m=(b-a)*.1; cambiarVista(a-m,b+m);}
      });
    });
    ["tolerance","limit"].forEach(id=>el(id).addEventListener("input",()=>{cancelar();limpiarResultado();dibujar();}));
    document.querySelectorAll('[name="nr-criterion"]').forEach(n=>n.addEventListener("change",()=>{cancelar();limpiarResultado();dibujar();}));
    document.querySelectorAll("[data-nr-step]").forEach(b=>b.addEventListener("click",()=>el(`card-${b.dataset.nrStep}`).scrollIntoView({block:"start"})));
    document.querySelectorAll("[data-nr-example]").forEach(b=>b.addEventListener("click",()=>{
      const ej=EJEMPLOS[b.dataset.nrExample]; invalidarFuncion(); el("x0").value="";
      el("function").value=ej.funcion; el("a").value=ej.a; el("b").value=ej.b;
      el("function-form").requestSubmit(); renderMixedLatex(el("hint"),ej.ayuda);
    }));
    el("clear").addEventListener("click",()=>{invalidarFuncion();el("function").value="";el("x0").value="";el("initial-preview").replaceChildren();el("function").focus();});
  });
})();
