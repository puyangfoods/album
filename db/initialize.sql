create table if not exists shop_status (
    `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
    `timestamp` int(11) unsigned NOT NULL,
    `shop_id` smallint(6) unsigned NOT NULL,
    `shop_name` varchar(255) NOT NULL,
    `status` tinyint(4) unsigned NOT NULL,
    primary key (`id`),
    index t (`timestamp`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
