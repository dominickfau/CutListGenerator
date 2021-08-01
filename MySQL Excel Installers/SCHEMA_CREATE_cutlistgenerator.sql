-- CREATE SCHEMA `cutlistgenerator` DEFAULT CHARACTER SET utf8;

USE `cutlistgenerator`;

CREATE TABLE `fishbowlsodata` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `addedToCutListFlag` bit(1) DEFAULT b'0',
  `assignedCutter` varchar(255) DEFAULT NULL,
  `customerName` varchar(255) NOT NULL,
  `cutFlag` bit(1) DEFAULT b'0',
  `dateCutEnd` datetime(6) DEFAULT NULL,
  `dateCutStart` datetime(6) DEFAULT NULL,
  `dateSpliceEnd` datetime(6) DEFAULT NULL,
  `dateSpliceStart` datetime(6) DEFAULT NULL,
  `dateTerminationEnd` datetime(6) DEFAULT NULL,
  `dateTerminationStart` datetime(6) DEFAULT NULL,
  `description` varchar(255) NOT NULL,
  `dueDate` datetime(6) NOT NULL,
  `kitFlag` bit(1) NOT NULL DEFAULT b'0',
  `parentKitPartNum` varchar(255) DEFAULT NULL,
  `productNum` varchar(255) NOT NULL,
  `qtyCut` decimal(28,9) DEFAULT NULL,
  `qtyLeftToCut` decimal(28,9) NOT NULL,
  `soLineItem` int(11) NOT NULL,
  `soNum` varchar(255) NOT NULL,
  `splicedFlag` bit(1) DEFAULT b'0',
  `terminatedFlag` bit(1) DEFAULT b'0',
  `uom` varchar(15) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `extrapartscut` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `addedToCutListFlag` bit(1) DEFAULT b'0',
  `assignedCutter` varchar(255) DEFAULT NULL,
  `customerName` varchar(255) NOT NULL,
  `cutFlag` bit(1) DEFAULT b'0',
  `dateCutEnd` datetime(6) DEFAULT NULL,
  `dateCutStart` datetime(6) DEFAULT NULL,
  `dateSpliceEnd` datetime(6) DEFAULT NULL,
  `dateSpliceStart` datetime(6) DEFAULT NULL,
  `dateTerminationEnd` datetime(6) DEFAULT NULL,
  `dateTerminationStart` datetime(6) DEFAULT NULL,
  `description` varchar(255) NOT NULL,
  `readyForBuildFlag` bit(1) DEFAULT b'0',
  `kitFlag` bit(1) NOT NULL DEFAULT b'0',
  `parentKitPartNum` varchar(255) DEFAULT NULL,
  `productNum` varchar(255) NOT NULL,
  `qtyCut` decimal(28,9) DEFAULT NULL,
  `splicedFlag` bit(1) DEFAULT b'0',
  `terminatedFlag` bit(1) DEFAULT b'0',
  `uom` varchar(15) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

USE `qes`;

INSERT INTO cutlistgenerator.fishbowlsodata (soNum, customerName, dueDate, soLineItem, productNum, description, qtyToFulfill, qtyLeftToShip, uom)
SELECT so.num AS soNum,
	CASE 
		WHEN customer.name = "Brunswick Boat Group, Fort Wayne Operatio" THEN "Brunswick"
        WHEN customer.name = "GODFREY MARINE-HURRICANE" THEN "Godfrey"
        WHEN customer.name = "MARINE MOORING, INC." THEN "Marine Mooring"
        WHEN customer.name = "Bennington Pontoon Boats" THEN "Bennington"
        ELSE customer.name
	END AS customerName,
    so.dateFirstShip AS dueDate,
    -- DATE_SUB(so.dateFirstShip, INTERVAL 14 DAY) AS cutDate,
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