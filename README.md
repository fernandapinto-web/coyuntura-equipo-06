# Coyuntura Equipo 06 — Inflación en Chile

Proyecto semestral de la asignatura **Ciencia de Datos para Economía (ICO09425)**.

## Integrantes

- Fernanda Pinto Morales
- Diego Elvenberg Contreras
- Jorge López Sanhueza

## Tema

**Inflación en Chile (IPC)**

### Variable objetivo

Inflación en Chile, medida como la **variación interanual del Índice de Precios al Consumidor (IPC)**.

### Horizonte de proyección

12 meses.

## Pregunta de investigación

¿En qué medida la incorporación de variables asociadas a la actividad económica, política monetaria y factores externos permite mejorar la proyección de la inflación interanual en Chile a 12 meses respecto de un modelo basado únicamente en su dinámica histórica?

## Fuentes de datos

El proyecto utilizará principalmente datos provenientes de:

- Banco Central de Chile (BDE)
- Instituto Nacional de Estadísticas (INE)
- FRED — Federal Reserve Bank of St. Louis
- U.S. Energy Information Administration (EIA)

## Metodología inicial

Se comparará un modelo de series de tiempo **ARIMA/SARIMA** con un modelo alternativo que incorpore variables macroeconómicas explicativas.

El proyecto seguirá el flujo:

**API → SQL → Python → Power BI**

y será desarrollado de manera reproducible utilizando **Git y GitHub**.

## Estructura del repositorio

```
coyuntura-equipo-06/
  README.md
  requirements.txt     librerías de Python
  .env.example         plantilla de claves
  .gitignore
  src/
    config.py          catálogo de las 12 series y lectura de claves
    extraccion.py      descarga desde las APIs del Banco Central y FRED
    carga_db.py        crea la base de datos y carga las series
    validar_db.py      audita cobertura, faltantes e integridad de SQLite
  sql/
    01_esquema.sql     tablas: series, temas, observaciones
    02_consultas_ejemplo.sql
    03_join_groupby.sql
    04_series_jorge.sql
    05_analisis_inflacion_chile.sql
  notebooks/
    01_pipeline_datos.ipynb
    02_analisis_ejemplo.ipynb
    03_analisis_coyuntura.ipynb
    04_analisis_inflacion_chile.ipynb
  data/
    coyuntura.db       se genera con el script (no se sube a GitHub)
```

El pipeline de extracción y carga está adaptado del kit de inicio del curso. El catálogo de series (`src/config.py`) es el del equipo.

## Series utilizadas

| Variable | Código | Frecuencia | Fuente |
|---|---|---|---|
| IPC Chile (índice 2023=100, serie empalmada) | F074.IPC.IND.Z.EP23.C.M | Mensual | BCCh |
| Tipo de cambio observado | F073.TCO.PRE.Z.D | Diaria | BCCh |
| Tasa de Política Monetaria (TPM) | F022.TPM.TIN.D001.NO.Z.D | Diaria | BCCh |
| Imacec | F032.IMC.IND.Z.Z.EP18.Z.Z.0.M | Mensual | BCCh |
| Tasa de desocupación | F049.DES.TAS.INE9.10.M | Mensual | BCCh / INE |
| Índice de remuneraciones (var. anual) | G049.RMM.V12.INE23.NE.M | Mensual | BCCh / INE |
| Petróleo WTI | F019.PPB.PRE.41B.M | Mensual | BCCh |
| Cobre refinado BML | F019.PPB.PRE.100.D | Diaria | BCCh |
| IPC de Estados Unidos | CPIAUCSL | Mensual | FRED |
| Tasa Fed Funds | FEDFUNDS | Mensual | FRED |
| Índice de precios al productor (EE.UU.) | PPIACO | Mensual | FRED |
| Índice mundial de precios de alimentos | PFOODINDEXM | Mensual | FRED |

## Cómo reproducir la extracción y la base de datos

