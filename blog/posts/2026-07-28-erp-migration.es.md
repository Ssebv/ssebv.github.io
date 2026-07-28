---
title: Los errores que sobreviven a una actualización de ERP son los silenciosos
subtitle: Migrar cinco versiones mayores en cuatro empresas y tres países
date: 2026-07-28
lang: es
slug: erp-migration
summary: Migrar cinco versiones mayores en cuatro empresas y tres países. Las fallas que lanzaron errores se arreglaron en días; las que cambiaron el comportamiento sin lanzar nada duraron semanas.
tags: odoo, migracion, erp
---

El ERP del que soy responsable hace funcionar cuatro empresas en Chile, Colombia y Perú. Contiene el inventario, la contabilidad, las órdenes de compra y venta, y la facturación electrónica que tres autoridades tributarias distintas exigen por ley. Cuando se detiene, las bodegas dejan de despachar y las facturas dejan de emitirse — lo que, en países donde facturar es un acto regulado, no es una molestia sino un problema de cumplimiento.

    
Ese sistema iba cinco versiones mayores atrasado. Ponerlo al día significaba migrar la base de datos, reescribir el código custom contra una API distinta y recertificar la facturación electrónica ante tres reguladores — sin perder un registro y sin una ventana lo bastante larga como para que alguien lo notara.

    
La migración en sí salió bien. De lo que quiero escribir es de lo que vino después, porque ahí estuvo la lección real.

    
## La forma del problema

    
La instalación tenía unos 228 módulos, de los cuales 41 eran código custom escrito durante años por varias manos. Buena parte del trabajo previo a tocar nada fue arqueología: leer cada módulo custom para decidir qué seguía sosteniendo la operación, qué estaba muerto y qué se había convertido en un duplicado de algo que la plataforma ya hacía de forma nativa. Cuarenta y un módulos custom quedaron en dieciocho.

    
La consolidación no fue orden por el orden. Cada módulo custom que sobrescribe un modelo estándar es una apuesta a que ese modelo no va a cambiar por debajo. Cinco versiones son muchos cambios. Mientras menos apuestas abiertas haya en el cutover, menos formas tiene la actualización de sorprenderte.

    
El cutover corrió por la ruta nativa de actualización, primero contra una copia de producción y después de verdad. La identidad de la base de datos se preservó, no se perdió nada y no hubo vuelta atrás.

    
## Entonces empezaron las fallas silenciosas

    
Me había preparado para que la actualización rompiera cosas ruidosamente — un traceback, un módulo que se niega a cargar, una factura que no publica. Esas son las fallas fáciles. Se anuncian solas, las arreglas y sigues. Casi ninguno de los problemas reales se comportó así.

    
El ejemplo más claro fue un solo campo. En la versión antigua, una línea de factura que representaba un producto real tenía el `display_type` vacío; los encabezados de sección y las notas llevaban un valor. Así que el código escrito a lo largo del sistema filtraba las líneas de producto de la forma obvia: *toma las líneas donde display_type está vacío*. En la versión nueva, las líneas de producto dejaron de estar vacías y pasaron a llevar un valor propio y explícito.

    
Nada falló. Los filtros siguieron corriendo. Simplemente dejaron de devolver nada, para siempre. Código que llevaba años funcionando siguió ejecutándose, siguió reportando éxito y procesó cero registros.

    
Ese único cambio produjo tres errores distintos antes de que entendiera el patrón: un PDF que dejó de compactar sus líneas en silencio, una rutina de consolidación para documentos que superan el límite de líneas del regulador y que dejó de consolidar, y un formato de ticket que perdió su contenido. Tres síntomas, tres áreas, una causa — y ninguno lanzó una excepción.

    
Una vez reconocido, el arreglo fue mecánico: auditar *cada* filtro heredado de la versión anterior que tocara ese campo, y hacer que acepte ambas formas. Lo caro no fue el arreglo. Fueron las semanas entre la actualización y el momento en que supe dónde mirar.

    
## Otras cuatro formas de quedarse callado

    
El mismo patrón — sin error, comportamiento equivocado — apareció en formas que no había anticipado:

    
- **Tareas programadas que sobrevivieron a su código.** Definiciones de trabajos de la versión anterior sobrevivieron a la actualización aunque el método que llamaban ya no existiera. Cada corrida fallaba en silencio. Solo se veían buscando trabajos con contador de fallos mayor que cero; nada los sacaba a la superficie por sí solo.

      - **Campos computados almacenados que se desincronizaron sin avisar.** Algunos campos cachean un valor copiado desde otro lado. La actualización cambió varias de esas fuentes sin recalcular las copias, así que ambas discrepaban. Todo se veía normal hasta que un informe cruzó las dos.

      - **Comportamiento nuevo de la plataforma chocando con supuestos viejos.** Una rutina nocturna estándar ganó un paso que "repara" las reservas de inventario. Nuestras bodegas de consignación violan ese invariante a propósito, por buenas razones. El choque solo corría de noche, así que el primer síntoma apareció más de veinticuatro horas después del cambio que lo causó — que es exactamente el tiempo suficiente para dejar de sospechar del cambio.

      - **Código que nunca se estaba ejecutando.** Dos módulos de nuestro repositorio compartían nombre con módulos que la plataforma ahora incluye. Gana la versión de la plataforma. Así que un módulo que yo podía leer, editar y commitear no tenía efecto alguno sobre el sistema en ejecución. Antes de arreglar nada, verifica que el archivo que estás leyendo sea el que realmente se ejecuta.

    
