TABLE_DATA = {
    'system_properties': {
        {
            'create': """CREATE TABLE `system_properties` (
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
                            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
                
        }
    },
    'database_version': {
        {
            'create': """CREATE TABLE `database_version` (
                            `id` int(11) NOT NULL AUTO_INCREMENT,
                            `date_updated` datetime(6) DEFAULT NULL,
                            `version` int(11) NOT NULL,
                            PRIMARY KEY (`id`),
                            UNIQUE KEY `UKd2crfgsuo4c4raueftf2a3v0l` (`version`),
                            KEY `databaseVersionVersionIdx` (`version`)
                            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        }
    },
    'product': {
        {
            'create': """CREATE TABLE `product` (
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
                            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        }
    },
    'wire_cutter_option': {
        {
            'create': """CREATE TABLE `wire_cutter_option` (
                        `id` int(11) NOT NULL AUTO_INCREMENT,
                        `name` varchar(255) NOT NULL,
                        `description` varchar(255) DEFAULT NULL,
                        PRIMARY KEY (`id`),
                        UNIQUE KEY `name_UNIQUE` (`name`),
                        KEY `IDX_bifbvnivbiuwkjdfghn` (`name`)
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        }
    },
    'wire_cutter': {
        {
            'create': """CREATE TABLE `wire_cutter` (
                            `id` int(11) NOT NULL AUTO_INCREMENT,
                            `name` varchar(255) NOT NULL,
                            `max_wire_gauge_awg` int(11) DEFAULT NULL,
                            `processing_speed_feet_per_minute` int(11) DEFAULT NULL,
                            `details` varchar(255) DEFAULT NULL,
                            `date_created` datetime(6) NOT NULL,
                            `date_modified` datetime(6) NOT NULL,
                            PRIMARY KEY (`id`),
                            UNIQUE KEY `name_UNIQUE` (`name`)
                            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        }
    },
    'wire_cutter_to_wire_cutter_option': {
        {
            'create': """CREATE TABLE `wire_cutter_to_wire_cutter_option` (
                            `id` int(11) NOT NULL AUTO_INCREMENT,
                            `wire_cutter_id` int(11) NOT NULL,
                            `wire_cutter_option_id` int(11) NOT NULL,
                            PRIMARY KEY (`id`),
                            KEY `FK_usidfbviadflkjnbbkjhjfgnf_idx` (`wire_cutter_id`),
                            KEY `FK_vbiuakjdfbjkdvkjdfbkjfhg_idx` (`wire_cutter_option_id`),
                            CONSTRAINT `FK_usidfbviadflkjnbbkjhjfgnf` FOREIGN KEY (`wire_cutter_id`) REFERENCES `wire_cutter` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
                            CONSTRAINT `FK_vbiuakjdfbjkdvkjdfbkjfhg` FOREIGN KEY (`wire_cutter_option_id`) REFERENCES `wire_cutter_option` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
                            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        }
    },
    'sales_order': {
        {
            'create': """CREATE TABLE `sales_order` (
                            `id` int(11) NOT NULL AUTO_INCREMENT,
                            `customer_name` varchar(255) NOT NULL,
                            `number` varchar(255) NOT NULL,
                            PRIMARY KEY (`id`),
                            UNIQUE KEY `number_UNIQUE` (`number`),
                            KEY `IDX_bfuiargjahfkjdfuherjf` (`number`)
                            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        }
    },
    'sales_order_item': {
        {
            'create': """CREATE TABLE `sales_order_item` (
                            `id` int(11) NOT NULL AUTO_INCREMENT,
                            `sales_order_id` int(11) NOT NULL,
                            `product_id` int(11) NOT NULL,
                            `qty_to_fulfill` decimal(28,9) NOT NULL,
                            `qty_fulfilled` decimal(28,9) NOT NULL,
                            `qty_picked` decimal(28,9) NOT NULL,
                            `line_number` int(11) NOT NULL,
                            `due_date` datetime(6) NOT NULL,
                            PRIMARY KEY (`id`),
                            KEY `FK_buiajikfbgiuadfrgkijsfgbkj_idx` (`sales_order_id`),
                            KEY `FK_buiwejfgbuiwefjhbghjarg_idx` (`product_id`),
                            CONSTRAINT `FK_buiajikfbgiuadfrgkijsfgbkj` FOREIGN KEY (`sales_order_id`) REFERENCES `sales_order` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
                            CONSTRAINT `FK_buiwejfgbuiwefjhbghjarg` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
                            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        }
    },
    'parent_to_child_product': {
        {
            'create': """CREATE TABLE `parent_to_child_product` (
                            `child_product_id` int(11) NOT NULL,
                            `parent_product_id` int(11) NOT NULL,
                            PRIMARY KEY (`child_product_id`,`parent_product_id`),
                            KEY `FK_hogjqwjhvbjhqwdkjvfdjh_idx` (`parent_product_id`),
                            CONSTRAINT `FK_guiwjkfijhwjhqwekjfgdsjb` FOREIGN KEY (`child_product_id`) REFERENCES `product` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
                            CONSTRAINT `FK_hogjqwjhvbjhqwdkjvfdjh` FOREIGN KEY (`parent_product_id`) REFERENCES `product` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
                            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        }
    }
}