# SAP — Estabilidad y Transformación · Tablero Ejecutivo DXC

Tablero ejecutivo de la operación SAP que DXC Technology gestiona para
Coca-Cola FEMSA. Dieciséis secciones con avance por scroll: alertas e
incidentes, MTTR, RFCs, transportes por sistema y remediación de
vulnerabilidades. **Corte: junio 2026.**

**En vivo:** https://antoniolopezlabra-boop.github.io/sap-tablero-ejecutivo/

---

## Versión pública

Esta es la **versión enmascarada** del tablero. Las cifras de operación
—volúmenes, MTTR, porcentajes de éxito, series mensuales— están
**intactas**; lo que se retiró es aquello que permitiría señalar un
servidor concreto o una vulnerabilidad concreta:

| Original | Aquí |
|---|---|
| 10 hostnames reales (`haerpp10`, `hl113q10`, …) | Identificadores genéricos por rol (`SRV-ERP-01`, `SRV-DB-01`, …), consistentes en todo el tablero |
| Folios de nota SAP a 7 dígitos | `Nota 01` … `Nota 12` |
| Columna de remediaciones pendientes por nota | Retirada; queda sistemas, implementadas y % de avance |

Los agregados del programa de seguridad (59 % de avance, 315
remediaciones, 130 pendientes) se conservan: son la tesis de esa sección
y, sin nota ni servidor al que atribuirlos, no señalan nada.

El archivo maestro con los datos reales vive en un repositorio privado
aparte.

---

## El entregable

`index.html` — **un archivo de 263 KB**. Se abre con doble clic en
cualquier laptop corporativa: sin servidor, sin build, sin permisos de TI.
La única petición de red es Google Fonts; si no carga, el tablero cae a
las tipografías del sistema y sigue siendo legible.

## Cómo está construido

Sin framework. HTML + CSS + JavaScript clásico (sin módulos ES, por
diseño — se bloquean en `file://`), 694 líneas en total.

| Componente | Versión | Peso |
|---|---|---|
| Chart.js (build UMD, embebido) | 4.4.6 | 206 KB |
| chartjs-plugin-datalabels (embebido) | 2.2.0 | 13 KB |
| Código de aplicación | — | 15 KB |

Ambas librerías van **inlineadas** dentro del archivo, no enlazadas a un
CDN: por eso el tablero funciona sin internet una vez cargadas las fuentes.

### Estructura del código de aplicación

- **`DATA`** — todas las series en un objeto literal: alertas, incidentes
  y requerimientos a 13 meses, MTTR, transportes por sistema, % de RFCs
  exitosos, clasificación trimestral de RFCs, top 10 de alertas
  recurrentes y tabla de remediación.
- **`BUILD`** — 11 constructores de gráficas: 8 de barras, 1 de línea, 2
  combinadas barra+línea y 1 de dona. Se instancian de forma perezosa: un
  `IntersectionObserver` crea cada gráfica sólo cuando su sección está al
  menos 60 % visible.
- **`countUp()`** — animación de cifras con `requestAnimationFrame` y
  easing cúbico.
- **Navegación** — 16 `<section>` con `scroll-snap`, barra de progreso,
  riel de puntos generado en JS y teclas `↑` `↓` `PgUp` `PgDn`.

Todo respeta `prefers-reduced-motion`: con esa preferencia activa se
apagan las animaciones de Chart.js, el count-up y el scroll suave.

## Diseño

Comparte el sistema de diseño de PANORAMA: los mismos tokens de color DXC
(`--amber #FFAE41`, `--coral #FF7E51`, `--rust #D14600`, `--blue #004AAC`,
`--navy #0E1020`) y la misma tipografía display, Space Grotesk.

## Publicación

GitHub Pages desde la rama `main`, carpeta raíz. El archivo `.nojekyll`
evita que Pages procese el HTML con Jekyll y lo sirva alterado.

---
*KOF × DXC Technology*
