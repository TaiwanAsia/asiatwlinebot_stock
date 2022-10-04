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
-- Table structure for table `cmp`
--

DROP TABLE IF EXISTS `cmp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cmp` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cmp_name` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cmp_ancs`
--

DROP TABLE IF EXISTS `cmp_ancs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cmp_ancs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cmp_id` int(5) DEFAULT NULL,
  `cmp_name` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ancs_title` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ancs_content` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ancs_date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `company_l_o`
--

DROP TABLE IF EXISTS `company_l_o`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `company_l_o` (
  `id` int(11) DEFAULT NULL,
  `出表日期` int(11) DEFAULT NULL,
  `公司代號` int(11) DEFAULT NULL,
  `公司名稱` text COLLATE utf8mb4_unicode_ci,
  `公司簡稱` text COLLATE utf8mb4_unicode_ci,
  `外國企業註冊地國` text COLLATE utf8mb4_unicode_ci,
  `產業別` int(11) DEFAULT NULL,
  `住址` text COLLATE utf8mb4_unicode_ci,
  `營利事業統一編號` int(11) DEFAULT NULL,
  `董事長` text COLLATE utf8mb4_unicode_ci,
  `總經理` text COLLATE utf8mb4_unicode_ci,
  `發言人` text COLLATE utf8mb4_unicode_ci,
  `發言人職稱` text COLLATE utf8mb4_unicode_ci,
  `代理發言人` text COLLATE utf8mb4_unicode_ci,
  `總機電話` text COLLATE utf8mb4_unicode_ci,
  `成立日期` int(11) DEFAULT NULL,
  `上市日期` int(11) DEFAULT NULL,
  `普通股每股面額` text COLLATE utf8mb4_unicode_ci,
  `實收資本額` bigint(20) DEFAULT NULL,
  `私募股數` int(11) DEFAULT NULL,
  `特別股` int(11) DEFAULT NULL,
  `編制財務報表類型` int(11) DEFAULT NULL,
  `股票過戶機構` text COLLATE utf8mb4_unicode_ci,
  `過戶電話` text COLLATE utf8mb4_unicode_ci,
  `過戶地址` text COLLATE utf8mb4_unicode_ci,
  `簽證會計師事務所` text COLLATE utf8mb4_unicode_ci,
  `簽證會計師1` text COLLATE utf8mb4_unicode_ci,
  `簽證會計師2` text COLLATE utf8mb4_unicode_ci,
  `英文簡稱` text COLLATE utf8mb4_unicode_ci,
  `英文通訊地址` text COLLATE utf8mb4_unicode_ci,
  `傳真機號碼` text COLLATE utf8mb4_unicode_ci,
  `電子郵件信箱` text COLLATE utf8mb4_unicode_ci,
  `網址` text COLLATE utf8mb4_unicode_ci
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
) ENGINE=InnoDB AUTO_INCREMENT=201 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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

-- Dump completed on 2022-10-04 12:50:56
