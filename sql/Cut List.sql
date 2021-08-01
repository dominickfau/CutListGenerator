SELECT so.num AS soNum,
	CASE 
		WHEN customer.name = "Brunswick Boat Group, Fort Wayne Operatio" THEN "Brunswick"
        WHEN customer.name = "GODFREY MARINE-HURRICANE" THEN "Godfrey"
        WHEN customer.name = "MARINE MOORING, INC." THEN "Marine Mooring"
        WHEN customer.name = "Bennington Pontoon Boats" THEN "Bennington"
        ELSE customer.name
	END AS customerName,
    so.dateFirstShip AS dueDate,
    DATE_SUB(so.dateFirstShip, INTERVAL 14 DAY) AS cutDate,
    soitem.soLineItem AS soLineItem,
    product.num AS productNum,
    product.description,
    soitem.qtyToFulfill AS qtyToFulfill,
    (soitem.qtyToFulfill - qtyPicked - qtyFulfilled) AS qtyLeftToShip,
    productuom.code AS uom

FROM so
JOIN soitem ON soitem.soId = so.id
JOIN customer ON so.customerId = customer.id
JOIN product ON soitem.productId = product.id
JOIN uom productuom ON product.uomId = productuom.id

WHERE soitem.statusId < 50 -- 50 = Finished
AND (soitem.qtyToFulfill - qtyPicked - qtyFulfilled) > 0
-- AND DATE_SUB(so.dateFirstShip, INTERVAL 14 DAY) < NOW()
AND product.num LIKE "50%"
AND productuom.code = "ea"

ORDER BY so.dateFirstShip, soLineItem