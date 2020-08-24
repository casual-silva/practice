/*
SQLyog Ultimate v11.11 (64 bit)
MySQL - 5.7.18-log (cetus 0.8.8) : Database - wpi
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`wpi` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `wpi`;

/*Table structure for table `ic_brand` */

DROP TABLE IF EXISTS `ic_brand`;

CREATE TABLE `ic_brand` (
  `brand_id` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `brand_name` varchar(60) NOT NULL DEFAULT '',
  `brand_logo` varchar(200) NOT NULL DEFAULT '',
  `brand_desc` text NOT NULL,
  `first_letter` char(1) NOT NULL,
  `site_url` varchar(255) NOT NULL DEFAULT '',
  `digikey` varchar(255) NOT NULL,
  `sort_order` tinyint(3) unsigned NOT NULL DEFAULT '50',
  `is_show` tinyint(1) unsigned NOT NULL DEFAULT '1',
  `goods_count` int(10) unsigned NOT NULL,
  `is_recom` tinyint(1) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`brand_id`),
  UNIQUE KEY `brand_name` (`brand_name`),
  KEY `is_show` (`is_show`),
  KEY `first_letter` (`first_letter`)
) ENGINE=MyISAM AUTO_INCREMENT=550 DEFAULT CHARSET=utf8;

/*Table structure for table `ic_brand_mapping` */

DROP TABLE IF EXISTS `ic_brand_mapping`;

CREATE TABLE `ic_brand_mapping` (
  `map_id` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `brand_id` smallint(5) unsigned DEFAULT '0' COMMENT '供应商品牌ID',
  `brand_name` varchar(60) NOT NULL DEFAULT '' COMMENT '供应商品牌名',
  `ic_brand_id` smallint(5) unsigned DEFAULT '0' COMMENT 'hqchip设置品牌ID',
  `ic_brand_name` varchar(60) NOT NULL DEFAULT '' COMMENT 'hqchip设定品牌名',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '状态, 1启用，0禁用',
  PRIMARY KEY (`map_id`),
  KEY `brand_id` (`brand_id`),
  KEY `brand_name` (`brand_name`),
  KEY `ic_brand_id` (`ic_brand_id`),
  KEY `brand_map` (`brand_name`,`ic_brand_name`),
  KEY `status` (`status`)
) ENGINE=MyISAM AUTO_INCREMENT=404 DEFAULT CHARSET=utf8;

/*Table structure for table `ic_brand_mapping_log` */

DROP TABLE IF EXISTS `ic_brand_mapping_log`;

