# FuelFinder CV — Diseño

**Fecha:** 2026-09-21
**Autor:** Néstor Soriano López
**Estado:** Implementado el mismo día

## Objetivo

Proyecto rápido para un post de LinkedIn con repercusión, alineado con un perfil de datos y
backend. Sustituye a `radar-junior-tech`, aparcado porque InfoJobs tiene cerrado el registro de su
API y Adzuna no cubre el mercado español (ver el spec de aquel proyecto).

**Pregunta:** ¿cuánto cuesta repostar en una gasolinera de marca frente a una low-cost en la
Comunitat Valenciana?

## Validación previa (la lección de radar-junior-tech)

Antes de diseñar se comprobó que la fuente responde y que el titular existe en los datos:

- La API del Ministerio responde sin registro y tiene **histórico diario de al menos seis meses**.
- El titular se sostiene los siete días de la semana analizada (sobreprecio en Valencia entre 26 y
  28 cts/L), no solo en una foto.

## Decisiones

| Decisión | Motivo |
|---|---|
| Solo Comunitat Valenciana | Elección de Néstor: ángulo local, donde busca trabajo. |
| Media de 7 días del histórico | Una única descarga es frágil; el histórico permite publicar hoy con una semana de datos. |
| Clasificación conservadora | Ante la duda, fuera de la comparación: ningún error puede inflar el titular. |
| Hipermercados separados de low-cost | Son baratos, pero mezclarlos sería rebatible. |
| Distancias en línea recta, declaradas | Sin API de rutas; se dice explícitamente. |
| Web estática con cálculo en el navegador | Coste cero y la ubicación del usuario no sale de su dispositivo. |
| `SECLEVEL=1` sin tocar la verificación | El servidor solo negocia cifrados antiguos. Desactivar la verificación sería un fallo de seguridad. |
| Nombre *FuelFinder CV* | Elección de Néstor. |

## Fuera de alcance

Actualización automática con GitHub Actions (siguiente paso; hay que validar que el servidor del
Ministerio acepte peticiones desde los servidores de GitHub) · rutas por carretera · otras
comunidades · histórico largo.
