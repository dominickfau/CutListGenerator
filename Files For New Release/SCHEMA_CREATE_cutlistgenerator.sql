DROP DATABASE IF EXISTS `cutlistgenerator_test`;
CREATE DATABASE `cutlistgenerator_test` DEFAULT CHARACTER SET utf8;
USE `cutlistgenerator_test`;

CREATE TABLE `system_properties` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date_last_modified` datetime(6) DEFAULT NULL,
  `read_only` bit(1) NOT NULL,
  `name` varchar(255) NOT NULL,
  `value` varchar(1024) NOT NULL,
  `visible` bit(1) NOT NULL,
  `value_type` varchar(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK_osp7t6r0heujnkqu21sxoqhgd` (`name`),
  KEY `sysPropertiesSysKeyIdx` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `database_version` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date_updated` datetime(6) DEFAULT NULL,
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
  `number` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `number_UNIQUE` (`number`),
  KEY `IDX_bfuiargjahfkjdfuherjf` (`number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `sales_order_item` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sales_order_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `qty_to_fulfill` decimal(28,9) NOT NULL,
  `qty_fulfilled` decimal(28,9) NOT NULL,
  `qty_picked` decimal(28,9) NOT NULL,
  `line_number` int(11) NOT NULL,
  `due_date` datetime(6) NOT NULL,
  `cut_in_full` bit(1) NOT NULL DEFAULT b'0',
  `date_added` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_buiajikfbgiuadfrgkijsfgbkj_idx` (`sales_order_id`),
  KEY `FK_buiwejfgbuiwefjhbghjarg_idx` (`product_id`),
  CONSTRAINT `FK_buiajikfbgiuadfrgkijsfgbkj` FOREIGN KEY (`sales_order_id`) REFERENCES `sales_order` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_buiwejfgbuiwefjhbghjarg` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `parent_to_child_product` (
  `child_product_id` int(11) NOT NULL,
  `parent_product_id` int(11) NOT NULL,
  PRIMARY KEY (`child_product_id`,`parent_product_id`),
  KEY `FK_hogjqwjhvbjhqwdkjvfdjh_idx` (`parent_product_id`),
  CONSTRAINT `FK_guiwjkfijhwjhqwekjfgdsjb` FOREIGN KEY (`child_product_id`) REFERENCES `product` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_hogjqwjhvbjhqwdkjvfdjh` FOREIGN KEY (`parent_product_id`) REFERENCES `product` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `cut_job` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `product_id` int(11) NOT NULL,
  `related_sales_order_item_id` int(11) DEFAULT NULL,
  `assigned_wire_cutter_id` int(11) NOT NULL,
  `quantity_cut` decimal(28,9) DEFAULT NULL,
  `date_cut_start` datetime(6) DEFAULT NULL,
  `date_cut_end` datetime(6) DEFAULT NULL,
  `date_termination_start` datetime(6) DEFAULT NULL,
  `date_termination_end` datetime(6) DEFAULT NULL,
  `date_splice_start` datetime(6) DEFAULT NULL,
  `date_splice_end` datetime(6) DEFAULT NULL,
  `is_cut` bit(1) NOT NULL DEFAULT b'0',
  `is_spliced` bit(1) NOT NULL DEFAULT b'0',
  `is_terminated` bit(1) NOT NULL DEFAULT b'0',
  `is_ready_for_build` bit(1) NOT NULL DEFAULT b'0',
  `date_created` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_feiugebuihadfjhflfbakuhff_idx` (`related_sales_order_item_id`),
  KEY `FK_herakjhgjhwerjdfvkjejhfg_idx` (`product_id`),
  KEY `FK_giokjgbkhfkjjhwekjhfkuir_idx` (`assigned_wire_cutter_id`),
  KEY `IDX_giwkjgkeknfbgidkjg` (`is_cut`,`is_spliced`,`is_terminated`,`is_ready_for_build`),
  CONSTRAINT `FK_feiugebuihadfjhflfbakuhff` FOREIGN KEY (`related_sales_order_item_id`) REFERENCES `sales_order_item` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_giokjgbkhfkjjhwekjhfkuir` FOREIGN KEY (`assigned_wire_cutter_id`) REFERENCES `wire_cutter` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_herakjhgjhwerjdfvkjejhfg` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `customer_name_conversion` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `from_` varchar(100) NOT NULL,
  `to_` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `from__UNIQUE` (`from_`),
  UNIQUE KEY `to__UNIQUE` (`to_`),
  KEY `IDX_from_` (`from_`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `exclude_product_number` (
  `part_number` varchar(45) NOT NULL,
  PRIMARY KEY (`part_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='This table represents all product numbers to skip, when importing SO data from Fishbowl.';


-- TRIGGERS
DROP TRIGGER IF EXISTS `sales_order_item_BEFORE_INSERT`;

DELIMITER $$
CREATE DEFINER = CURRENT_USER TRIGGER `sales_order_item_BEFORE_INSERT` BEFORE INSERT ON `sales_order_item` FOR EACH ROW
BEGIN
	SET NEW.date_added = NOW();
END$$
DELIMITER ;


-- Views
DROP VIEW IF EXISTS `parent_child_product_relationship`;

CREATE VIEW `parent_child_product_relationship` AS
SELECT 
	parent_product.id AS parent_product_id,
	parent_product.number AS parent_product_number,
	parent_product.description AS parent_product_description,
	parent_product.uom AS parent_product_uom,
	child_product.id AS child_product_id,
	child_product.number AS child_product_number,
	child_product.description AS child_product_description,
	child_product.uom AS child_product_uom
FROM product parent_product
LEFT JOIN parent_to_child_product ON parent_to_child_product.parent_product_id = parent_product.id
LEFT JOIN product child_product ON parent_to_child_product.child_product_id = child_product.id
ORDER BY parent_product.number;


DROP VIEW IF EXISTS `sales_orders`;

CREATE VIEW `sales_orders` AS
SELECT
	sales_order.id AS sales_order_id,
	sales_order_item.date_added AS date_added,
	sales_order_item.due_date AS due_date,
	sales_order.customer_name AS customer_name,
	sales_order.number AS sales_order_number,
    sales_order_item.id AS sales_order_item_id,
	product.number AS product_number,
	product.description AS product_description,
	product.unit_price_dollars AS unit_price_dollars,
	product.uom AS product_uom,
	sales_order_item.qty_to_fulfill AS qty_to_fulfill,
	sales_order_item.qty_picked AS qty_picked,
	sales_order_item.qty_fulfilled AS qty_fulfilled,
	(sales_order_item.qty_to_fulfill - sales_order_item.qty_picked - sales_order_item.qty_fulfilled) AS qty_left_to_ship,
	sales_order_item.cut_in_full AS cut_in_full
FROM sales_order
JOIN sales_order_item ON sales_order.id = sales_order_item.sales_order_id
JOIN product ON sales_order_item.product_id = product.id;


DROP VIEW IF EXISTS `so_items_to_cut`;

CREATE VIEW `so_items_to_cut` AS
SELECT
	sales_order_item.id AS so_id,
	DATE_FORMAT(sales_order_item.due_date, '%c-%e-%Y') AS so_item_due_date,
	sales_order.customer_name AS customer_name,
	sales_order.number AS so_number,
	product.number AS product_number,
	product.description AS description,
	product.unit_price_dollars AS unit_price,
	(sales_order_item.qty_to_fulfill - sales_order_item.qty_fulfilled - sales_order_item.qty_picked) AS qty_left_to_ship,
	product.uom AS uom,
	sales_order_item.line_number AS line_number,
	product.kit_flag AS is_child_item,
	sales_order_item.cut_in_full AS fully_cut,
	parent_product.number AS parent_number,
	parent_product.description AS parent_description
FROM sales_order
JOIN sales_order_item ON sales_order_item.sales_order_id = sales_order.id
JOIN product ON sales_order_item.product_id = product.id
LEFT JOIN parent_to_child_product ON parent_to_child_product.child_product_id = product.id
LEFT JOIN product parent_product ON parent_to_child_product.parent_product_id = parent_product.id
ORDER BY product.number, sales_order_item.due_date;


DROP VIEW IF EXISTS `wire_cutter_with_options`;

CREATE VIEW `wire_cutter_with_options` AS
SELECT
	wire_cutter.id AS wire_cutter_id,
	wire_cutter.name AS wire_cutter_name,
	wire_cutter.max_wire_gauge_awg AS max_wire_gauge_awg,
	wire_cutter.processing_speed_feet_per_minute AS processing_speed_feet_per_minute,
	wire_cutter.details AS details,
	wire_cutter_option.id AS wire_cutter_option_id,
	wire_cutter_option.name AS wire_cutter_option_name,
	wire_cutter_option.description AS wire_cutter_option_description
FROM wire_cutter
LEFT JOIN wire_cutter_to_wire_cutter_option ON wire_cutter.id = wire_cutter_to_wire_cutter_option.wire_cutter_id
LEFT JOIN wire_cutter_option ON wire_cutter_to_wire_cutter_option.wire_cutter_option_id;