const test=require('node:test');
const assert=require('node:assert/strict');
const {sustitucion}=require('../src/ui/web/secante.js');
const {prepararInsercionFormula:insert}=require('../src/ui/web/formula-keyboard.js');
const {vistaZoom,vistaDesplazada,crearNavegacionGrafica,MARCO}=require('../src/ui/web/grafica-funciones.js');
test('la secante representa la sustitución de la presentación con signos explícitos',()=>{
  assert.equal(sustitucion({n:1,a:1,b:2,fa:-2,fb:4,c:4/3}),String.raw`x_{2}=2-\frac{(4)(2-(1))}{4-(-2)}\approx 1.333333333`);
});
test('zoom conserva el punto bajo el cursor y rechaza escalas agotadas',()=>{
  const v={xMin:-2,xMax:8,yMin:-10,yMax:10};
  const z=vistaZoom(v,.5,0,5);
  assert.deepEqual(z,{xMin:-1,xMax:4,yMin:-2.5,yMax:7.5});
  assert.equal((0-z.xMin)/(z.xMax-z.xMin),(0-v.xMin)/(v.xMax-v.xMin));
  assert.deepEqual(vistaZoom(z,2,0,5),v);
  assert.equal(vistaZoom(v,1e-20),null);
  assert.equal(vistaZoom(v,Infinity),null);
  assert.deepEqual(vistaDesplazada(v,3,-2),{xMin:1,xMax:11,yMin:-12,yMax:8});
});
test('controlador compartido soporta rueda, teclado, arrastre y selección sin confundirlos',()=>{
  const handlers={};let v={xMin:0,xMax:10,yMin:0,yMax:10},selecciones=[],resets=0,focus=0;
  const svg={getBoundingClientRect:()=>({left:0,top:0,width:600,height:330}),focus:()=>focus++};
  const host={querySelector:()=>svg,addEventListener:(t,f)=>handlers[t]=f,setPointerCapture(){},hasPointerCapture:()=>true,releasePointerCapture(){},classList:{add(){},remove(){}}};
  crearNavegacionGrafica({contenedor:host,obtenerVista:()=>v,cambiarVista:n=>v=n,restablecer:()=>resets++,elegir:x=>selecciones.push(x)});
  const evt={clientX:MARCO.x+MARCO.ancho/2,clientY:MARCO.y+MARCO.alto/2,pointerId:1,button:0,preventDefault(){}};
  handlers.wheel({...evt,deltaY:-10});assert.ok(v.xMax-v.xMin<10);
  handlers.keydown({key:'ArrowUp',preventDefault(){}});assert.ok(v.yMax>10-1e-6);
  handlers.pointerdown(evt);handlers.pointermove({...evt,clientX:evt.clientX+30});handlers.pointerup({...evt,type:'pointerup',clientX:evt.clientX+30});
  assert.equal(selecciones.length,0);assert.equal(focus,1);
  handlers.pointerdown(evt);handlers.pointerup({...evt,type:'pointerup'});assert.equal(selecciones.length,1);
  handlers.keydown({key:'Home',preventDefault(){}});assert.equal(resets,1);
});
test('las funciones inversas se insertan con argumento y multiplicación a ambos lados',()=>{
  for(const f of ['asin','acos','atan']){
    assert.equal(insert('2x',1,1,f,'function').text,`*${f}()*`);
    assert.equal(insert(`${f}(x)`,0,0,'2','digit').text,'2*');
  }
});
