# Análisis de Ventas — Trabajo Práctico de Organización Empresarial (UTN TUP)

Proyecto de la célula de desarrollo del **TP de Gestión Colaborativa, Control de Versiones y Organización Empresarial** de la Tecnicatura Universitaria en Programación a Distancia (UTN). Implementa el **Escenario B**: análisis estadístico básico de ventas de una pequeña empresa.

> **Equipo (modalidad individual):** Matias Fernando Nuñez asume los tres roles definidos por la cátedra (P1 Líder/Organizador, P2 Desarrollador Técnico, P3 Revisor/QA), evidenciando la separación de responsabilidades mediante ramas y Pull Requests independientes.

## Tabla de contenidos

- [Objetivo](#objetivo)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Dataset](#dataset)
- [Indicadores calculados](#indicadores-calculados)
- [Cómo ejecutar el proyecto](#cómo-ejecutar-el-proyecto)
- [Flujo de trabajo Git/GitHub](#flujo-de-trabajo-gitgithub)
- [Trazabilidad con Jira](#trazabilidad-con-jira)
- [Seguridad](#seguridad)
- [Licencia](#licencia)

## Objetivo

Procesar un conjunto de datos transaccionales de ventas y producir indicadores accionables para una pyme: ventas totales, producto con mejor desempeño, evolución mensual y ticket promedio. El proyecto demuestra el uso del control de versiones y la gestión organizacional en Jira como soporte de la calidad y trazabilidad del trabajo técnico.

## Estructura del repositorio

```
tup-utn-organizacion-empresarial-tp2/
├── datos/
│   └── ventas_pyme.csv          # Dataset transaccional simulado (4 meses, 420 tx)
├── scripts/
│   └── analisis_ventas.py       # Lógica de cálculo, agregaciones y gráfico
├── resultados/
│   ├── indicadores_ventas.csv   # Salida tabular (KPIs)
│   └── evolucion_ventas.png     # Gráfico evolución temporal
├── notebooks/
│   └── analisis_ventas_colab.ipynb  # Notebook ejecutable en Google Colab
├── .gitignore
└── README.md
```

La estructura respeta la consigna de la cátedra (`/datos`, `/scripts`, `/resultados`) y agrega `notebooks/` para alojar el flujo Colab, ya que el TP exige ejecución desde ese entorno.

## Dataset

`datos/ventas_pyme.csv` contiene 420 registros transaccionales sintéticos (120 días × 3-4 transacciones diarias en promedio sobre un catálogo de 5 productos) con las columnas:

| Columna | Tipo | Descripción |
|--------|------|-------------|
| `id` | int | Identificador único de transacción |
| `producto` | string | Nombre del producto vendido |
| `cantidad` | int | Unidades vendidas en la transacción |
| `precio_unitario` | float | Precio por unidad (ARS) |
| `fecha_venta` | date | Fecha de la operación (`YYYY-MM-DD`) |

El dataset fue generado de manera reproducible por `scripts/generar_dataset.py` con semilla fija (`random.seed(42)`), por lo que el lector puede regenerarlo y obtener exactamente los mismos resultados. Se almacena en formato CSV liviano (≈14 KB) para que la clonación del repositorio sea rápida.

## Indicadores calculados

`scripts/analisis_ventas.py` produce los siguientes KPIs:

1. **Ventas totales** (sumatoria de `cantidad × precio_unitario`).
2. **Producto más vendido** por facturación y por unidades.
3. **Ventas por mes** (agregación mensual).
4. **Ticket promedio** por transacción.
5. **Gráfico de evolución** de la facturación diaria con media móvil de 7 días.

## Cómo ejecutar el proyecto

### Localmente

```bash
python -m pip install -r requirements.txt  # pandas, matplotlib
python scripts/analisis_ventas.py
```

Las salidas se generan en `resultados/`.

### En Google Colab

1. Abrir `notebooks/analisis_ventas_colab.ipynb`.
2. Ejecutar la celda inicial que clona el repositorio.
3. Ejecutar la celda de análisis; los gráficos se renderizan inline y los artefactos se guardan en la carpeta `resultados/` del entorno Colab.

Todas las rutas son **relativas** al raíz del repositorio, lo que evita romper la reproducibilidad fuera del entorno original.

## Flujo de trabajo Git/GitHub

El proyecto sigue un flujo **GitHub Flow** simplificado:

1. La rama `main` representa el estado entregable. Está protegida (no se permite push directo).
2. Cada Issue de Jira se desarrolla en una rama `feature/<descripcion-corta>`.
3. Cada commit comienza con el ID del Issue Jira: `TUPOE-1: feat: ...` (Conventional Commits + trazabilidad).
4. El merge a `main` se realiza vía Pull Request con peer review (mínimo dos comentarios técnicos en el hilo de discusión, conforme a la consigna).

## Trazabilidad con Jira

Cada commit del historial cumple con el formato:

```
<JIRA-ID>: <tipo>(<scope>): <descripcion corta>
```

Donde `<JIRA-ID>` es el identificador del issue en el proyecto Jira asociado (ejemplo: `TUPOE-3`). El proyecto Jira contiene los 6 issues que describen el ciclo completo de trabajo (ver informe PDF).

## Seguridad

- El **PAT de GitHub nunca se commitea**. Para `push` desde Google Colab se inyecta como variable de entorno (`from google.colab import userdata; userdata.get("GH_PAT")`) y se interpola en la URL solo dentro de la celda de ejecución.
- `.gitignore` excluye explícitamente `*.token`, `secrets/`, `.env` y archivos `__pycache__`.
- Si un token llega a publicarse por error, debe revocarse de inmediato desde *Settings → Developer settings → Personal access tokens* y generarse uno nuevo.

## Licencia

Proyecto académico — uso educativo bajo la Tecnicatura Universitaria en Programación a Distancia (UTN). El dataset es sintético y no contiene información personal.
