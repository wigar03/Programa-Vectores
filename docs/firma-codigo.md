# Code signing policy

## Estado actual

La distribución `v1.0.0-rc.1` no tiene firma digital del equipo. Puede ser bloqueada
por Smart App Control. No se ha solicitado ni obtenido la aprobación de SignPath
Foundation; este documento prepara los requisitos para evaluar esa solicitud.

La licencia abierta del código propio está pendiente de selección por el equipo.
Las dependencias mantienen sus licencias y atribuciones originales.

## Preparación de la solicitud

Según las [condiciones de SignPath Foundation](https://signpath.org/terms), antes
de solicitar el servicio se deben completar estos puntos:

- Publicar una licencia aprobada por OSI para el código propio.
- Revisar la elegibilidad de las dependencias y los componentes redistribuidos.
- Identificar públicamente autores con acceso de escritura, revisores y personas
  autorizadas para aprobar cada solicitud de firma. Esos roles están por designar.
- Confirmar autenticación multifactor de los miembros que participen en la firma.
- Incluir nombre del producto y versión en los metadatos de los ejecutables propios.
- Vincular los binarios a la revisión del código y al build verificable de GitHub Actions.

La aceptación del proyecto depende de la evaluación de la fundación. La licencia
abierta por sí sola no garantiza la aprobación ni elimina los bloqueos de Windows.

## Reglas para una futura distribución firmada

Cada solicitud de firma deberá contar con aprobación manual de un responsable
designado. Se firmarán únicamente los artefactos propios autorizados del proyecto;
se conservarán las firmas y atribuciones de los componentes de terceros.

Los paquetes finales se comprobarán con Smart App Control activado, incluida la
instalación, apertura de los diez módulos y desinstalación. Las sumas de descarga
se calcularán después de firmar. Una firma no sustituye las pruebas de funcionamiento.

## Privacidad y componentes externos

Los cálculos se procesan en la computadora del usuario. La aplicación no incorpora
telemetría propia ni un servicio de cuentas. El setup puede descargar WebView2 si
falta; el runtime de Microsoft tiene sus propios mecanismos de actualización.
Se deben revisar y declarar los términos aplicables de esos componentes en la
solicitud y en cualquier futura política de privacidad.

Cuando exista aprobación efectiva del proveedor, se actualizarán aquí el estado,
los responsables, la atribución del servicio y el procedimiento de firma.