## El que más me enseñó

    
Una vista de lista nueva que agregué para un país se convirtió, sin que nadie la tocara, en la vista de lista por defecto de ese tipo de registro en todo el sistema — en las cuatro compañías.

    
La razón es casi graciosa. Las vistas se ordenan por prioridad y luego por nombre. Mi vista nueva tenía la misma prioridad que la estándar, y su nombre resultó ordenar antes alfabéticamente. Ese fue todo el mecanismo. Usuarios de otros dos países empezaron a ver columnas de un tipo de documento que no existe en su país, y como la lista era editable, un clic perdido podía modificar un registro.

    
No hay arreglo ingenioso. Se le pone una prioridad baja explícita a toda vista nueva que no deba convertirse en la por defecto. Pero jamás habría predicho que un desempate alfabético pudiera reasignar una pantalla usada por cuatro compañías, y ninguna cantidad de pruebas sobre mi propia funcionalidad lo habría detectado, porque desde donde yo estaba la funcionalidad andaba perfecta.

    
> 
::: note
**La lección generalizable:** después de una actualización mayor, las fallas que lanzan errores se arreglan en días porque el sistema te avisa. Las que cambian el comportamiento sin lanzar nada pueden durar meses, porque el modelo mental de todos dice que el código "funciona" — y sí corre, solo que ya no hace lo que dice. Tras una actualización, la pregunta correcta no es "¿qué se rompió?" sino "¿qué sigue corriendo y ahora significa otra cosa?".
:::

    
## Qué hago distinto ahora

    
**Trato el silencio como no verificado, no como éxito.** Si una rutina reporta que procesó registros, reviso el conteo. Un trabajo que dice "listo" sin haber hecho nada es el estado más caro en el que puede estar un sistema.

    
**Reviso los logs del día siguiente, no los de la hora siguiente.** Cualquier cosa que corra de noche va a fallar un día más tarde que el cambio que la causó, y para entonces todos pasaron a otra cosa.

    
**Documento cada hallazgo como regla, no como anécdota.** Cada uno de estos quedó escrito en el repositorio, redactado como algo que hay que revisar y no como algo que pasó. Quien herede este sistema no debería tener que redescubrir que un desempate alfabético puede secuestrar una pantalla.

    
**Y construí el monitoreo que habría atrapado la mayoría.** Ese es el [otro trabajo](./health-check.html) — un conjunto de detectores que cuadran lo que el sistema cree contra lo que dice la contabilidad, de forma programada, para que el mecanismo de descubrimiento deje de ser un usuario notando algo raro semanas después.
