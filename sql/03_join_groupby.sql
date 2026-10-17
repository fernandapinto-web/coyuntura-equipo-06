-- ============================================================
-- Consultas SQL: JOIN y GROUP BY (Jorge)
-- Series a cargo: desocupación, remuneraciones, IPC EE.UU. y PPI EE.UU.
-- ============================================================

-- ------------------------------------------------------------
-- Consulta 1 (JOIN): uno las tablas observaciones, series y temas
-- para ver la historia completa de mis series con su nombre, tema y unidad.
-- ------------------------------------------------------------
SELECT s.nombre, t.tema, o.fecha, o.valor, s.unidad
FROM observaciones o
JOIN series s ON s.id_serie = o.id_serie
JOIN temas t ON t.id_tema = s.id_tema
WHERE s.nombre IN ('Tasa de desocupación',
                   'Índice de remuneraciones (var. anual)',
                   'IPC Estados Unidos (índice)',
                   'Índice de precios al productor (EE.UU.)')
ORDER BY s.nombre, o.fecha;


-- ------------------------------------------------------------
-- Consulta 2 (GROUP BY): agrupo las series diarias por mes
-- y calculo el promedio mensual de cada una.
-- ------------------------------------------------------------

SELECT s.nombre,
       strftime('%Y-%m', o.fecha)  AS mes,
       ROUND(AVG(o.valor), 2)      AS promedio_mensual,
       COUNT(*)                    AS n_dias
FROM observaciones o
JOIN series s ON s.id_serie = o.id_serie
WHERE s.frecuencia = 'D'
GROUP BY s.nombre, mes
ORDER BY s.nombre, mes;

