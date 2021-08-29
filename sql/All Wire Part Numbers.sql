SELECT UPPER(part.num) AS part_number,
	UPPER(part.description) AS description,
    qtyinventory.qtyOnHand AS qty_on_hand,
    qtyinventory.qtyallocatedSo + qtyinventory.qtyallocatedMo AS qty_allocated,
    qtyinventory.qtyOnHand - (qtyinventory.qtyallocatedSo + qtyinventory.qtyallocatedMo) AS qty_available,
    qtyinventory.qtyOnOrderPo AS qty_on_order_po,
    CASE
		WHEN SUBSTRING_INDEX(LOWER(part.description), "ga", 1)
        THEN SUBSTRING_INDEX(LOWER(part.description), "ga", 1)
        ELSE "N/A"
	END AS wire_awg
FROM part
JOIN qtyinventory ON part.id = qtyinventory.partId AND qtyinventory.locationGroupId = 2
WHERE part.description LIKE "%ga wire%"
AND part.num LIKE "BC-%"

# Order by wire awg descending
ORDER BY FIELD(wire_awg, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30)