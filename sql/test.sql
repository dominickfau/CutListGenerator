SELECT DISTINCT
	rawpart.num AS kit_part_number
FROM product
JOIN part finishedpart ON product.partId = finishedpart.id
JOIN bomitem ON finishedpart.defaultBomId = bomitem.bomId
JOIN part rawpart ON bomitem.partId = rawpart.id
WHERE product.num = "5000107"
AND bomitem.typeId = (
					  SELECT id
					  FROM bomitemtype
					  WHERE name = "Raw Good"
					  )
AND ((rawpart.num LIKE "BC-10%" AND rawpart.uomId = (SELECT id FROM uom WHERE name = "Each")) OR rawpart.num LIKE "50%")
AND rawpart.typeId = (SELECT id FROM parttype WHERE name = "Inventory");

SELECT part.num AS number,
	bomitem.quantity AS quantity,
    bomitemtype.name AS part_type
FROM bom
JOIN bomitem ON bom.id = bomitem.bomId
JOIN bomitemtype ON bomitem.typeId = bomitemtype.id
JOIN part ON bomitem.partId = part.id
WHERE bom.num = "5000107";

SELECT part.num AS number,
	bomitem.quantity AS quantity,
    bomitemtype.name AS part_type
FROM bom
JOIN bomitem ON bom.id = bomitem.bomId
JOIN bomitemtype ON bomitem.typeId = bomitemtype.id
JOIN part ON bomitem.partId = part.id
WHERE bom.num = "5000107"
AND bomitemtype.name = "Raw Good";