SELECT DISTINCT
	rawpart.num
FROM product
JOIN part finishedpart ON product.partId = finishedpart.id
JOIN bomitem ON finishedpart.defaultBomId = bomitem.bomId
JOIN part rawpart ON bomitem.partId = rawpart.id
WHERE product.num = "5001043"
AND bomitem.typeId = 20
AND (rawpart.num LIKE "BC-10%" OR rawpart.num LIKE "50%")