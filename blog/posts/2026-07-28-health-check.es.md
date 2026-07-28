---
title: La calidad de las alertas le gana a la cantidad
subtitle: Construir un monitoreo para un ERP que hace funcionar cuatro empresas en tres países
date: 2026-07-28
lang: es
slug: health-check
summary: Construir un monitoreo que cuadra el inventario contra la contabilidad cada seis horas, lo que encontró que ningún informe mostraba, y por qué una alerta que nadie acciona es un defecto y no una molestia.
tags: monitoreo, erp, observabilidad
---

Durante mucho tiempo, la forma en que nos enterábamos de que algo andaba mal en nuestro ERP era que alguien reclamaba.

    
Un contador notaba, cerrando el mes, que el inventario y la contabilidad no cuadraban. Un vendedor descubría que una factura electrónica había sido rechazada por la autoridad tributaria semanas antes y llevaba todo ese tiempo en una cola. Alguien se daba cuenta un miércoles de que el rango autorizado de folios para un tipo de documento se había agotado — lo que en un régimen de facturación regulada significa que simplemente no puedes facturar hasta que el regulador emita más.

    
Todos esos casos eran detectables con anticipación. Ninguno se detectó con anticipación, porque nada estaba mirando.

    
## Perseguir errores versus construir lo que los encuentra

    
Mi primer instinto fue arreglar cada problema a medida que aparecía. Eso es satisfactorio y no escala. Cada arreglo atendía una instancia de una clase de falla que yo no era capaz de enumerar, y el intervalo entre que la falla ocurría y alguien la notaba seguía siendo exactamente el mismo: semanas.

    
Así que dejé de arreglar casos individuales y construí un health check: una rutina programada que interroga al sistema con una cadencia fija y reporta lo que encuentra a quienes pueden actuar. Hoy corre unos cuarenta y seis detectores cada seis horas, con un subconjunto urgente cada treinta minutos.

    
Lo que miran los detectores cae en cuatro grupos:

    
- **Cuadratura.** El kardex de inventario y la contabilidad tienen que contar la misma historia. Para cada país y cada cuenta relevante, el detector calcula ambos lados y los compara contra un umbral apropiado a esa moneda. La divergencia se reporta con las transacciones que la causaron, no solo con un número.

      - **Estado regulatorio.** Documentos rechazados por una autoridad tributaria, documentos atascados esperando envío, y la fecha proyectada de agotamiento de cada rango de folios autorizado — de modo que "nos quedamos sin folios en nueve días" es algo que sabemos nueve días antes y no el mismo día.

      - **Salud del sistema.** Errores reales en el log del servidor, separados del ruido, más las tareas programadas que empezaron a fallar.

      - **Pulso del negocio.** Un resumen por país de lo que efectivamente se movió. No para alertar, sino para dar contexto, de modo que una anomalía pueda leerse contra un día normal.

    
## Lo que encontró

    
La primera corrida significativa sacó a la luz algo que nadie sabía: el costo de inventario se estaba registrando dos veces para una categoría de transacción. Dos partes independientes del sistema — un movimiento físico de stock y un proceso de liquidación — hacían cada una su trabajo honesto, y ambas acreditaban el mismo asiento contable.

    
Llevaba más de un año acumulándose. Ningún informe lo mostraba, porque cada informe individual era internamente consistente; la discrepancia solo existía *entre* dos vistas que nadie había puesto lado a lado. Esa es precisamente la clase de problema que un revisor humano nunca encuentra, porque encontrarlo exige comparar dos cosas que por separado se ven correctas.

    
De ahí salieron dos cosas. Las cifras históricas se corrigieron y, más importante, la cuadratura quedó permanente. La misma comparación corre ahora cada seis horas, así que si las condiciones que lo permitieron vuelven alguna vez, nos enteramos ese día y no al año siguiente.

    
## La regla que lo hizo funcionar

    
La tentación con un sistema así es medirlo por cobertura: cuántos detectores, cuántas alertas. Esa es la métrica equivocada, y seguirla produce algo peor que nada.

    
> 
Cada alerta tiene que producir una acción. Si una alerta se dispara y la respuesta correcta es ignorarla, eso es un defecto de mi detector — no una molestia que haya que tolerar.

    
Lo apliqué de forma literal. Todo detector que produjo una alerta que nadie accionó fue reescrito o eliminado. El razonamiento es simple: un canal que grita "lobo" enseña a la gente a ignorarlo, y el costo no es la atención desperdiciada — es la única alerta real que se ignora junto con el ruido. Un sistema de monitoreo con cien detectores que la gente hojea es estrictamente peor que uno con diez que la gente lee.

    
## Dónde me equivoqué

    
Uno de mis propios detectores fue el mejor argumento a favor de esta regla.

    
Construí uno para encontrar registros de inventario duplicados, usando la llave identificadora que la plataforma usa por estándar. Reportó miles de duplicados. Yo estaba convencido de haber encontrado algo grande.

    
Estaba equivocado, y de forma peligrosa. Nuestras bodegas de consignación separan el stock por dimensiones que la llave estándar no incluye: en qué local de qué cliente está, y qué compañía es su dueña. Registros que parecían idénticos bajo la llave estándar eran registros legítimamente distintos de tiendas diferentes. Actuar sobre mi propia alerta habría mezclado inventario perteneciente a clientes distintos en un solo montón: un problema mucho peor que el que creía estar arreglando.

    
Cuando volví a correr la comparación con la llave correcta, el conteo fue cero. Nunca hubo un problema. El detector se reescribió, y la restricción quedó escrita en negrita para que nadie — incluido mi yo futuro — lo repita.

    
Vuelvo a este caso seguido, porque hice todo bien desde el procedimiento: noté una anomalía, la cuantifiqué y preparé un arreglo. Lo que nos salvó fue que un colega me contradijera y que yo verificara antes de actuar. La confianza en un hallazgo no es evidencia a su favor.

    
## Cómo se ve el éxito de verdad

    
No es un dashboard. El resultado medible es poco vistoso: la cuadratura entre inventario y contabilidad se mantiene dentro del umbral en cada país, el resumen llega y es mayormente aburrido, y cuando no lo es, alguien actúa esa misma mañana.

    
La señal en la que más confío es de conducta. Ahora la gente revisa la alerta antes de revisar el sistema. El mecanismo de descubrimiento dejó de ser un usuario notando algo raro semanas después — y ese cambio, no el número de detectores, es todo el punto.