1. Clonar el repositorio y entrar a la carpeta:

   ```
   git clone https://github.com/fernandapinto-web/coyuntura-equipo-06
   cd coyuntura-equipo-06
   ```

2. Instalar las librerías :

   ```
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

3. Crear el archivo .env con las claves personales de acceso a las APIs. Se copia el archivo .env.example, se le cambia el nombre a .env y se escriben las claves propias. Las claves son gratuitas:

Banco Central de Chile: https://si3.bcentral.cl/Siete/es/Siete/API
FRED: https://fred.stlouisfed.org/docs/api/api_key.html

El .env no se sube a GitHub.

4. Descargar las series y generar la base de datos, fijando la fecha de corte:

   ```
   python src/carga_db.py --hasta 2026-10-20
   ```

Esto descarga las 12 series desde las APIs oficiales y crea el archivo
`data/coyuntura.db`. La carga exige que las 12 descargas terminen correctamente:
si una falla, no reemplaza silenciosamente la base con una versión parcial. Los
valores no observados se conservan como `NULL` para poder auditarlos. No usar
`--demo` para resultados del informe.

5. Auditar la base generada:

   ```
   python src/validar_db.py
   ```

   El control verifica las tablas `temas`, `series` y `observaciones`, las 12
   series esperadas, cobertura temporal, faltantes, regularidad de frecuencia,
   duplicados y observaciones sin serie asociada.

6. Ejecutar los análisis:

   - `notebooks/03_analisis_coyuntura.ipynb` conserva el análisis elaborado por
     Jorge con `sql/04_series_jorge.sql`.
   - `notebooks/04_analisis_inflacion_chile.ipynb` usa
     `sql/05_analisis_inflacion_chile.sql` para analizar IPC, TPM, Imacec y tipo
     de cambio. El notebook calcula la inflación interanual, mensualiza las
     series diarias, audita faltantes y compara pronósticos directos a 12 meses
     con un backtest de origen móvil.

## Consultas SQL verificadas

- `sql/02_consultas_ejemplo.sql`: `INNER JOIN`, `GROUP BY`, `LAG` y promedio
  móvil con ventana.
- `sql/03_join_groupby.sql`: consolidación del catálogo y agregación mensual de
  series diarias.
- `sql/04_series_jorge.sql`: selección con `INNER JOIN` y `WHERE` de las series
  asignadas a Jorge.
- `sql/05_analisis_inflacion_chile.sql`: base mensual del análisis principal;
  combina `SELECT`, `WHERE`, `INNER JOIN`, `LEFT JOIN`, `GROUP BY`, `AVG` y
  `LAG(12)`.

## Resultado de la ejecución reproducible

Con corte solicitado al **20 de octubre de 2026**, el pipeline real descargó
las 12 series y almacenó 19.199 filas. La auditoría encontró 5.537 valores
`NULL`, concentrados principalmente en fines de semana y feriados de las series
diarias, sin duplicados ni observaciones huérfanas. Las fechas finales difieren
entre series debido a sus calendarios de publicación.

En el backtest preliminar de 36 pronósticos, el modelo Ridge basado solo en la
historia de la inflación obtuvo RMSE 2,716 y MAE 2,077. El modelo ampliado con
TPM, Imacec y tipo de cambio rezagados obtuvo RMSE 5,465 y MAE 4,310; por tanto,
esa especificación macroeconómica no mejora al benchmark histórico. Este
resultado usa datos revisados y no constituye evidencia causal ni una selección
definitiva de modelo. Al seleccionar entre ambos modelos por el menor RMSE, la
especificación de solo inflación proyecta **4,67 % interanual para septiembre de
2027**, usando información hasta septiembre de 2026. Es una proyección
condicional y no incorpora shocks futuros.

La base SQLite y `.env` están excluidos de Git. Antes de preparar un commit se
debe revisar que ningún archivo versionado contenga credenciales.
