-- MySQL dump 10.13  Distrib 5.5.50, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: curious
-- ------------------------------------------------------
-- Server version	5.5.50-0ubuntu0.14.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissi_permission_id_84c5c92e_fk_auth_permission_id` (`permission_id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_group_permissi_permission_id_84c5c92e_fk_auth_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permissi_content_type_id_2f476e4b_fk_django_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=85 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_perm_permission_id_1fbb5f2c_fk_auth_permission_id` (`permission_id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `auth_user_user_perm_permission_id_1fbb5f2c_fk_auth_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `curiousWorkbench_certification`
--

DROP TABLE IF EXISTS `curiousWorkbench_certification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `curiousWorkbench_certification` (
  `ID` int(11) NOT NULL DEFAULT '0',
  `Title` varchar(500) NOT NULL,
  `Description` varchar(500) NOT NULL,
  `Image` varchar(500) NOT NULL,
  `Module_ID` int(11) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `curiousWorkbench_content`
--

DROP TABLE IF EXISTS `curiousWorkbench_content`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `curiousWorkbench_content` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `Title` varchar(500) DEFAULT NULL,
  `OrderNumber` varchar(500) DEFAULT NULL,
  `Content` longtext,
  `Image` varchar(500) DEFAULT NULL,
  `ContentType` varchar(1) DEFAULT NULL,
  `OptionA` varchar(500) DEFAULT NULL,
  `OptionB` varchar(500) DEFAULT NULL,
  `OptionC` varchar(500) DEFAULT NULL,
  `WaitForUser` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `curiousWorkbench_contentlibrary`
--

DROP TABLE IF EXISTS `curiousWorkbench_contentlibrary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `curiousWorkbench_contentlibrary` (
  `ID` int(11) NOT NULL,
  `Title` varchar(500) NOT NULL,
  `Subtitle` varchar(500) NOT NULL,
  `ImageURL` varchar(500) NOT NULL,
  `LinkURL` varchar(500) NOT NULL,
  `Embed_ID` varchar(500) NOT NULL,
  `Type` varchar(500) NOT NULL,
  `Skill` varchar(500) NOT NULL,
  `Questions` varchar(500) NOT NULL,
  `AnswerOptions` varchar(500) CHARACTER SET utf8 DEFAULT NULL,
  `RightAnswer` varchar(500) NOT NULL,
  `Content_Order` int(11) NOT NULL,
  `Module_ID` int(11) DEFAULT NULL,
  `Right_Ans_Response` varchar(500) CHARACTER SET utf8 DEFAULT NULL,
  `Text` varchar(500) CHARACTER SET utf8 DEFAULT NULL,
  `Wrong_Ans_Response` varchar(500) CHARACTER SET utf8 DEFAULT NULL,
  `Message_Type` varchar(500) DEFAULT NULL,
  `Rating` int(11) NOT NULL DEFAULT '5',
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `curiousWorkbench_messagelibrary`
--

DROP TABLE IF EXISTS `curiousWorkbench_messagelibrary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `curiousWorkbench_messagelibrary` (
  `Action` varchar(100) NOT NULL,
  `MsgOrder` varchar(500) NOT NULL,
  `MessageType` varchar(500) NOT NULL,
  `MessageText` varchar(500) NOT NULL,
  `MessageImage` varchar(500) NOT NULL,
  `MessageVideo` varchar(500) NOT NULL,
  `MessageButtons` varchar(500) NOT NULL,
  `MessageQuickReplies` varchar(500) NOT NULL,
  `ID` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `curiousWorkbench_modelmap`
--

DROP TABLE IF EXISTS `curiousWorkbench_modelmap`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `curiousWorkbench_modelmap` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(200) NOT NULL,
  `CreatedBy` varchar(200) NOT NULL,
  `Created` datetime NOT NULL,
  `Description` longtext NOT NULL,
  `RawXML` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `curiousWorkbench_module`
--

DROP TABLE IF EXISTS `curiousWorkbench_module`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `curiousWorkbench_module` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Title` varchar(500) NOT NULL,
  `Description` varchar(500) NOT NULL,
  `Goal` varchar(500) NOT NULL,
  `Author` varchar(500) NOT NULL,
  `AuthorAffiliation` varchar(500) NOT NULL,
  `AuthorURL` varchar(500) NOT NULL,
  `Days` int(11) DEFAULT NULL,
  `UnitsPerDay` int(11) DEFAULT NULL,
  `Units` int(11) DEFAULT NULL,
  `CertificateURL` varchar(500) NOT NULL,
  `CertificateTest` tinyint(1) NOT NULL,
  `Live` tinyint(1) NOT NULL,
  `MinPoints` int(11) DEFAULT NULL,
  `SKILL_CODE` varchar(500) DEFAULT NULL,
  `UserID` varchar(500) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `curiousWorkbench_moduletags`
--

DROP TABLE IF EXISTS `curiousWorkbench_moduletags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `curiousWorkbench_moduletags` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `curiousWorkbench_progress`
--

DROP TABLE IF EXISTS `curiousWorkbench_progress`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `curiousWorkbench_progress` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userID` varchar(500) NOT NULL,
  `contentID` varchar(500) NOT NULL,
  `Status` varchar(500) NOT NULL,
  `StartDate` varchar(500) NOT NULL,
  `LastActivityDate` varchar(500) NOT NULL,
  `LastActivityUserID` varchar(500) NOT NULL,
  `ExpectedEndDate` varchar(500) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `curiousWorkbench_project`
--

DROP TABLE IF EXISTS `curiousWorkbench_project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `curiousWorkbench_project` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(200) NOT NULL,
  `CreatedBy` varchar(200) NOT NULL,
  `LastUpdated` datetime NOT NULL,
  `Description` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `curiousWorkbench_roledemandinfo`
--

DROP TABLE IF EXISTS `curiousWorkbench_roledemandinfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `curiousWorkbench_roledemandinfo` (
  `Role` varchar(500) DEFAULT NULL,
  `Location` varchar(500) DEFAULT NULL,
  `CompanyClass` varchar(500) DEFAULT NULL,
  `Skill` varchar(500) DEFAULT NULL,
  `SKILL_CODE` varchar(500) DEFAULT NULL,
  `Percentage` varchar(500) DEFAULT NULL,
  `Enabled` varchar(500) DEFAULT NULL,
  `Demand_Count` int(11) NOT NULL,
  `World_Count` int(11) NOT NULL,
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=575 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `curiousWorkbench_skill`
--

DROP TABLE IF EXISTS `curiousWorkbench_skill`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `curiousWorkbench_skill` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `skillCode` varchar(500) NOT NULL,
  `skillTitle` varchar(500) NOT NULL,
  `skillDescription` varchar(500) NOT NULL,
  `skillFlag` varchar(500) NOT NULL,
  `skillImage` varchar(500) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `curiousWorkbench_statemachine`
--

DROP TABLE IF EXISTS `curiousWorkbench_statemachine`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `curiousWorkbench_statemachine` (
  `Event_Code` varchar(100) NOT NULL,
  `SM_ID` int(11) NOT NULL,
  `ExpectedState` varchar(500) NOT NULL,
  `State` varchar(500) NOT NULL,
  `Expiry` varchar(500) NOT NULL,
  `Action` varchar(500) NOT NULL,
  `NextEvent` varchar(500) NOT NULL,
  `CallFunction` varchar(500) NOT NULL,
  `ParentSystem` varchar(500) NOT NULL,
  PRIMARY KEY (`SM_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `curiousWorkbench_storeinformation`
--

DROP TABLE IF EXISTS `curiousWorkbench_storeinformation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `curiousWorkbench_storeinformation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `StoreName` varchar(500) NOT NULL,
  `StoreInfo` varchar(500) DEFAULT NULL,
  `StoreType` varchar(500) DEFAULT NULL,
  `StoreHours` varchar(500) DEFAULT NULL,
  `StoreLocation` varchar(500) DEFAULT NULL,
  `StoreWalkins` varchar(500) DEFAULT NULL,
  `StorePhone` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `curiousWorkbench_storeproductcategories`
--

DROP TABLE IF EXISTS `curiousWorkbench_storeproductcategories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `curiousWorkbench_storeproductcategories` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `CategoryName` varchar(500) NOT NULL,
  `CategoryDesc` varchar(500) DEFAULT NULL,
  `CategoryOrder` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `curiousWorkbench_storeproduts`
--

DROP TABLE IF EXISTS `curiousWorkbench_storeproduts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `curiousWorkbench_storeproduts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ProductName` varchar(500) NOT NULL,
  `ProductOrder` varchar(500) DEFAULT NULL,
  `ProductDesc` varchar(500) DEFAULT NULL,
  `ProductPrice` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `curiousWorkbench_tag`
--

DROP TABLE IF EXISTS `curiousWorkbench_tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `curiousWorkbench_tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `Tag` varchar(500) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `curiousWorkbench_test`
--

DROP TABLE IF EXISTS `curiousWorkbench_test`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `curiousWorkbench_test` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `Question` varchar(500) DEFAULT NULL,
  `AnswerType` varchar(500) DEFAULT NULL,
  `AnswerOptionA` varchar(500) DEFAULT NULL,
  `AnswerOptionB` varchar(500) DEFAULT NULL,
  `AnswerOptionC` varchar(500) DEFAULT NULL,
  `CorrectAnswer` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `curiousWorkbench_usercertification`
--

DROP TABLE IF EXISTS `curiousWorkbench_usercertification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `curiousWorkbench_usercertification` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userID` varchar(500) NOT NULL,
  `certificationID` varchar(500) NOT NULL,
  `date` datetime NOT NULL,
  `Module_ID` int(11) NOT NULL,
  `Title` varchar(500) DEFAULT NULL,
  `Author` varchar(500) DEFAULT NULL,
  `AuthorURL` varchar(500) DEFAULT NULL,
  `SKILL_CODE` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `curiousWorkbench_useridentity`
--

DROP TABLE IF EXISTS `curiousWorkbench_useridentity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `curiousWorkbench_useridentity` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `slackUserID` varchar(500) NOT NULL,
  `nAccessToken` varchar(500) NOT NULL,
  `first_name` varchar(500) NOT NULL,
  `last_name` varchar(500) NOT NULL,
  `age_range_min` varchar(500) NOT NULL,
  `gender` varchar(500) NOT NULL,
  `location` varchar(500) NOT NULL,
  `locale` varchar(500) NOT NULL,
  `timezone` varchar(500) NOT NULL,
  `birthday` varchar(500) NOT NULL,
  `hometown` varchar(500) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `curiousWorkbench_usermoduleprogress`
--

DROP TABLE IF EXISTS `curiousWorkbench_usermoduleprogress`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `curiousWorkbench_usermoduleprogress` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ModuleID` int(11) NOT NULL,
  `UserID` varchar(500) NOT NULL,
  `CurrentPosition` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `curiousWorkbench_userskillstatus`
--

DROP TABLE IF EXISTS `curiousWorkbench_userskillstatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `curiousWorkbench_userskillstatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userID` varchar(500) NOT NULL,
  `skill` varchar(500) NOT NULL,
  `points` varchar(500) NOT NULL,
  `LastActivityDate` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `curiousWorkbench_userstate`
--

DROP TABLE IF EXISTS `curiousWorkbench_userstate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `curiousWorkbench_userstate` (
  `UserID` varchar(100) NOT NULL,
  `UserName` varchar(500) NOT NULL,
  `UserEmail` varchar(500) NOT NULL,
  `UserGender` varchar(500) NOT NULL,
  `UserCurrentState` varchar(500) NOT NULL,
  `UserLastAccessedTime` datetime NOT NULL,
  `Location_PIN` varchar(500) NOT NULL,
  `UserCompany` varchar(500) NOT NULL,
  `UserRole` varchar(500) NOT NULL,
  `Current_Module_ID` int(11) DEFAULT NULL,
  `UserStateDict` varchar(1000) DEFAULT NULL,
  `Notify_Subscription` varchar(500) NOT NULL DEFAULT 'FALSE',
  `Notify_Time` varchar(500) NOT NULL DEFAULT 'MOR',
  `UserTimeZone` float NOT NULL DEFAULT '-8',
  PRIMARY KEY (`UserID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin__content_type_id_c4bce8eb_fk_django_content_type_id` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin__content_type_id_c4bce8eb_fk_django_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_de54fa62` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-01-02 17:38:27
