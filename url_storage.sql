/*
SQLyog Ultimate v11.11 (64 bit)
MySQL - 5.7.18-log (cetus 0.8.8) : Database - szlcsc
*********************************************************************
*/


/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
USE `szlcsc`;

/*Table structure for table `ecs_goods_ic_stat_item_0` */

CREATE TABLE `ecs_goods_ic_stat_item_0` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `dgk_goods_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '芯城商品ID，分表字段',
  `goods_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '自营库存ID',
  `goods_no` varchar(16) NOT NULL DEFAULT '' COMMENT '商品编码',
  `goods_name` varchar(120) NOT NULL DEFAULT '' COMMENT '商品型号',
  `provider_name` varchar(100) NOT NULL DEFAULT '' COMMENT '品牌',
  `dayint` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '8位整型格式的天：20191119',
  `sale_amount` decimal(15,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '历史以来总销售额',
  `spot_amount` decimal(15,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '当前现货总额',
  `intransit_amount` decimal(15,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '当前在途总额',
  `add_time` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '数据创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `goods_id` (`goods_id`,`dayint`),
  KEY `dgk_goods_id` (`dgk_goods_id`),
  KEY `goods_no` (`goods_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='自营库存明细周转率统计数据';

/*Table structure for table `ecs_goods_ic_stat_item_1` */

CREATE TABLE `ecs_goods_ic_stat_item_1` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `dgk_goods_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '芯城商品ID，分表字段',
  `goods_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '自营库存ID',
  `goods_no` varchar(16) NOT NULL DEFAULT '' COMMENT '商品编码',
  `goods_name` varchar(120) NOT NULL DEFAULT '' COMMENT '商品型号',
  `provider_name` varchar(100) NOT NULL DEFAULT '' COMMENT '品牌',
  `dayint` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '8位整型格式的天：20191119',
  `sale_amount` decimal(15,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '历史以来总销售额',
  `spot_amount` decimal(15,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '当前现货总额',
  `intransit_amount` decimal(15,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '当前在途总额',
  `add_time` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '数据创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `goods_id` (`goods_id`,`dayint`),
  KEY `dgk_goods_id` (`dgk_goods_id`),
  KEY `goods_no` (`goods_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='自营库存明细周转率统计数据';

/*Table structure for table `ecs_goods_ic_stat_item_2` */

CREATE TABLE `ecs_goods_ic_stat_item_2` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `dgk_goods_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '芯城商品ID，分表字段',
  `goods_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '自营库存ID',
  `goods_no` varchar(16) NOT NULL DEFAULT '' COMMENT '商品编码',
  `goods_name` varchar(120) NOT NULL DEFAULT '' COMMENT '商品型号',
  `provider_name` varchar(100) NOT NULL DEFAULT '' COMMENT '品牌',
  `dayint` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '8位整型格式的天：20191119',
  `sale_amount` decimal(15,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '历史以来总销售额',
  `spot_amount` decimal(15,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '当前现货总额',
  `intransit_amount` decimal(15,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '当前在途总额',
  `add_time` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '数据创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `goods_id` (`goods_id`,`dayint`),
  KEY `dgk_goods_id` (`dgk_goods_id`),
  KEY `goods_no` (`goods_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='自营库存明细周转率统计数据';

/*Table structure for table `ecs_goods_ic_stat_item_4` */

CREATE TABLE `ecs_goods_ic_stat_item_4` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `dgk_goods_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '芯城商品ID，分表字段',
  `goods_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '自营库存ID',
  `goods_no` varchar(16) NOT NULL DEFAULT '' COMMENT '商品编码',
  `goods_name` varchar(120) NOT NULL DEFAULT '' COMMENT '商品型号',
  `provider_name` varchar(100) NOT NULL DEFAULT '' COMMENT '品牌',
  `dayint` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '8位整型格式的天：20191119',
  `sale_amount` decimal(15,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '历史以来总销售额',
  `spot_amount` decimal(15,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '当前现货总额',
  `intransit_amount` decimal(15,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '当前在途总额',
  `add_time` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '数据创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `goods_id` (`goods_id`,`dayint`),
  KEY `dgk_goods_id` (`dgk_goods_id`),
  KEY `goods_no` (`goods_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='自营库存明细周转率统计数据';

/*Table structure for table `ecs_goods_ic_stat_item_5` */

CREATE TABLE `ecs_goods_ic_stat_item_5` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `dgk_goods_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '芯城商品ID，分表字段',
  `goods_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '自营库存ID',
  `goods_no` varchar(16) NOT NULL DEFAULT '' COMMENT '商品编码',
  `goods_name` varchar(120) NOT NULL DEFAULT '' COMMENT '商品型号',
  `provider_name` varchar(100) NOT NULL DEFAULT '' COMMENT '品牌',
  `dayint` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '8位整型格式的天：20191119',
  `sale_amount` decimal(15,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '历史以来总销售额',
  `spot_amount` decimal(15,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '当前现货总额',
  `intransit_amount` decimal(15,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '当前在途总额',
  `add_time` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '数据创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `goods_id` (`goods_id`,`dayint`),
  KEY `dgk_goods_id` (`dgk_goods_id`),
  KEY `goods_no` (`goods_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='自营库存明细周转率统计数据';

/*Table structure for table `ecs_goods_ic_stat_item_6` */

CREATE TABLE `ecs_goods_ic_stat_item_6` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `dgk_goods_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '芯城商品ID，分表字段',
  `goods_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '自营库存ID',
  `goods_no` varchar(16) NOT NULL DEFAULT '' COMMENT '商品编码',
  `goods_name` varchar(120) NOT NULL DEFAULT '' COMMENT '商品型号',
  `provider_name` varchar(100) NOT NULL DEFAULT '' COMMENT '品牌',
  `dayint` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '8位整型格式的天：20191119',
  `sale_amount` decimal(15,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '历史以来总销售额',
  `spot_amount` decimal(15,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '当前现货总额',
  `intransit_amount` decimal(15,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '当前在途总额',
  `add_time` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '数据创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `goods_id` (`goods_id`,`dayint`),
  KEY `dgk_goods_id` (`dgk_goods_id`),
  KEY `goods_no` (`goods_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='自营库存明细周转率统计数据';

/*Table structure for table `ecs_goods_ic_stat_item_7` */

CREATE TABLE `ecs_goods_ic_stat_item_7` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `dgk_goods_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '芯城商品ID，分表字段',
  `goods_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '自营库存ID',
  `goods_no` varchar(16) NOT NULL DEFAULT '' COMMENT '商品编码',
  `goods_name` varchar(120) NOT NULL DEFAULT '' COMMENT '商品型号',
  `provider_name` varchar(100) NOT NULL DEFAULT '' COMMENT '品牌',
  `dayint` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '8位整型格式的天：20191119',
  `sale_amount` decimal(15,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '历史以来总销售额',
  `spot_amount` decimal(15,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '当前现货总额',
  `intransit_amount` decimal(15,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '当前在途总额',
  `add_time` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '数据创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `goods_id` (`goods_id`,`dayint`),
  KEY `dgk_goods_id` (`dgk_goods_id`),
  KEY `goods_no` (`goods_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='自营库存明细周转率统计数据';

/*Table structure for table `ecs_goods_ic_stat_item_8` */

CREATE TABLE `ecs_goods_ic_stat_item_8` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `dgk_goods_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '芯城商品ID，分表字段',
  `goods_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '自营库存ID',
  `goods_no` varchar(16) NOT NULL DEFAULT '' COMMENT '商品编码',
  `goods_name` varchar(120) NOT NULL DEFAULT '' COMMENT '商品型号',
  `provider_name` varchar(100) NOT NULL DEFAULT '' COMMENT '品牌',
  `dayint` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '8位整型格式的天：20191119',
  `sale_amount` decimal(15,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '历史以来总销售额',
  `spot_amount` decimal(15,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '当前现货总额',
  `intransit_amount` decimal(15,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '当前在途总额',
  `add_time` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '数据创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `goods_id` (`goods_id`,`dayint`),
  KEY `dgk_goods_id` (`dgk_goods_id`),
  KEY `goods_no` (`goods_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='自营库存明细周转率统计数据';

/*Table structure for table `ecs_goods_ic_stat_item_9` */

CREATE TABLE `ecs_goods_ic_stat_item_9` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `dgk_goods_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '芯城商品ID，分表字段',
  `goods_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '自营库存ID',
  `goods_no` varchar(16) NOT NULL DEFAULT '' COMMENT '商品编码',
  `goods_name` varchar(120) NOT NULL DEFAULT '' COMMENT '商品型号',
  `provider_name` varchar(100) NOT NULL DEFAULT '' COMMENT '品牌',
  `dayint` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '8位整型格式的天：20191119',
  `sale_amount` decimal(15,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '历史以来总销售额',
  `spot_amount` decimal(15,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '当前现货总额',
  `intransit_amount` decimal(15,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '当前在途总额',
  `add_time` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '数据创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `goods_id` (`goods_id`,`dayint`),
  KEY `dgk_goods_id` (`dgk_goods_id`),
  KEY `goods_no` (`goods_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='自营库存明细周转率统计数据';

/*Table structure for table `ecs_ickey_brand` */

CREATE TABLE `ecs_ickey_brand` (
  `brand_id` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `brand_name` varchar(60) NOT NULL DEFAULT '' COMMENT '品牌名称',
  `brand_logo` varchar(200) NOT NULL DEFAULT '' COMMENT '品牌logo',
  `brand_desc` text NOT NULL COMMENT '品牌描述',
  `first_letter` char(1) NOT NULL COMMENT '首字母',
  `site_url` varchar(255) DEFAULT NULL COMMENT '品牌站点url',
  `digikey` varchar(255) NOT NULL DEFAULT '' COMMENT '源站url',
  `sort_order` tinyint(3) unsigned NOT NULL DEFAULT '50' COMMENT '排序',
  `is_show` tinyint(1) unsigned NOT NULL DEFAULT '1' COMMENT '展示',
  `goods_count` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '商品数量',
  `is_recom` tinyint(1) unsigned NOT NULL DEFAULT '0' COMMENT '推荐',
  PRIMARY KEY (`brand_id`),
  UNIQUE KEY `brand_name` (`brand_name`),
  KEY `is_show` (`is_show`),
  KEY `first_letter` (`first_letter`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='立创品牌表';

/*Table structure for table `ic_brand` */

CREATE TABLE `ic_brand` (
  `brand_id` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `brand_name` varchar(60) NOT NULL DEFAULT '',
  `brand_logo` varchar(200) NOT NULL DEFAULT '',
  `brand_desc` text NOT NULL,
  `first_letter` char(1) NOT NULL,
  `site_url` varchar(255) DEFAULT NULL,
  `digikey` varchar(255) NOT NULL DEFAULT '',
  `sort_order` tinyint(3) unsigned NOT NULL DEFAULT '50',
  `is_show` tinyint(1) unsigned NOT NULL DEFAULT '1',
  `goods_count` int(10) unsigned NOT NULL DEFAULT '0',
  `is_recom` tinyint(1) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`brand_id`),
  UNIQUE KEY `brand_name` (`brand_name`),
  KEY `is_show` (`is_show`),
  KEY `first_letter` (`first_letter`)
) ENGINE=MyISAM AUTO_INCREMENT=1312 DEFAULT CHARSET=utf8;

/*Table structure for table `ic_category` */

CREATE TABLE `ic_category` (
  `cat_id` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `cat_name` varchar(90) NOT NULL DEFAULT '',
  `cat_desc` varchar(255) NOT NULL DEFAULT '',
  `parent_id` smallint(5) unsigned NOT NULL DEFAULT '0',
  `grade` tinyint(4) NOT NULL DEFAULT '0',
  `filter_attr` varchar(255) NOT NULL DEFAULT '0',
  `url` varchar(255) NOT NULL,
  `goods_count` int(10) unsigned NOT NULL DEFAULT '0',
  `islast` tinyint(1) unsigned NOT NULL,
  `level` tinyint(1) unsigned NOT NULL DEFAULT '1',
  PRIMARY KEY (`cat_id`),
  KEY `cat_name` (`cat_name`)
) ENGINE=MyISAM AUTO_INCREMENT=436 DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods` */

CREATE TABLE `ic_goods` (
  `goods_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `cat_id` smallint(5) unsigned NOT NULL DEFAULT '0',
  `goods_sn` varchar(60) NOT NULL DEFAULT '',
  `goods_name` varchar(120) NOT NULL DEFAULT '',
  `goods_name_style` varchar(60) NOT NULL DEFAULT '+',
  `brand_id` smallint(5) unsigned NOT NULL DEFAULT '0',
  `provider_name` varchar(100) NOT NULL DEFAULT '',
  `doc_url` varchar(255) NOT NULL DEFAULT '',
  `goods_number` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '库存数量',
  `goods_weight` decimal(10,3) unsigned NOT NULL DEFAULT '0.000',
  `shop_price` decimal(10,4) unsigned NOT NULL DEFAULT '0.0000',
  `min_buynum` mediumint(8) unsigned NOT NULL DEFAULT '1',
  `keywords` varchar(255) NOT NULL DEFAULT '',
  `goods_desc` text NOT NULL,
  `goods_thumb` varchar(255) NOT NULL DEFAULT '',
  `goods_img` varchar(255) NOT NULL DEFAULT '',
  `original_img` varchar(255) NOT NULL DEFAULT '',
  `is_real` tinyint(3) unsigned NOT NULL DEFAULT '1',
  `extension_code` varchar(30) NOT NULL DEFAULT '',
  `is_on_sale` tinyint(1) unsigned NOT NULL DEFAULT '1',
  `add_time` int(10) unsigned NOT NULL DEFAULT '0',
  `sort_order` smallint(4) unsigned NOT NULL DEFAULT '100',
  `bonus_type_id` tinyint(3) unsigned NOT NULL DEFAULT '0',
  `last_update` int(10) unsigned NOT NULL DEFAULT '0',
  `goods_type` smallint(5) unsigned NOT NULL DEFAULT '1',
  `seller_note` varchar(255) NOT NULL DEFAULT '',
  `suppliers_id` smallint(5) unsigned DEFAULT NULL,
  `digikey_url` varchar(500) NOT NULL DEFAULT '',
  `series` varchar(255) NOT NULL DEFAULT '',
  `source_type` tinyint(3) unsigned NOT NULL DEFAULT '0',
  `sale_count` mediumint(8) unsigned NOT NULL DEFAULT '0',
  `is_rohs` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `is_insert` tinyint(1) unsigned DEFAULT '0',
  `package` varchar(255) DEFAULT '-' COMMENT '封装规格',
  `increment` smallint(5) DEFAULT '1' COMMENT '产品增量',
  `sale_unit` varchar(16) NOT NULL DEFAULT '' COMMENT '销售单位',
  `min_unit_str` varchar(60) NOT NULL DEFAULT '' COMMENT '最小单位描述',
  `min_unit` varchar(16) NOT NULL DEFAULT '' COMMENT '最小单位',
  `purchase_limit` tinyint(1) unsigned NOT NULL DEFAULT '0' COMMENT '限购 0不限购',
  `is_hot` tinyint(1) NOT NULL DEFAULT '0' COMMENT '热销型号',
  `market_price` tinyint(4) DEFAULT '0' COMMENT '折扣',
  PRIMARY KEY (`goods_id`),
  UNIQUE KEY `goods_sn` (`goods_sn`),
  KEY `cat_id` (`cat_id`),
  KEY `brand_id` (`brand_id`),
  KEY `goods_name` (`goods_name`),
  KEY `goods_name_style` (`goods_name_style`)
) ENGINE=MyISAM AUTO_INCREMENT=3600256599 DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_price_0` */

CREATE TABLE `ic_goods_price_0` (
  `goods_id` int(10) unsigned NOT NULL,
  `price` text NOT NULL,
  PRIMARY KEY (`goods_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_price_1` */

CREATE TABLE `ic_goods_price_1` (
  `goods_id` int(10) unsigned NOT NULL,
  `price` text NOT NULL,
  PRIMARY KEY (`goods_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_price_2` */

CREATE TABLE `ic_goods_price_2` (
  `goods_id` int(10) unsigned NOT NULL,
  `price` text NOT NULL,
  PRIMARY KEY (`goods_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_price_3` */

CREATE TABLE `ic_goods_price_3` (
  `goods_id` int(10) unsigned NOT NULL,
  `price` text NOT NULL,
  PRIMARY KEY (`goods_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_price_4` */

CREATE TABLE `ic_goods_price_4` (
  `goods_id` int(10) unsigned NOT NULL,
  `price` text NOT NULL,
  PRIMARY KEY (`goods_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_price_5` */

CREATE TABLE `ic_goods_price_5` (
  `goods_id` int(10) unsigned NOT NULL,
  `price` text NOT NULL,
  PRIMARY KEY (`goods_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_price_6` */

CREATE TABLE `ic_goods_price_6` (
  `goods_id` int(10) unsigned NOT NULL,
  `price` text NOT NULL,
  PRIMARY KEY (`goods_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_price_7` */

CREATE TABLE `ic_goods_price_7` (
  `goods_id` int(10) unsigned NOT NULL,
  `price` text NOT NULL,
  PRIMARY KEY (`goods_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_price_8` */

CREATE TABLE `ic_goods_price_8` (
  `goods_id` int(10) unsigned NOT NULL,
  `price` text NOT NULL,
  PRIMARY KEY (`goods_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_price_9` */

CREATE TABLE `ic_goods_price_9` (
  `goods_id` int(10) unsigned NOT NULL,
  `price` text NOT NULL,
  PRIMARY KEY (`goods_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_sale_0` */

CREATE TABLE `ic_goods_sale_0` (
  `goods_id` int(12) unsigned DEFAULT NULL COMMENT '商品id',
  `time` int(15) DEFAULT NULL COMMENT '购买时间戳',
  `customerCode` varchar(20) DEFAULT NULL COMMENT '顾客标识',
  `num` varchar(12) DEFAULT NULL COMMENT '购买数量',
  UNIQUE KEY `goods_id` (`goods_id`,`time`,`customerCode`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_sale_1` */

CREATE TABLE `ic_goods_sale_1` (
  `goods_id` int(12) unsigned DEFAULT NULL COMMENT '商品id',
  `time` int(15) DEFAULT NULL COMMENT '购买时间戳',
  `customerCode` varchar(20) DEFAULT NULL COMMENT '顾客标识',
  `num` varchar(12) DEFAULT NULL COMMENT '购买数量',
  UNIQUE KEY `goods_id` (`goods_id`,`time`,`customerCode`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_sale_2` */

CREATE TABLE `ic_goods_sale_2` (
  `goods_id` int(12) unsigned DEFAULT NULL COMMENT '商品id',
  `time` int(15) DEFAULT NULL COMMENT '购买时间戳',
  `customerCode` varchar(20) DEFAULT NULL COMMENT '顾客标识',
  `num` varchar(8) DEFAULT NULL COMMENT '购买数量',
  UNIQUE KEY `goods_id` (`goods_id`,`time`,`customerCode`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_sale_3` */

CREATE TABLE `ic_goods_sale_3` (
  `goods_id` int(12) unsigned DEFAULT NULL COMMENT '商品id',
  `time` int(15) DEFAULT NULL COMMENT '购买时间戳',
  `customerCode` varchar(20) DEFAULT NULL COMMENT '顾客标识',
  `num` varchar(12) DEFAULT NULL COMMENT '购买数量',
  UNIQUE KEY `goods_id` (`goods_id`,`time`,`customerCode`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_sale_4` */

CREATE TABLE `ic_goods_sale_4` (
  `goods_id` int(12) unsigned DEFAULT NULL COMMENT '商品id',
  `time` int(15) DEFAULT NULL COMMENT '购买时间戳',
  `customerCode` varchar(20) DEFAULT NULL COMMENT '顾客标识',
  `num` varchar(12) DEFAULT NULL COMMENT '购买数量',
  UNIQUE KEY `goods_id` (`goods_id`,`time`,`customerCode`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_sale_5` */

CREATE TABLE `ic_goods_sale_5` (
  `goods_id` int(12) unsigned DEFAULT NULL COMMENT '商品id',
  `time` int(15) DEFAULT NULL COMMENT '购买时间戳',
  `customerCode` varchar(20) DEFAULT NULL COMMENT '顾客标识',
  `num` varchar(12) DEFAULT NULL COMMENT '购买数量',
  UNIQUE KEY `goods_id` (`goods_id`,`time`,`customerCode`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_sale_6` */

CREATE TABLE `ic_goods_sale_6` (
  `goods_id` int(12) unsigned DEFAULT NULL COMMENT '商品id',
  `time` int(15) DEFAULT NULL COMMENT '购买时间戳',
  `customerCode` varchar(20) DEFAULT NULL COMMENT '顾客标识',
  `num` varchar(12) DEFAULT NULL COMMENT '购买数量',
  UNIQUE KEY `goods_id` (`goods_id`,`time`,`customerCode`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_sale_7` */

CREATE TABLE `ic_goods_sale_7` (
  `goods_id` int(12) unsigned DEFAULT NULL COMMENT '商品id',
  `time` int(15) DEFAULT NULL COMMENT '购买时间戳',
  `customerCode` varchar(20) DEFAULT NULL COMMENT '顾客标识',
  `num` varchar(12) DEFAULT NULL COMMENT '购买数量',
  UNIQUE KEY `goods_id` (`goods_id`,`time`,`customerCode`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_sale_8` */

CREATE TABLE `ic_goods_sale_8` (
  `goods_id` int(12) unsigned DEFAULT NULL COMMENT '商品id',
  `time` int(15) DEFAULT NULL COMMENT '购买时间戳',
  `customerCode` varchar(20) DEFAULT NULL COMMENT '顾客标识',
  `num` varchar(12) DEFAULT NULL COMMENT '购买数量',
  UNIQUE KEY `goods_id` (`goods_id`,`time`,`customerCode`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_sale_9` */

CREATE TABLE `ic_goods_sale_9` (
  `goods_id` int(12) unsigned DEFAULT NULL COMMENT '商品id',
  `time` int(15) DEFAULT NULL COMMENT '购买时间戳',
  `customerCode` varchar(20) DEFAULT NULL COMMENT '顾客标识',
  `num` varchar(12) DEFAULT NULL COMMENT '购买数量',
  UNIQUE KEY `goods_id` (`goods_id`,`time`,`customerCode`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_page` */

CREATE TABLE `ic_page` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `cat_id` int(10) unsigned NOT NULL COMMENT '分类id',
  `url` varchar(300) NOT NULL,
  `status` tinyint(1) unsigned NOT NULL DEFAULT '0' COMMENT '是否抓取成功',
  PRIMARY KEY (`id`),
  UNIQUE KEY `url` (`url`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_url` */

CREATE TABLE `ic_url` (
  `goods_id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '芯片id',
  `cat_id` int(10) unsigned NOT NULL COMMENT '分类id',
  `id` int(10) unsigned NOT NULL COMMENT '目标网站芯片对应的id',
  `url` varchar(500) NOT NULL COMMENT '目标网站芯片地址',
  `status` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否采集',
  PRIMARY KEY (`goods_id`),
  KEY `cat_id` (`cat_id`),
  KEY `id` (`id`),
  KEY `url` (`url`(333))
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
