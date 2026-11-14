/* Secante: gráfica, dos puntos manuales, sustitución e historial. */
(() => {
  "use strict";
  const G = typeof module !== "undefined" && module.exports ? require("./grafica-funciones.js") : window.GraficaFunciones;
  const num=G.numeroLatex;
  const MOTIVOS={tolerancia:"Se alcanzó la tolerancia del criterio seleccionado.",raiz_inicial:"Uno de los valores iniciales ya es una raíz.",raiz_evaluada:"La función se evaluó como cero en punto flotante.",denominador_nulo:"Las dos evaluaciones son iguales: el denominador es cero. Elija otros puntos.",divergencia:"El siguiente paso no es finito. Revise los puntos iniciales.",fuera_de_dominio:"La siguiente aproximación sale del dominio real de la función.",sin_progreso:"La precisión de punto flotante impide seguir avanzando.",ciclo:"Las aproximaciones forman un ciclo. Elija otros puntos.",max_iteraciones:"Se alcanzó el máximo de iteraciones sin cumplir la tolerancia."};
  function sustitucion(p) {return String.raw`x_{${p.n+1}}=${num(p.b)}-\frac{(${num(p.fb)})(${num(p.b)}-(${num(p.a)}))}{${num(p.fb)}-(${num(p.fa)})}\approx ${num(p.c)}`;}
  if(typeof module!=="undefined"&&module.exports)module.exports={sustitucion,MOTIVOS};
  if(typeof document==="undefined")return;
  document.addEventListener("DOMContentLoaded",()=>{
    const el=id=>document.getElementById(`sc-${id}`);
    const node=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n;};
    const math=(s,display=true)=>{const n=node(display?"div":"span");renderLatexElement(n,s,display);return n;};
    const mix=(s)=>{const n=node("p");renderMixedLatex(n,s);return n;};
    let funcion=null,puntos=[],vista=null,base=null,vistaBase=null,res=null,version=0,temporizador=null,marcando=null;
    const lienzo=document.createElementNS("http://www.w3.org/2000/svg","svg");
    Object.entries({viewBox:"0 0 600 330",role:"img",tabindex:"0","aria-label":"Función y rectas secantes. Use flechas para desplazar, más y menos para zoom e Inicio para restablecer."}).forEach(([k,v])=>lienzo.setAttribute(k,v));
    const requests=new Map();
    function cancel(){version++;requests.forEach(c=>c.abort());requests.clear();clearTimeout(temporizador);}
    function error(s){el("error").textContent=s;el("error").hidden=!s;}
    function clearResult(){res=null;el("result").replaceChildren();el("table-card").hidden=true;el("focus-root").disabled=true;draw();}
    function invalidate(level){cancel();navegacion.cancelar();error("");clearResult();if(level<=2){el("card-3").hidden=true;el("card-4").hidden=true;el("first").replaceChildren();}if(level===1){funcion=null;vista=null;vistaBase=null;base=null;puntos=[];marcar(null);el("graph-controls").hidden=true;el("readout").replaceChildren();el("card-2").hidden=true;el("plot").replaceChildren();el("hint").replaceChildren();}}
    async function request(route,data){
      requests.get(route)?.abort();const c=new AbortController(),v=version;requests.set(route,c);
      try{const r=await fetch(`/api/secante/${route}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data),signal:c.signal});const d=await r.json();if(v!==version||requests.get(route)!==c)return null;if(!r.ok)throw Error(d.error);return d;}
      finally{if(requests.get(route)===c)requests.delete(route);}
    }
    async function run(form,fn){const b=form.querySelector('[type="submit"]');b.disabled=true;error("");try{await fn();}catch(e){if(e.name!=="AbortError")error(e.message);}finally{b.disabled=false;}}
    const datos=()=>({funcion,x0:el("x0").value,x1:el("x1").value,tolerancia:el("tolerance").value,max_iteraciones:el("limit").value,criterio:document.querySelector('[name="sc-criterion"]:checked').value});
    function draw(){
      if(!vista)return;const e=G.crearEscala(vista),M=G.MARCO;
      const svg=(tag,a={},t)=>{const n=document.createElementNS("http://www.w3.org/2000/svg",tag);Object.entries(a).forEach(([k,v])=>n.setAttribute(k,v));if(t!==undefined)n.textContent=t;return n;};
      const s=lienzo;s.replaceChildren();
      const defs=svg("defs"),clip=svg("clipPath",{id:"sc-clip"});clip.append(svg("rect",{x:M.x,y:M.y,width:M.ancho,height:M.alto}));defs.append(clip);s.append(defs);
      for(const x of G.marcas(vista.xMin,vista.xMax))s.append(svg("line",{x1:e.x(x),x2:e.x(x),y1:M.y,y2:M.y+M.alto,class:"rf-grid"}),svg("text",{x:e.x(x),y:305,"text-anchor":"middle",class:"rf-tick"},G.formatear(x,5)));
      for(const y of G.marcas(vista.yMin,vista.yMax,5))s.append(svg("line",{x1:M.x,x2:M.x+M.ancho,y1:e.y(y),y2:e.y(y),class:"rf-grid"}),svg("text",{x:M.x-6,y:e.y(y),"text-anchor":"end",class:"rf-tick"},G.formatear(y,4)));
      const layer=svg("g",{"clip-path":"url(#sc-clip)"});
      const line=(x,y,xx,yy,cl)=>{const a=[e.x(x),e.y(y),e.x(xx),e.y(yy)];if(a.every(Number.isFinite))layer.append(svg("line",{x1:a[0],y1:a[1],x2:a[2],y2:a[3],class:cl}));};
      line(vista.xMin,0,vista.xMax,0,"bis-axis-zero");line(0,vista.yMin,0,vista.yMax,"bis-axis-zero");
      layer.append(svg("path",{d:G.caminoCurva(puntos,e),class:"bis-curve",fill:"none","stroke-width":2}));
      const dot=(x,y,cl="nr-point")=>{if([e.x(x),e.y(y)].every(Number.isFinite))layer.append(svg("circle",{cx:e.x(x),cy:e.y(y),r:3.5,class:cl}));};
      if(res){res.pasos.slice(0,8).forEach(p=>{line(p.a,p.fa,p.c,0,"nr-tangent");line(p.b,p.fb,p.c,0,"nr-tangent");line(p.c,0,p.c,p.fc,"nr-guide");dot(p.c,0);});line(res.raiz,vista.yMin,res.raiz,vista.yMax,"bis-root nr-guide");dot(res.raiz,0,"bis-root");}
      s.append(layer);const labels=node("div");labels.className="nr-labels";
      [[96,97,"x"],[9,7,"f(x)"]].forEach(([x,y,t])=>{const a=math(t,false);a.className="nr-plot-label";a.style.left=`${x}%`;a.style.top=`${y}%`;labels.append(a);});
      const colocadas=[];
      const label=(x,y,t)=>{const px=e.x(x),py=e.y(y);if(px<M.x||px>M.x+M.ancho||py<M.y+18||py>M.y+M.alto||colocadas.some(p=>Math.abs(p[0]-px)<65&&Math.abs(p[1]-py)<22))return;colocadas.push([px,py]);const n=math(t,false);n.className="nr-plot-label";n.style.left=`${px/6}%`;n.style.top=`${py/3.3}%`;labels.append(n);};
      for(const [id,n] of [["x0",0],["x1",1]]){const raw=el(id).value.trim(),partes=raw.split("/"),x=raw?Number(partes[0])/(partes.length===2?Number(partes[1]):1):NaN;if(!Number.isFinite(x)||partes.length>2)continue;const y=G.interpolar(puntos,x);line(x,vista.yMin,x,vista.yMax,"nr-guide");if(y!==null)dot(x,y);label(x,0,`x_${n}`);}
      if(res)label(res.raiz,vista.yMax-(vista.yMax-vista.yMin)*.13,`x_n\\approx ${num(res.raiz)}`);
      if(s.parentNode!==el("plot"))el("plot").replaceChildren(s,labels);
      else el("plot").querySelector(".nr-labels").replaceWith(labels);
      el("zoom-level").textContent=vistaBase?`${Math.round((vistaBase.xMax-vistaBase.xMin)/(vista.xMax-vista.xMin)*100)}%`:"100%";
    }
    async function graph(a,b){clearTimeout(temporizador);const d=await request("graficar",{funcion:funcion||el("function").value,a,b});if(!d)return;funcion=d.funcion;puntos=d.grafica;const [yMin,yMax]=G.rangoVertical(puntos);vista={xMin:d.intervalo[0],xMax:d.intervalo[1],yMin,yMax};el("card-2").hidden=false;draw();}
    el("graph-form").addEventListener("submit",e=>{e.preventDefault();invalidate(1);run(e.currentTarget,async()=>{await graph(el("a").value,el("b").value);if(vista){base=[vista.xMin,vista.xMax];vistaBase={...vista};el("graph-controls").hidden=false;draw();}});});
    ["function","a","b"].forEach(id=>el(id).addEventListener("input",()=>invalidate(1)));
    ["x0","x1"].forEach(id=>el(id).addEventListener("input",()=>{invalidate(2);draw();}));
    ["tolerance","limit"].forEach(id=>el(id).addEventListener("input",()=>invalidate(4)));
    document.querySelectorAll('[name="sc-criterion"]').forEach(n=>n.addEventListener("change",()=>invalidate(4)));
    el("initial-form").addEventListener("submit",e=>{e.preventDefault();invalidate(2);run(e.currentTarget,async()=>{
      const d=await request("evaluar",{...datos(),tolerancia:1e-300});if(!d)return;res=d;el("card-3").hidden=false;el("first").replaceChildren();
      if(d.pasos.length){const p=d.pasos[0];el("first").append(math(`f(${num(p.a)})=${num(p.fa)}\\qquad f(${num(p.b)})=${num(p.fb)}`),math(sustitucion(p)),mix("La secante corta el eje horizontal en la nueva aproximación. Ya puede iterar."));}
      else el("first").append(node("p",MOTIVOS[d.motivo]));
      el("card-4").hidden=!(d.pasos.length||d.convergio);draw();
    });});
    function result(d){
      const out=el("result");out.replaceChildren(node("h4",d.convergio?"Raíz calculada":"Sin convergencia"),node("p",MOTIVOS[d.motivo]));
      el("focus-root").disabled=false;
      out.append(math(`x_n\\approx ${num(d.raiz)}\\qquad |f(x_n)|=${num(d.residuo)}`),math(`E_a=${num(d.error_absoluto)}\\qquad \\varepsilon_r=${num(d.error_relativo)}`),mix(`Iteraciones: $${d.iteraciones}$.`));
      for(const [k,t]of Object.entries({absoluto:"E_a",relativo:"\\varepsilon_r",residuo:"|f(x_n)|"}))out.append(mix(`${d.cumple[k]?"✓":"✗"} $${t}<\\varepsilon$${k===d.criterio?" (seleccionado)":""}`));
      if(d.advertencias.length)out.append(mix(`Denominador pequeño en las iteraciones $${d.advertencias.join(",")}$: puede causar saltos grandes.`));
      const t=node("table"),h=node("thead"),hr=node("tr"),body=node("tbody");const headers=["n","x_{n-1}","x_n","x_{n+1}","|f(x_{n+1})|","E_a","\\varepsilon_r"];
      headers.forEach(v=>{const th=node("th");th.scope="col";th.append(math(v,false));hr.append(th);});hr.append(node("th","Detalle"));h.append(hr);
      d.pasos.forEach(p=>{const row=node("tr");[p.n,p.a,p.b,p.c,Math.abs(p.fc),p.error_absoluto,p.error_relativo].forEach((v,i)=>{const td=node("td");td.className="bis-cell";td.title=String(v??"No definido");const l=node("span");l.className="bis-cell-label";l.append(math(headers[i],false));td.append(l,math(num(v),false));row.append(td);});const td=node("td"),details=node("details");td.className="bis-detail-cell";details.append(node("summary","Ver detalle"),math(sustitucion(p)));td.append(details);row.append(td);body.append(row);});
      t.append(h,body);el("table").replaceChildren(t);el("table-card").hidden=false;
    }
    el("solve-form").addEventListener("submit",e=>{e.preventDefault();cancel();clearResult();run(e.currentTarget,async()=>{const d=await request("resolver",datos());if(!d)return;res=d;result(d);draw();if(d.raiz<vista.xMin||d.raiz>vista.xMax){const a=Math.min(...base,d.raiz),b=Math.max(...base,d.raiz),m=(b-a)*.1;await graph(a-m,b+m);}});});
    function cambiarVista(nueva){
      if(!vista)return;requests.get("graficar")?.abort();requests.delete("graficar");
      vista={...nueva};draw();clearTimeout(temporizador);
      temporizador=setTimeout(async()=>{try{const d=await request("graficar",{funcion,a:vista.xMin,b:vista.xMax});if(d){puntos=d.grafica;draw();}}catch(e){if(e.name!=="AbortError")error(e.message);}},140);
    }
    const navegacion=G.crearNavegacionGrafica({contenedor:el("plot"),obtenerVista:()=>vista,cambiarVista,
      restablecer:()=>{if(vistaBase)cambiarVista(vistaBase);},
      leer:x=>{const y=G.interpolar(puntos,x);renderLatexElement(el("readout"),`x=${num(x)}${y===null?"":String.raw`\qquad f(x)\approx ${num(y)}`}`,false);},
      elegir:x=>{if(!marcando)return;const input=el(marcando);input.value=String(G.redondearSegunVista(x,vista.xMax-vista.xMin));input.dispatchEvent(new Event("input",{bubbles:true}));marcar(null);}
    });
    function marcar(id){marcando=id;el("plot").classList.toggle("graph-marking",Boolean(id));for(const [boton,campo]of [["mark-x0","x0"],["mark-x1","x1"]])el(boton).setAttribute("aria-pressed",String(id===campo));}
    for(const [id,factor]of [["zoom-in",.7],["zoom-out",1/.7]])el(id).addEventListener("click",()=>navegacion.zoom(factor));
    el("reset").addEventListener("click",()=>{if(vistaBase)cambiarVista(vistaBase);});
    el("mark-x0").addEventListener("click",()=>marcar(marcando==="x0"?null:"x0"));
    el("mark-x1").addEventListener("click",()=>marcar(marcando==="x1"?null:"x1"));
    el("focus-root").addEventListener("click",()=>{if(!res)return;const margen=Math.max(Math.abs(res.raiz)*.03,.05),a=res.raiz-margen,b=res.raiz+margen;run(el("graph-form"),()=>graph(a,b));});
    for(const [id,f,b,hint]of [["example","x^3-x-2",2.5,"La presentación utiliza $x_0=1$, $x_1=2$. Escríbalos después de observar la gráfica."],["practice","x^3-2*x-5",3.5,"La práctica propone $x_0=2$, $x_1=3$ y tolerancia $10^{-6}$."]])el(id).addEventListener("click",()=>{invalidate(1);el("function").value=f;el("a").value=0;el("b").value=b;el("x0").value="";el("x1").value="";el("graph-form").requestSubmit();renderMixedLatex(el("hint"),hint);});
    el("clear").addEventListener("click",()=>{invalidate(1);["function","x0","x1"].forEach(id=>el(id).value="");el("function").focus();});
  });
})();
