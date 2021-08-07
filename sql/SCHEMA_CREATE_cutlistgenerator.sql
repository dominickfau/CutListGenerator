DROP DATABASE IF EXISTS `cutlistgenerator`;
CREATE DATABASE `cutlistgenerator` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `cutlistgenerator`;
DROP TABLE IF EXISTS `cutlist`;

CREATE TABLE `databaseversion` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dateUpdated` datetime(6) DEFAULT NULL,
  `version` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UKd2crfgsuo4c4raueftf2a3v0l` (`version`),
  KEY `databaseVersionVersionIdx` (`version`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `product` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `number` varchar(45) NOT NULL,
  `description` varchar(255) NOT NULL,
  `unit_price_dollars` decimal(28,9) NOT NULL DEFAULT '0.000000000',
  `kit_flag` bit(1) NOT NULL DEFAULT b'0',
  `parent_kit_product_number` varchar(45) DEFAULT NULL,
  `uom` varchar(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `number_UNIQUE` (`number`),
  KEY `IDK_bviufgifbiudgljdfiuhd` (`number`),
  KEY `IFD_biusbfjknfiufbjrweerw` (`kit_flag`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `wire_cutter_option` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`),
  KEY `IDX_bifbvnivbiuwkjdfghn` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `wire_cutter` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `max_wire_gauge_awg` int(11) DEFAULT NULL,
  `processing_speed_feet_per_minute` int(11) DEFAULT NULL,
  `details` varchar(255) DEFAULT NULL,
  `date_created` datetime(6) NOT NULL,
  `date_modified` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `wire_cutter_to_wire_cutter_option` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `wire_cutter_id` int(11) NOT NULL,
  `wire_cutter_option_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_usidfbviadflkjnbbkjhjfgnf_idx` (`wire_cutter_id`),
  KEY `FK_vbiuakjdfbjkdvkjdfbkjfhg_idx` (`wire_cutter_option_id`),
  CONSTRAINT `FK_usidfbviadflkjnbbkjhjfgnf` FOREIGN KEY (`wire_cutter_id`) REFERENCES `wire_cutter` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_vbiuakjdfbjkdvkjdfbkjfhg` FOREIGN KEY (`wire_cutter_option_id`) REFERENCES `wire_cutter_option` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `sales_order` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `customer_name` varchar(255) NOT NULL,
  `due_date` datetime(6) NOT NULL,
  `number` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `number_UNIQUE` (`number`),
  KEY `IDX_bfuiargjahfkjdfuherjf` (`number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `sales_order_item` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sales_order_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `quantity_requseted` decimal(28,9) NOT NULL,
  `line_number` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_buiajikfbgiuadfrgkijsfgbkj_idx` (`sales_order_id`),
  KEY `FK_buiwejfgbuiwefjhbghjarg_idx` (`product_id`),
  CONSTRAINT `FK_buiajikfbgiuadfrgkijsfgbkj` FOREIGN KEY (`sales_order_id`) REFERENCES `sales_order` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_buiwejfgbuiwefjhbghjarg` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;