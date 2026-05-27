"""Genera el dataset sintético `datos/ventas_pyme.csv` de manera reproducible.

Este script se ejecuta una única vez para producir el CSV transaccional que
versiona el repositorio. La semilla fija (`random.seed(42)`) garantiza que
cualquier integrante del equipo (o el cuerpo docente) pueda regenerar el
dataset y obtener exactamente los mismos registros.

La separación entre generación y análisis es deliberada: aísla la lógica que
introduce aleatoriedad (potencial fuente de no reproducibilidad) de la lógica
de negocio (cálculo de indicadores), facilitando el peer review.
"""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

# Ruta relativa al raíz del repositorio (cumple consigna: nunca rutas absolutas).
RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "datos" / "ventas_pyme.csv"

# Catálogo de productos con precio base. El precio real varía ±10% para
# simular promociones puntuales o ajustes de la pyme.
PRODUCTOS: list[tuple[str, float]] = [
    ("Yerba mate 500g", 2800.0),
    ("Café molido 250g", 4200.0),
    ("Té en saquitos x25", 1500.0),
    ("Galletitas dulces", 1200.0),
    ("Mermelada frutilla", 2100.0),
]

# Ventana temporal: cuatro meses completos (febrero a mayo 2026). Cubrir
# meses calendario enteros evita que la agregación mensual muestre un mes
# incompleto al final del período, lo que distorsionaría el gráfico de
# evolución y los KPIs de "ventas por mes".
FECHA_INICIO = date(2026, 2, 1)
DIAS = 120  # 1-feb a 31-may inclusive en un año no bisiesto.


def generar_filas(semilla: int = 42) -> list[dict]:
    """Construye la lista de transacciones. Devuelve diccionarios listos
    para `csv.DictWriter`. La semilla externa permite tests deterministas.
    """
    random.seed(semilla)
    filas: list[dict] = []
    id_actual = 1

    for offset in range(DIAS):
        fecha = FECHA_INICIO + timedelta(days=offset)
        # Entre 2 y 5 transacciones por día — modela la actividad de una
        # pyme con flujo bajo pero constante.
        for _ in range(random.randint(2, 5)):
            nombre, precio_base = random.choice(PRODUCTOS)
            # Variación ±10% sobre precio base. Se redondea a múltiplos de 10
            # para que los precios parezcan reales.
            ruido = random.uniform(-0.10, 0.10)
            precio = round((precio_base * (1 + ruido)) / 10) * 10
            cantidad = random.randint(1, 6)
            filas.append(
                {
                    "id": id_actual,
                    "producto": nombre,
                    "cantidad": cantidad,
                    "precio_unitario": precio,
                    "fecha_venta": fecha.isoformat(),
                }
            )
            id_actual += 1

    return filas


def escribir_csv(filas: list[dict], destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["id", "producto", "cantidad", "precio_unitario", "fecha_venta"]
        )
        writer.writeheader()
        writer.writerows(filas)


def main() -> None:
    filas = generar_filas()
    escribir_csv(filas, SALIDA)
    print(f"[OK] Generadas {len(filas)} filas en {SALIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
