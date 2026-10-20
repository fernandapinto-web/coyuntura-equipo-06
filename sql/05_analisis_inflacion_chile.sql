SELECT
    s.nombre,
    o.fecha,
    o.valor,
    s.unidad
FROM observaciones AS o
INNER JOIN series AS s
    ON s.id_serie = o.id_serie
WHERE s.id_serie = 'F074.IPC.IND.Z.EP09.C.M'
ORDER BY o.fecha ASC;
