SELECT DISTINCT
	rawpart.num
FROM product
JOIN part finishedpart ON product.partId = finishedpart.id
JOIN bomitem ON finishedpart.defaultBomId = bomitem.bomId
JOIN part rawpart ON bomitem.partId = rawpart.id
WHERE product.num = "5001406"
AND bomitem.typeId = 20
AND ((rawpart.num LIKE "BC-10%" AND rawpart.uomId = 1) OR rawpart.num LIKE "50%")