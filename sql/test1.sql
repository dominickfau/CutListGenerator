SET @so_num = "Q14615";
SET @product_num = "5001472";
SET @qty_to_cut = 25;



SET @row_id = (SELECT id
				FROM fishbowlsodata
				WHERE soNum = @so_num
				AND productNum = @product_num);

UPDATE fishbowlsodata
SET `assignedCutter` = 'N/A',
`cutFlag` = 1,
`dateCutEnd` = '2021-07-31 00:00:00.000000',
`dateCutStart` = '2021-07-31 00:00:00.000000',
`dateSpliceEnd` = '2021-07-31 00:00:00.000000',
`dateSpliceStart` = '2021-07-31 00:00:00.000000',
`dateTerminationStart` = '2021-07-31 00:00:00.000000',
`dateTerminationEnd` = '2021-07-31 00:00:00.000000',
`qtyCut` = @qty_to_cut,
`splicedFlag` = 1,
`terminatedFlag` = 1
WHERE (`id` = @row_id);

SELECT *
FROM fishbowlsodata
WHERE id = @row_id;