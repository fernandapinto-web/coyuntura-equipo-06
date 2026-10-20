-- Series de Jorge: desocupación, remuneraciones, IPC y PPI de EE.UU.
-- Usada en: notebooks/03_analisis_coyuntura.ipynb
SELECT   s.nombre, o.fecha, o.valor, s.unidad
FROM         observaciones AS o
INNER JOIN   series        AS s  ON s.id_serie = o.id_serie
WHERE    s.nombre IN ('Tasa de desocupación',
                      'Índice de remuneraciones (var. anual)',
                      'IPC Estados Unidos (índice)',
                      'Índice de precios al productor (EE.UU.)')
ORDER BY s.nombre, o.fecha