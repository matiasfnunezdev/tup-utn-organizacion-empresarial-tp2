"""Análisis de ventas para el Escenario B del TP de Organización Empresarial.

Procesa el CSV transaccional `datos/ventas_pyme.csv` y produce:

1. KPIs tabulares en `resultados/indicadores_ventas.csv`.
2. Gráfico de evolución diaria de facturación en `resultados/evolucion_ventas.png`.

Decisiones técnicas:
- Se usa `pandas` por la legibilidad de las agregaciones (`groupby` + `agg`).
- Las rutas son relativas al raíz del repositorio para garantizar la
  ejecución idéntica en Google Colab y en máquinas locales.
- El gráfico incluye una media móvil de 7 días para suavizar el ruido diario
  y permitir distinguir tendencia subyacente del ruido aleatorio.
- Se evita `matplotlib.pyplot.show()` para que el script sea ejecutable de
  manera no interactiva (CI, notebook, terminal).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Backend no interactivo (necesario en Colab/CI sin display).
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
DATASET = RAIZ / "datos" / "ventas_pyme.csv"
DIR_RESULTADOS = RAIZ / "resultados"


def cargar_dataset(ruta: Path) -> pd.DataFrame:
    """Lee el CSV transaccional y agrega la columna derivada `monto`.

    `monto = cantidad * precio_unitario` se calcula una sola vez acá para que
    el resto del análisis trabaje sobre datos ya enriquecidos.
    """
    df = pd.read_csv(ruta, parse_dates=["fecha_venta"])
    df["monto"] = df["cantidad"] * df["precio_unitario"]
    return df


def calcular_indicadores(df: pd.DataFrame) -> dict[str, float | str | dict]:
    """Computa los KPIs principales del período cubierto por el dataset."""
    ventas_totales = df["monto"].sum()
    ticket_promedio = df["monto"].mean()
    cantidad_transacciones = len(df)

    # Producto más vendido por facturación (criterio empresarial: el que
    # genera mayor ingreso). Se reporta también por unidades porque a veces
    # el de mayor volumen no es el de mayor facturación.
    facturacion_por_producto = df.groupby("producto")["monto"].sum().sort_values(ascending=False)
    unidades_por_producto = df.groupby("producto")["cantidad"].sum().sort_values(ascending=False)

    # Agregación mensual: clave para detectar estacionalidad y planificar
    # compras / promociones del mes siguiente.
    ventas_mensuales = (
        df.set_index("fecha_venta").resample("MS")["monto"].sum().rename("ventas_mes")
    )

    return {
        "ventas_totales": float(ventas_totales),
        "ticket_promedio": float(ticket_promedio),
        "cantidad_transacciones": int(cantidad_transacciones),
        "producto_top_facturacion": facturacion_por_producto.index[0],
        "producto_top_unidades": unidades_por_producto.index[0],
        "facturacion_por_producto": facturacion_por_producto.to_dict(),
        "ventas_mensuales": {fecha.strftime("%Y-%m"): float(monto) for fecha, monto in ventas_mensuales.items()},
    }


def guardar_indicadores(indicadores: dict, destino: Path) -> None:
    """Persiste los KPIs en CSV de dos columnas (indicador, valor).

    El formato plano facilita que el cuerpo docente lo abra en Excel sin
    parsear JSON ni instalar dependencias extra.
    """
    filas = [
        ("ventas_totales_ars", f"{indicadores['ventas_totales']:.2f}"),
        ("ticket_promedio_ars", f"{indicadores['ticket_promedio']:.2f}"),
        ("cantidad_transacciones", indicadores["cantidad_transacciones"]),
        ("producto_top_por_facturacion", indicadores["producto_top_facturacion"]),
        ("producto_top_por_unidades", indicadores["producto_top_unidades"]),
    ]
    for producto, monto in indicadores["facturacion_por_producto"].items():
        filas.append((f"facturacion_{producto}", f"{monto:.2f}"))
    for mes, monto in indicadores["ventas_mensuales"].items():
        filas.append((f"ventas_mes_{mes}", f"{monto:.2f}"))

    destino.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(filas, columns=["indicador", "valor"]).to_csv(destino, index=False, encoding="utf-8")


def graficar_evolucion(df: pd.DataFrame, destino: Path) -> None:
    """Grafica facturación diaria con media móvil de 7 días.

    La media móvil hace visible la tendencia subyacente; sin ella, el ruido
    transaccional diario domina la visualización y obstaculiza la lectura.
    """
    diario = df.groupby("fecha_venta")["monto"].sum().sort_index()
    media_movil = diario.rolling(window=7, min_periods=1).mean()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(diario.index, diario.values, alpha=0.4, label="Facturación diaria")
    ax.plot(media_movil.index, media_movil.values, linewidth=2.2, label="Media móvil 7 días")

    ax.set_title("Evolución de la facturación diaria — Pyme (escenario B)")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Facturación (ARS)")
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
    ax.grid(alpha=0.3)
    ax.legend(loc="upper left")
    fig.autofmt_xdate()
    fig.tight_layout()

    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino, dpi=150)
    plt.close(fig)


def main() -> None:
    df = cargar_dataset(DATASET)
    indicadores = calcular_indicadores(df)

    csv_salida = DIR_RESULTADOS / "indicadores_ventas.csv"
    grafico_salida = DIR_RESULTADOS / "evolucion_ventas.png"

    guardar_indicadores(indicadores, csv_salida)
    graficar_evolucion(df, grafico_salida)

    print("[OK] Análisis completado")
    print(f"  Transacciones procesadas: {indicadores['cantidad_transacciones']}")
    print(f"  Ventas totales: ARS {indicadores['ventas_totales']:.2f}")
    print(f"  Ticket promedio: ARS {indicadores['ticket_promedio']:.2f}")
    print(f"  Producto top (facturación): {indicadores['producto_top_facturacion']}")
    print(f"  Producto top (unidades): {indicadores['producto_top_unidades']}")
    print(f"  Indicadores: {csv_salida.relative_to(RAIZ)}")
    print(f"  Gráfico: {grafico_salida.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
