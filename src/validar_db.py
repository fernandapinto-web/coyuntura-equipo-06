"""Auditoría reproducible de la base SQLite del proyecto.

Uso desde la raíz del repositorio:
    python src/validar_db.py

El script no modifica la base. Comprueba esquema, catálogo, integridad de las
claves, duplicados, cobertura temporal, faltantes y regularidad de fechas.
"""
from __future__ import annotations

import sqlite3
import sys

import pandas as pd

try:
    import config
except ImportError:
    from src import config  # type: ignore


TABLAS_REQUERIDAS = {"temas", "series", "observaciones"}


def main() -> None:
    if not config.RUTA_DB.exists():
        sys.exit(f"[ERROR] No existe la base: {config.RUTA_DB}")

    errores: list[str] = []
    catalogo = config.SERIES_BCCH + config.SERIES_FRED
    ids_esperados = {fila[0] for fila in catalogo}

    with sqlite3.connect(config.RUTA_DB) as conn:
        tablas = {
            fila[0]
            for fila in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        faltan_tablas = TABLAS_REQUERIDAS - tablas
        if faltan_tablas:
            errores.append(f"Faltan tablas: {sorted(faltan_tablas)}")

        if faltan_tablas:
            for error in errores:
                print(f"[ERROR] {error}")
            sys.exit(1)

        ids_db = {fila[0] for fila in conn.execute("SELECT id_serie FROM series")}
        if ids_db != ids_esperados:
            errores.append(
                "El catálogo SQLite no coincide con config.py: "
                f"faltan={sorted(ids_esperados - ids_db)}, "
                f"sobran={sorted(ids_db - ids_esperados)}"
            )

        duplicados = conn.execute(
            """
            SELECT COUNT(*)
            FROM (
                SELECT id_serie, fecha
                FROM observaciones
                GROUP BY id_serie, fecha
                HAVING COUNT(*) > 1
            )
            """
        ).fetchone()[0]
        if duplicados:
            errores.append(f"Hay {duplicados} pares (id_serie, fecha) duplicados")

        huerfanas = conn.execute(
            """
            SELECT COUNT(*)
            FROM observaciones AS o
            LEFT JOIN series AS s ON s.id_serie = o.id_serie
            WHERE s.id_serie IS NULL
            """
        ).fetchone()[0]
        if huerfanas:
            errores.append(f"Hay {huerfanas} observaciones sin serie asociada")

        resumen = pd.read_sql_query(
            """
            SELECT
                s.id_serie,
                s.nombre,
                s.fuente,
                s.frecuencia,
                COUNT(o.fecha)                  AS filas,
                COUNT(o.valor)                  AS validas,
                COUNT(o.fecha) - COUNT(o.valor) AS faltantes,
                MIN(o.fecha)                    AS desde,
                MAX(o.fecha)                    AS hasta,
                MIN(o.valor)                    AS minimo,
                MAX(o.valor)                    AS maximo
            FROM series AS s
            LEFT JOIN observaciones AS o ON o.id_serie = s.id_serie
            GROUP BY s.id_serie, s.nombre, s.fuente, s.frecuencia
            ORDER BY s.fuente, s.id_serie
            """,
            conn,
        )

        observaciones = pd.read_sql_query(
            "SELECT id_serie, fecha, valor FROM observaciones ORDER BY id_serie, fecha",
            conn,
            parse_dates=["fecha"],
        )

    for fila in resumen.itertuples():
        if fila.filas == 0 or fila.validas == 0:
            errores.append(f"{fila.id_serie} no tiene observaciones válidas")

        fechas = observaciones.loc[
            observaciones["id_serie"] == fila.id_serie, "fecha"
        ].drop_duplicates()
        if fila.frecuencia == "M":
            periodos = fechas.dt.to_period("M")
            if periodos.duplicated().any():
                errores.append(f"{fila.id_serie} tiene más de una fila por mes")
            if len(periodos):
                esperados = pd.period_range(periodos.min(), periodos.max(), freq="M")
                meses_ausentes = esperados.difference(pd.PeriodIndex(periodos))
                if len(meses_ausentes):
                    errores.append(
                        f"{fila.id_serie} tiene {len(meses_ausentes)} meses ausentes"
                    )
        elif fila.frecuencia == "D" and len(fechas) > 1:
            salto_maximo = fechas.sort_values().diff().dt.days.max()
            if salto_maximo > 4:
                errores.append(
                    f"{fila.id_serie} tiene un salto diario de {salto_maximo} días"
                )

    print("\n=== Auditoría de data/coyuntura.db ===")
    print(resumen.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
    print(f"\nTablas requeridas: {sorted(TABLAS_REQUERIDAS)}")
    print(f"Series esperadas/cargadas: {len(ids_esperados)}/{len(ids_db)}")
    print(f"Observaciones totales: {int(resumen['filas'].sum())}")
    print(f"Valores faltantes conservados como NULL: {int(resumen['faltantes'].sum())}")
    print(f"Duplicados por serie-fecha: {duplicados}")
    print(f"Observaciones huérfanas: {huerfanas}")

    if errores:
        print("\nResultado: FALLÓ")
        for error in errores:
            print(f"  [ERROR] {error}")
        sys.exit(1)

    print("\nResultado: OK")


if __name__ == "__main__":
    main()
