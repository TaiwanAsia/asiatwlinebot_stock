-- MySQL dump 10.13  Distrib 8.0.25, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: linebot_stock
-- ------------------------------------------------------
-- Server version	5.7.24

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `business_code`
--

DROP TABLE IF EXISTS `business_code`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `business_code` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '營業項目代碼',
  `name_ch` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '營業項目',
  `name_en` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '英文營業項目',
  `definition` text COLLATE utf8mb4_unicode_ci COMMENT '定義內容',
  `upstream` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `downstream` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=676 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='營業項目代碼，而非行業代碼。';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `company`
--

DROP TABLE IF EXISTS `company`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `company` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uniid` varchar(10) COLLATE utf8mb4_bin NOT NULL,
  `top_uniid` varchar(10) COLLATE utf8mb4_bin DEFAULT NULL,
  `business_entity` varchar(225) COLLATE utf8mb4_bin NOT NULL,
  `capital` varchar(30) COLLATE utf8mb4_bin NOT NULL DEFAULT '0',
  `establishment_date` varchar(30) COLLATE utf8mb4_bin NOT NULL,
  `company_type` varchar(30) COLLATE utf8mb4_bin NOT NULL,
  `business_code` text COLLATE utf8mb4_bin,
  `industrial_classification` varchar(30) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '行業代碼',
  `industrial_name` varchar(45) COLLATE utf8mb4_bin DEFAULT NULL,
  `industrial_classification_1` varchar(30) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '行業代碼',
  `industrial_name_1` varchar(45) COLLATE utf8mb4_bin DEFAULT NULL,
  `industrial_classification_2` varchar(30) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '行業代碼',
  `industrial_name_2` varchar(45) COLLATE utf8mb4_bin DEFAULT NULL,
  `industrial_classification_3` varchar(30) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '行業代碼',
  `industrial_name_3` varchar(45) COLLATE utf8mb4_bin DEFAULT NULL,
  `companycol` varchar(45) COLLATE utf8mb4_bin DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniid_UNIQUE` (`uniid`),
  KEY `business_code` (`business_code`(50))
) ENGINE=InnoDB AUTO_INCREMENT=705676 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin COMMENT='industrial_classification是行業代碼，而非營業項目代碼(business_code)。';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `company_news`
--

DROP TABLE IF EXISTS `company_news`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `company_news` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `company_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `company_business_entity` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `keyword` varchar(15) COLLATE utf8_bin NOT NULL DEFAULT '',
  `news_title` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `news_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `news_url` varchar(225) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `news_date` varchar(45) COLLATE utf8_bin DEFAULT NULL,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `keyword` (`keyword`)
) ENGINE=InnoDB AUTO_INCREMENT=225 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dataset_day`
--

DROP TABLE IF EXISTS `dataset_day`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dataset_day` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `website_id` int(5) NOT NULL COMMENT '哪個網站',
  `table_name` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '哪個排行榜',
  `order` int(3) DEFAULT NULL,
  `company_name` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `buy_amount` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `buy_high` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `buy_low` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `buy_average` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `buy_average_yesterday` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `buy_change_percent` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sell_amount` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sell_high` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sell_low` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sell_average` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sell_average_yesterday` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sell_change_percent` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date` date DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=101 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `industry`
--

DROP TABLE IF EXISTS `industry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `industry` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `upstream_1` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `upstream_2` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `downstream_1` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `downstream_2` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1602 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `log`
--

DROP TABLE IF EXISTS `log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  `message_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `message_content` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用戶使用紀錄';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_member` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'no',
  `is_admin` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'no',
  `text_reply` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'on' COMMENT '文字自動回覆開關',
  `image_reply` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'on' COMMENT '圖片自動回覆開關',
  `file_reply` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'on' COMMENT '文件自動回覆開關',
  `join_member_time` datetime DEFAULT NULL COMMENT '加入會員時間',
  `last_message_time` datetime DEFAULT NULL COMMENT '最後發送訊息時間',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id_UNIQUE` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='所有用戶';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_favorite_company`
--

DROP TABLE IF EXISTS `user_favorite_company`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_favorite_company` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userid` varchar(225) COLLATE utf8mb4_unicode_ci NOT NULL,
  `company_ids` text COLLATE utf8mb4_unicode_ci COMMENT '使用者自選股，股票代號',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `userid_UNIQUE` (`userid`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='使用者的自選股';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `website`
--

DROP TABLE IF EXISTS `website`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `website` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  `domain` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `target_url` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'work',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-01-31 16:04:32
