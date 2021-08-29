SELECT UPPER(bom.num) AS bom_number,
	UPPER(part.num) AS part_number,
    UPPER(part.description) AS part_description,
    SUM((bomitem.quantity * COALESCE(uomconversion.multiply,1)) / COALESCE(uomconversion.factor,1)) AS quantity,
    partuom.code AS uom,
    CASE
		WHEN SUBSTRING_INDEX(LOWER(part.description), "ga", 1)
        THEN SUBSTRING_INDEX(LOWER(part.description), "ga", 1)
        ELSE "N/A"
	END AS wire_awg
FROM bom
JOIN bomitem ON bom.id = bomitem.bomId
JOIN part ON bomitem.partId = part.id
JOIN uom partuom ON part.uomId = partuom.id
LEFT JOIN uomconversion ON (uomconversion.toUomId = part.uomId AND uomconversion.fromUomId = bomitem.uomId)
WHERE part.description LIKE "%ga wire%"
AND bomitem.typeId = 20
GROUP BY bom.num, part.num
# Order by wire awg descending
ORDER BY bom.num, FIELD(wire_awg, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30)