-- MySQL dump 10.13  Distrib 8.0.33, for Win64 (x86_64)
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
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `business_code`
--

DROP TABLE IF EXISTS `business_code`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `business_code` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name_ch` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `name_en` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `definition` text COLLATE utf8mb4_unicode_ci,
  `upstream` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `downstream` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=676 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
  PRIMARY KEY (`id`),
  KEY `business_code` (`business_code`(50)),
  KEY `ix_company_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=607823 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `company_news`
--

DROP TABLE IF EXISTS `company_news`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `company_news` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `company_id` int(11) DEFAULT NULL,
  `company_business_entity` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `keyword` varchar(15) COLLATE utf8_bin NOT NULL DEFAULT '',
  `news_title` varchar(400) COLLATE utf8_bin DEFAULT NULL,
  `news_content` text COLLATE utf8_bin,
  `news_url` varchar(225) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `news_date` varchar(45) COLLATE utf8_bin DEFAULT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `keyword` (`keyword`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dataset_day`
--

DROP TABLE IF EXISTS `dataset_day`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dataset_day` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `website_id` int(5) NOT NULL,
  `table_name` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `order` int(3) DEFAULT NULL,
  `company_name` text COLLATE utf8mb4_unicode_ci,
  `buy_amount` text COLLATE utf8mb4_unicode_ci,
  `buy_high` text COLLATE utf8mb4_unicode_ci,
  `buy_low` text COLLATE utf8mb4_unicode_ci,
  `buy_average` text COLLATE utf8mb4_unicode_ci,
  `buy_average_yesterday` text COLLATE utf8mb4_unicode_ci,
  `buy_change_percent` text COLLATE utf8mb4_unicode_ci,
  `sell_amount` text COLLATE utf8mb4_unicode_ci,
  `sell_high` text COLLATE utf8mb4_unicode_ci,
  `sell_low` text COLLATE utf8mb4_unicode_ci,
  `sell_average` text COLLATE utf8mb4_unicode_ci,
  `sell_average_yesterday` text COLLATE utf8mb4_unicode_ci,
  `sell_change_percent` text COLLATE utf8mb4_unicode_ci,
  `date` date NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=101 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `group`
--

DROP TABLE IF EXISTS `group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_ids` varchar(225) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `text_reply` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'on',
  `image_reply` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'on',
  `file_reply` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'on',
  `last_message_time` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `log`
--

DROP TABLE IF EXISTS `log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `chatroom` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `message_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `message_content` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_member` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'no',
  `is_admin` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'no',
  `text_reply` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'on',
  `image_reply` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'on',
  `file_reply` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'on',
  `join_member_time` datetime DEFAULT NULL,
  `last_message_time` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
  `company_ids` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-05-26 23:12:17
