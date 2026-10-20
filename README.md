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
  sql/
    01_esquema.sql     tablas: series, temas, observaciones
    02_consultas_ejemplo.sql
  notebooks/
    01_pipeline_datos.ipynb
    02_analisis_ejemplo.ipynb
  data/
    coyuntura.db       se genera con el script (no se sube a GitHub)
```

El pipeline de extracción y carga está adaptado del kit de inicio del curso. El catálogo de series (`src/config.py`) es el del equipo.

## Series utilizadas

### formato de la tabla
| Variable | Código | Frecuencia | Fuente |

|---|---|---|---|

| IPC (índice) | F074.IPC.IND.Z.EP09.C.M | Mensual | BCCh |
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
    pip install -r requirements.txt
   ```

3. Crear el archivo .env con las claves personales de acceso a las APIs. Se copia el archivo .env.example, se le cambia el nombre a .env y se escriben las claves propias. Las claves son gratuitas:

Banco Central de Chile: https://si3.bcentral.cl/Siete/es/Siete/API
FRED: https://fred.stlouisfed.org/docs/api/api_key.html

El .env no se sube a GitHub.

4. Descargar las series y generar la base de datos, fijando la fecha de corte:

```
python src/carga_db.py --hasta 2026-10-20
   ```

Esto descarga las 12 series y crea el archivo data/coyuntura.db. Se puede volver a correr cuando se quieran actualizar los datos.

5. Correr el análisis. Abrir notebooks/03_analisis_coyuntura.ipynb y ejecutar todas las celdas. El notebook lee las consultas de la carpeta sql/ y trabaja sobre data/coyuntura.db.