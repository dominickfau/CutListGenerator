SELECT bom.num "Part Number",
	SUM(bomitem.quantity) * $QTY{Qty_To_Cut} AS "Total Wire To Cut (ft)",
    ROUND(SUM(bomitem.quantity) / 150 * $QTY{Qty_To_Cut}, 2) AS "Estimated Time Minutes",
    ROUND(SUM(bomitem.quantity) / 150 * $QTY{Qty_To_Cut}, 2) / 60 AS "Estimated Time Hours"
FROM bom
JOIN bomitem ON bomitem.bomId = bom.id
JOIN part ON bomitem.partId = part.id

WHERE bomitem.typeId = 20
AND part.description LIKE "%ga wire%"
AND bom.id = $BOM{Bill_of_Material}
GROUP BY bom.num

-- Estimated cut speed = 150 ft/min