CREATE TABLE `ic_brand_mapping_log` (
  `log_id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `map_id` mediumint(8) unsigned NOT NULL DEFAULT '0' COMMENT '映射表ID',
  `goods_id` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '产品ID',
  `goods_name` varchar(120) NOT NULL DEFAULT '' COMMENT '产品型号名称',
  `origin_brand_name` varchar(60) NOT NULL DEFAULT '' COMMENT '原始品牌名称',
  `ic_brand_name` varchar(60) NOT NULL DEFAULT '' COMMENT '映射的IC品牌名称',
  `ic_brand_id` smallint(5) unsigned NOT NULL DEFAULT '0' COMMENT 'IC品牌ID',
  PRIMARY KEY (`log_id`),
  KEY `goods_id` (`goods_id`),
  KEY `goods_name` (`goods_name`)
) ENGINE=MyISAM AUTO_INCREMENT=73308 DEFAULT CHARSET=utf8;

/*Table structure for table `ic_brand_mapping_none` */

DROP TABLE IF EXISTS `ic_brand_mapping_none`;

CREATE TABLE `ic_brand_mapping_none` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `goods_id` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '产品ID',
  `brand_name` varchar(60) NOT NULL DEFAULT '' COMMENT '原始品牌名称',
  PRIMARY KEY (`id`),
  KEY `goods_id` (`goods_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_category` */

DROP TABLE IF EXISTS `ic_category`;

CREATE TABLE `ic_category` (
  `cat_id` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `cat_name` varchar(90) NOT NULL DEFAULT '',
  `keywords` varchar(255) NOT NULL DEFAULT '',
  `cat_desc` varchar(255) NOT NULL DEFAULT '',
  `parent_id` smallint(5) unsigned NOT NULL DEFAULT '0',
  `sort_order` tinyint(1) unsigned NOT NULL DEFAULT '50',
  `template_file` varchar(50) NOT NULL DEFAULT '',
  `measure_unit` varchar(15) NOT NULL DEFAULT '',
  `show_in_nav` tinyint(1) NOT NULL DEFAULT '0',
  `style` varchar(150) NOT NULL,
  `is_show` tinyint(1) unsigned NOT NULL DEFAULT '1',
  `grade` tinyint(4) NOT NULL DEFAULT '0',
  `filter_attr` varchar(255) NOT NULL DEFAULT '0',
  `url` varchar(255) NOT NULL,
  `ext` varchar(100) NOT NULL,
  `goods_count` int(10) unsigned NOT NULL DEFAULT '0',
  `ext_fields` text NOT NULL,
  `recom_attr` varchar(128) NOT NULL DEFAULT '',
  `islast` tinyint(1) unsigned NOT NULL,
  `level` tinyint(1) unsigned NOT NULL DEFAULT '1',
  PRIMARY KEY (`cat_id`),
  KEY `cat_name` (`cat_name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_category_attr` */

DROP TABLE IF EXISTS `ic_category_attr`;

CREATE TABLE `ic_category_attr` (
  `attr_id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `attr_name` varchar(128) NOT NULL DEFAULT '',
  `cat_id` smallint(5) NOT NULL DEFAULT '0',
  `sort_order` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`attr_id`),
  KEY `attr_name` (`attr_name`),
  KEY `attr_cat_id` (`attr_name`,`cat_id`),
  KEY `cat_id` (`cat_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods` */

DROP TABLE IF EXISTS `ic_goods`;

CREATE TABLE `ic_goods` (
  `goods_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `cat_id` smallint(5) unsigned NOT NULL DEFAULT '0',
  `goods_sn` varchar(60) NOT NULL DEFAULT '',
  `goods_name` varchar(120) NOT NULL DEFAULT '',
  `goods_name_style` varchar(60) NOT NULL DEFAULT '+',
  `click_count` int(10) unsigned NOT NULL DEFAULT '0',
  `brand_id` smallint(5) unsigned NOT NULL DEFAULT '0',
  `brand_goods_id` varchar(100) NOT NULL,
  `provider_name` varchar(100) NOT NULL DEFAULT '',
  `origin_provider_name` varchar(100) NOT NULL DEFAULT '' COMMENT '供应商牌名',
  `doc_url` varchar(255) NOT NULL,
  `goods_number` int(11) unsigned NOT NULL DEFAULT '0',
  `goods_weight` decimal(10,3) unsigned NOT NULL DEFAULT '0.000',
  `market_price` decimal(10,2) unsigned NOT NULL DEFAULT '0.00',
  `shop_price` decimal(10,2) unsigned NOT NULL DEFAULT '0.00',
  `promote_price` decimal(10,2) unsigned NOT NULL DEFAULT '0.00',
  `promote_start_date` int(11) unsigned NOT NULL DEFAULT '0',
  `promote_end_date` int(11) unsigned NOT NULL DEFAULT '0',
  `warn_number` tinyint(3) unsigned NOT NULL DEFAULT '1',
  `min_buynum` int(10) unsigned NOT NULL,
  `keywords` varchar(255) NOT NULL DEFAULT '',
  `goods_brief` varchar(255) NOT NULL DEFAULT '',
  `goods_desc` text NOT NULL,
  `goods_thumb` varchar(255) NOT NULL DEFAULT '',
  `goods_img` varchar(255) NOT NULL DEFAULT '',
  `original_img` varchar(255) NOT NULL DEFAULT '',
  `is_real` tinyint(3) unsigned NOT NULL DEFAULT '1',
  `extension_code` varchar(30) NOT NULL DEFAULT '',
  `is_on_sale` tinyint(1) unsigned NOT NULL DEFAULT '1',
  `is_alone_sale` tinyint(1) unsigned NOT NULL DEFAULT '1',
  `is_shipping` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `integral` int(10) unsigned NOT NULL DEFAULT '0',
  `add_time` int(10) unsigned NOT NULL DEFAULT '0',
  `sort_order` smallint(4) unsigned NOT NULL DEFAULT '100',
  `is_delete` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `is_best` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `is_new` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `is_hot` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `is_promote` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `bonus_type_id` tinyint(3) unsigned NOT NULL DEFAULT '0',
  `last_update` int(10) unsigned NOT NULL DEFAULT '0',
  `goods_type` smallint(5) unsigned NOT NULL DEFAULT '1',
  `seller_note` varchar(255) NOT NULL DEFAULT '',
  `give_integral` int(11) NOT NULL DEFAULT '-1',
  `rank_integral` int(11) NOT NULL DEFAULT '-1',
  `suppliers_id` smallint(5) unsigned DEFAULT NULL,
  `is_check` tinyint(1) unsigned DEFAULT NULL,
  `digikey_url` varchar(500) NOT NULL,
  `series` varchar(255) NOT NULL,
  `source_type` tinyint(3) unsigned NOT NULL,
  `sale_count` mediumint(8) unsigned NOT NULL DEFAULT '0',
  `is_rohs` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `s` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `p` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `is_insert` tinyint(1) unsigned DEFAULT '0',
  `warehouse` varchar(255) DEFAULT '-',
  `Encap` varchar(255) DEFAULT '-',
  `Package` varchar(255) DEFAULT '-',
  `MOQ` mediumint(8) NOT NULL DEFAULT '0',
  `SPQ` int(8) NOT NULL DEFAULT '0',
  `HDT` varchar(20) DEFAULT NULL,
  `CDT` varchar(20) DEFAULT NULL,
  `erp_id` int(11) unsigned NOT NULL DEFAULT '0',
  `increment` int(10) DEFAULT '1' COMMENT '产品增量',
  PRIMARY KEY (`goods_id`),
  UNIQUE KEY `goods_sn` (`goods_sn`),
  KEY `cat_id` (`cat_id`),
  KEY `brand_id` (`brand_id`),
  KEY `goods_type` (`goods_type`),
  KEY `goods_name` (`goods_name`),
  KEY `brand_goods_id` (`brand_goods_id`),
  KEY `delete_real_goods_id` (`is_delete`,`is_real`,`goods_id`),
  KEY `all_info` (`is_delete`,`is_real`,`is_alone_sale`),
  KEY `erp_id` (`erp_id`)
) ENGINE=MyISAM AUTO_INCREMENT=1800123907 DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_attr_fields_0` */

DROP TABLE IF EXISTS `ic_goods_attr_fields_0`;

CREATE TABLE `ic_goods_attr_fields_0` (
  `ext_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `extname1` mediumint(8) DEFAULT NULL,
  `goods_id` int(10) unsigned NOT NULL DEFAULT '0',
  `cat_id` smallint(5) DEFAULT NULL,
  `ext_value` varchar(500) DEFAULT NULL,
  `sort_order` smallint(4) unsigned DEFAULT '100',
  `ext_name` varchar(60) DEFAULT NULL,
  PRIMARY KEY (`ext_id`),
  KEY `cat_id` (`cat_id`),
  KEY `goods_id` (`goods_id`),
  KEY `ext_value` (`ext_value`(333))
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_attr_fields_1` */

DROP TABLE IF EXISTS `ic_goods_attr_fields_1`;

CREATE TABLE `ic_goods_attr_fields_1` (
  `ext_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `extname1` mediumint(8) DEFAULT NULL,
  `goods_id` int(10) unsigned NOT NULL DEFAULT '0',
  `cat_id` smallint(5) DEFAULT NULL,
  `ext_value` varchar(500) DEFAULT NULL,
  `sort_order` smallint(4) unsigned DEFAULT '100',
  `ext_name` varchar(60) DEFAULT NULL,
  PRIMARY KEY (`ext_id`),
  KEY `cat_id` (`cat_id`),
  KEY `goods_id` (`goods_id`),
  KEY `ext_value` (`ext_value`(333))
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_attr_fields_2` */

DROP TABLE IF EXISTS `ic_goods_attr_fields_2`;

CREATE TABLE `ic_goods_attr_fields_2` (
  `ext_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `extname1` mediumint(8) DEFAULT NULL,
  `goods_id` int(10) unsigned NOT NULL DEFAULT '0',
  `cat_id` smallint(5) DEFAULT NULL,
  `ext_value` varchar(500) DEFAULT NULL,
  `sort_order` smallint(4) unsigned DEFAULT '100',
  `ext_name` varchar(60) DEFAULT NULL,
  PRIMARY KEY (`ext_id`),
  KEY `cat_id` (`cat_id`),
  KEY `goods_id` (`goods_id`),
  KEY `ext_value` (`ext_value`(333))
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_attr_fields_3` */

DROP TABLE IF EXISTS `ic_goods_attr_fields_3`;

CREATE TABLE `ic_goods_attr_fields_3` (
  `ext_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `extname1` mediumint(8) DEFAULT NULL,
  `goods_id` int(10) unsigned NOT NULL DEFAULT '0',
  `cat_id` smallint(5) DEFAULT NULL,
  `ext_value` varchar(500) DEFAULT NULL,
  `sort_order` smallint(4) unsigned DEFAULT '100',
  `ext_name` varchar(60) DEFAULT NULL,
  PRIMARY KEY (`ext_id`),
  KEY `cat_id` (`cat_id`),
  KEY `goods_id` (`goods_id`),
  KEY `ext_value` (`ext_value`(333))
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_attr_fields_4` */

DROP TABLE IF EXISTS `ic_goods_attr_fields_4`;

CREATE TABLE `ic_goods_attr_fields_4` (
  `ext_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `extname1` mediumint(8) DEFAULT NULL,
  `goods_id` int(10) unsigned NOT NULL DEFAULT '0',
  `cat_id` smallint(5) DEFAULT NULL,
  `ext_value` varchar(500) DEFAULT NULL,
  `sort_order` smallint(4) unsigned DEFAULT '100',
  `ext_name` varchar(60) DEFAULT NULL,
  PRIMARY KEY (`ext_id`),
  KEY `cat_id` (`cat_id`),
  KEY `goods_id` (`goods_id`),
  KEY `ext_value` (`ext_value`(333))
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_attr_fields_5` */

DROP TABLE IF EXISTS `ic_goods_attr_fields_5`;

CREATE TABLE `ic_goods_attr_fields_5` (
  `ext_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `extname1` mediumint(8) DEFAULT NULL,
  `goods_id` int(10) unsigned NOT NULL DEFAULT '0',
  `cat_id` smallint(5) DEFAULT NULL,
  `ext_value` varchar(500) DEFAULT NULL,
  `sort_order` smallint(4) unsigned DEFAULT '100',
  `ext_name` varchar(60) DEFAULT NULL,
  PRIMARY KEY (`ext_id`),
  KEY `cat_id` (`cat_id`),
  KEY `goods_id` (`goods_id`),
  KEY `ext_value` (`ext_value`(333))
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_attr_fields_6` */

DROP TABLE IF EXISTS `ic_goods_attr_fields_6`;

CREATE TABLE `ic_goods_attr_fields_6` (
  `ext_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `extname1` mediumint(8) DEFAULT NULL,
  `goods_id` int(10) unsigned NOT NULL DEFAULT '0',
  `cat_id` smallint(5) DEFAULT NULL,
  `ext_value` varchar(500) DEFAULT NULL,
  `sort_order` smallint(4) unsigned DEFAULT '100',
  `ext_name` varchar(60) DEFAULT NULL,
  PRIMARY KEY (`ext_id`),
  KEY `cat_id` (`cat_id`),
  KEY `goods_id` (`goods_id`),
  KEY `ext_value` (`ext_value`(333))
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_attr_fields_7` */

DROP TABLE IF EXISTS `ic_goods_attr_fields_7`;

CREATE TABLE `ic_goods_attr_fields_7` (
  `ext_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `extname1` mediumint(8) DEFAULT NULL,
  `goods_id` int(10) unsigned NOT NULL DEFAULT '0',
  `cat_id` smallint(5) DEFAULT NULL,
  `ext_value` varchar(500) DEFAULT NULL,
  `sort_order` smallint(4) unsigned DEFAULT '100',
  `ext_name` varchar(60) DEFAULT NULL,
  PRIMARY KEY (`ext_id`),
  KEY `cat_id` (`cat_id`),
  KEY `goods_id` (`goods_id`),
  KEY `ext_value` (`ext_value`(333))
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_attr_fields_8` */

DROP TABLE IF EXISTS `ic_goods_attr_fields_8`;

CREATE TABLE `ic_goods_attr_fields_8` (
  `ext_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `extname1` mediumint(8) DEFAULT NULL,
  `goods_id` int(10) unsigned NOT NULL DEFAULT '0',
  `cat_id` smallint(5) DEFAULT NULL,
  `ext_value` varchar(500) DEFAULT NULL,
  `sort_order` smallint(4) unsigned DEFAULT '100',
  `ext_name` varchar(60) DEFAULT NULL,
  PRIMARY KEY (`ext_id`),
  KEY `cat_id` (`cat_id`),
  KEY `goods_id` (`goods_id`),
  KEY `ext_value` (`ext_value`(333))
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_attr_fields_9` */

DROP TABLE IF EXISTS `ic_goods_attr_fields_9`;

CREATE TABLE `ic_goods_attr_fields_9` (
  `ext_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `extname1` mediumint(8) DEFAULT NULL,
  `goods_id` int(10) unsigned NOT NULL DEFAULT '0',
  `cat_id` smallint(5) DEFAULT NULL,
  `ext_value` varchar(500) DEFAULT NULL,
  `sort_order` smallint(4) unsigned DEFAULT '100',
  `ext_name` varchar(60) DEFAULT NULL,
  PRIMARY KEY (`ext_id`),
  KEY `cat_id` (`cat_id`),
  KEY `goods_id` (`goods_id`),
  KEY `ext_value` (`ext_value`(333))
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_brand` */

DROP TABLE IF EXISTS `ic_goods_brand`;

CREATE TABLE `ic_goods_brand` (
  `goods_id` int(10) unsigned NOT NULL,
  `brand_id` smallint(5) unsigned DEFAULT '0' COMMENT '供应商品牌ID',
  PRIMARY KEY (`goods_id`),
  KEY `brand_id` (`brand_id`),
  KEY `goods_brand` (`goods_id`,`brand_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_price_0` */

DROP TABLE IF EXISTS `ic_goods_price_0`;

CREATE TABLE `ic_goods_price_0` (
  `goods_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `price` text NOT NULL,
  PRIMARY KEY (`goods_id`)
) ENGINE=MyISAM AUTO_INCREMENT=1800123901 DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_price_1` */

DROP TABLE IF EXISTS `ic_goods_price_1`;

CREATE TABLE `ic_goods_price_1` (
  `goods_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `price` text NOT NULL,
  PRIMARY KEY (`goods_id`)
) ENGINE=MyISAM AUTO_INCREMENT=1800123902 DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_price_2` */

DROP TABLE IF EXISTS `ic_goods_price_2`;

CREATE TABLE `ic_goods_price_2` (
  `goods_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `price` text NOT NULL,
  PRIMARY KEY (`goods_id`)
) ENGINE=MyISAM AUTO_INCREMENT=1800123903 DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_price_3` */

DROP TABLE IF EXISTS `ic_goods_price_3`;

CREATE TABLE `ic_goods_price_3` (
  `goods_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `price` text NOT NULL,
  PRIMARY KEY (`goods_id`)
) ENGINE=MyISAM AUTO_INCREMENT=1800123904 DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_price_4` */

DROP TABLE IF EXISTS `ic_goods_price_4`;

CREATE TABLE `ic_goods_price_4` (
  `goods_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `price` text NOT NULL,
  PRIMARY KEY (`goods_id`)
) ENGINE=MyISAM AUTO_INCREMENT=1800123905 DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_price_5` */

DROP TABLE IF EXISTS `ic_goods_price_5`;

CREATE TABLE `ic_goods_price_5` (
  `goods_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `price` text NOT NULL,
  PRIMARY KEY (`goods_id`)
) ENGINE=MyISAM AUTO_INCREMENT=1800123906 DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_price_6` */

DROP TABLE IF EXISTS `ic_goods_price_6`;

CREATE TABLE `ic_goods_price_6` (
  `goods_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `price` text NOT NULL,
  PRIMARY KEY (`goods_id`)
) ENGINE=MyISAM AUTO_INCREMENT=1800123907 DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_price_7` */

DROP TABLE IF EXISTS `ic_goods_price_7`;

CREATE TABLE `ic_goods_price_7` (
  `goods_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `price` text NOT NULL,
  PRIMARY KEY (`goods_id`)
) ENGINE=MyISAM AUTO_INCREMENT=1800123898 DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_price_8` */

DROP TABLE IF EXISTS `ic_goods_price_8`;

CREATE TABLE `ic_goods_price_8` (
  `goods_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `price` text NOT NULL,
  PRIMARY KEY (`goods_id`)
) ENGINE=MyISAM AUTO_INCREMENT=1800123899 DEFAULT CHARSET=utf8;

/*Table structure for table `ic_goods_price_9` */

DROP TABLE IF EXISTS `ic_goods_price_9`;

CREATE TABLE `ic_goods_price_9` (
  `goods_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `price` text NOT NULL,
  PRIMARY KEY (`goods_id`)
) ENGINE=MyISAM AUTO_INCREMENT=1800123900 DEFAULT CHARSET=utf8;

/*Table structure for table `ic_pagelist` */

DROP TABLE IF EXISTS `ic_pagelist`;

CREATE TABLE `ic_pagelist` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `cat_id` int(10) unsigned NOT NULL COMMENT '分类id',
  `url` varchar(300) NOT NULL,
  `status` tinyint(1) unsigned NOT NULL DEFAULT '0' COMMENT '是否抓取成功',
  PRIMARY KEY (`id`),
  UNIQUE KEY `url` (`url`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*Table structure for table `ic_url` */

DROP TABLE IF EXISTS `ic_url`;

CREATE TABLE `ic_url` (
  `goods_id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '芯片id',
  `cat_id` int(10) unsigned NOT NULL COMMENT '分类id',
  `id` int(10) unsigned NOT NULL COMMENT '目标网站芯片对应的id',
  `url` varchar(500) NOT NULL COMMENT '目标网站芯片地址',
  PRIMARY KEY (`goods_id`),
  KEY `cat_id` (`cat_id`),
  KEY `id` (`id`),
  KEY `url` (`url`(333))
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
