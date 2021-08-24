SELECT YEAR(mo.dateScheduled) AS date,
    part.num AS "Part Number",
    part.description AS "Description",
    SUM(woitem.qtyUsed) AS "Total Used",
    uom.code AS "UOM"
    
FROM woitem
JOIN moitem ON woitem.moitemId = moitem.id
JOIN mo ON moitem.moId = mo.id
JOIN part ON woitem.partId = part.id
JOIN uom ON woitem.uomId = uom.id

WHERE part.id = $PART{Part_Number}
-- AND part.num NOT LIKE "500%"
-- AND part.activeFlag = 1

GROUP BY YEAR(mo.dateScheduled)
ORDER BY part.id