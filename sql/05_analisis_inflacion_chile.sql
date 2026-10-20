-- ============================================================
-- Base mensual para el análisis de inflación de Chile
--
-- Técnicas utilizadas:
--   * SELECT y WHERE para escoger las cuatro series del análisis.
--   * INNER JOIN para incorporar el nombre y la unidad del IPC.
--   * GROUP BY y AVG para mensualizar TPM y tipo de cambio diarios.
--   * LAG para calcular la inflación interanual desde el nivel del IPC.
--   * LEFT JOIN para conservar todos los meses disponibles del IPC aunque
--     alguna variable explicativa no tenga observación en ese mes.
-- ============================================================

WITH ipc_nivel AS (
    SELECT
        date(o.fecha, 'start of month') AS fecha,
        o.valor                         AS ipc,
        s.nombre                        AS ipc_nombre,
        s.unidad                        AS ipc_unidad
    FROM observaciones AS o
    INNER JOIN series AS s
        ON s.id_serie = o.id_serie
    WHERE o.id_serie = 'F074.IPC.IND.Z.EP23.C.M'
),
ipc_con_inflacion AS (
    SELECT
        fecha,
        ipc,
        ipc_nombre,
        ipc_unidad,
        100.0 * (
            ipc / LAG(ipc, 12) OVER (ORDER BY fecha) - 1.0
        ) AS inflacion_interanual
    FROM ipc_nivel
),
tpm_mensual AS (
    SELECT
        date(fecha, 'start of month') AS fecha,
        AVG(valor)                    AS tpm_promedio,
        COUNT(valor)                  AS tpm_dias_validos
    FROM observaciones
    WHERE id_serie = 'F022.TPM.TIN.D001.NO.Z.D'
    GROUP BY date(fecha, 'start of month')
),
tipo_cambio_mensual AS (
    SELECT
        date(fecha, 'start of month') AS fecha,
        AVG(valor)                    AS tipo_cambio_promedio,
        COUNT(valor)                  AS tipo_cambio_dias_validos
    FROM observaciones
    WHERE id_serie = 'F073.TCO.PRE.Z.D'
    GROUP BY date(fecha, 'start of month')
),
imacec_mensual AS (
    SELECT
        date(fecha, 'start of month') AS fecha,
        valor                         AS imacec
    FROM observaciones
    WHERE id_serie = 'F032.IMC.IND.Z.Z.EP18.Z.Z.0.M'
)
SELECT
    i.fecha,
    i.ipc,
    i.inflacion_interanual,
    t.tpm_promedio,
    t.tpm_dias_validos,
    a.imacec,
    c.tipo_cambio_promedio,
    c.tipo_cambio_dias_validos
FROM ipc_con_inflacion AS i
LEFT JOIN tpm_mensual AS t
    ON t.fecha = i.fecha
LEFT JOIN imacec_mensual AS a
    ON a.fecha = i.fecha
LEFT JOIN tipo_cambio_mensual AS c
    ON c.fecha = i.fecha
ORDER BY i.fecha;
