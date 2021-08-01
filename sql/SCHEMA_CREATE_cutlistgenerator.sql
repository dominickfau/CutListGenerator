DROP DATABASE IF EXISTS `cutlistgenerator`;
CREATE DATABASE `cutlistgenerator` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `cutlistgenerator`;
DROP TABLE IF EXISTS `cutlist`;

CREATE TABLE `cutlist` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `addedToCutListFlag` bit(1) DEFAULT b'0',
  `assignedCutter` varchar(255) DEFAULT NULL,
  `customerName` varchar(255) NOT NULL,
  `cutFlag` bit(1) NOT NULL DEFAULT b'0',
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
  `splicedFlag` bit(1) NOT NULL DEFAULT b'0',
  `terminatedFlag` bit(1) NOT NULL DEFAULT b'0',
  `uom` varchar(15) NOT NULL,
  `readyForBuild` bit(1) NOT NULL DEFAULT b'0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;