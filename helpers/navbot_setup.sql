CREATE TABLE `shuttle` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `datetime` datetime NOT NULL,
  `status` varchar(45) DEFAULT 'ok',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `datetime_UNIQUE` (`datetime`)
) ENGINE=InnoDB AUTO_INCREMENT=920 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `people` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `shuttle_id` int(10) unsigned NOT NULL,
  `user` varchar(45) NOT NULL,
  `nb` int(11) NOT NULL DEFAULT 0,
  `user_contact` varchar(45) DEFAULT NULL,
  `user_id` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `fk_shuttle_idx` (`shuttle_id`),
  CONSTRAINT `fk_shuttle` FOREIGN KEY (`shuttle_id`) REFERENCES `shuttle` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1006 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `channel_user` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `telegram_id` varchar(45) NOT NULL,
  `spam` int(11) DEFAULT 0,
  `user_contact` varchar(45) DEFAULT 'None',
  PRIMARY KEY (`telegram_id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `telegram_id_UNIQUE` (`telegram_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1115 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

 CREATE TABLE `msg_ids` (
  `id` int(11) NOT NULL,
  `ids_values` longtext NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


--
-- Dumping routines for database 'navbot'
--
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `add_shuttle` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
DELIMITER ;;
CREATE DEFINER=`navbot_bot`@`localhost` PROCEDURE `add_shuttle`(timest DATETIME)
BEGIN
INSERT INTO shuttle (`datetime`) VALUES (timest) ON DUPLICATE KEY UPDATE `status`='ok';
COMMIT;
SELECT "OK" AS rstatus;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `book_shuttle` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
DELIMITER ;;
CREATE DEFINER=`navbot_bot`@`localhost` PROCEDURE `book_shuttle`(IN timest DATETIME,IN  u_name VARCHAR(45) ,IN  u_number INT, IN user_id VARCHAR(45))
BEGIN

START TRANSACTION;
INSERT INTO people ( shuttle_id, `user`,nb,`user_id`) 
(SELECT s.id , u_name, u_number, user_id FROM shuttle s  WHERE s.`datetime` = timest);

SELECT @free_seats:=(8-SUM(people.nb)) FROM shuttle INNER JOIN people ON shuttle.id=people.shuttle_id WHERE `datetime`=timest;
SELECT @user_r:=SUM(people.nb) FROM shuttle INNER JOIN people ON shuttle.id = people.shuttle_id  WHERE shuttle.`datetime`=timest AND people.`user`= u_name GROUP BY people.`user`;
   SET @rcode:=-1;
   SET @freeseats=@free_seats;
if isnull(@free_seats) THEN
  
  ROLLBACK;
   SET @freeseats:=NULL;
   SET @msg:="erreur: Cette navette n'existe pas.";
elseif @free_seats <0 THEN
  
  ROLLBACK;
   SET @freeseats:=CAST(@free_seats+u_number AS SIGNED);
   SET @msg:=CONCAT("erreur: Nombre de places disponibles: ",@freeseats);
elseif @user_r <0  THEN 
   SET @msg:=CONCAT("erreur: Pas autant de places réservées à ton nom. Seulement ",CAST(-u_number+@user_r AS SIGNED)," places peuvent être annulées.");
  ROLLBACK;
else
  
  commit;
   SET @rcode:=0;
   SET @freeseats:=@free_seats;
   SET @msg:="ok";
  end if;
  DROP TEMPORARY TABLE IF EXISTS book_shuttle_table;
  CREATE TEMPORARY TABLE book_shuttle_table(rcode INT, freeseats INT, msg VARCHAR(128));
  INSERT INTO  book_shuttle_table (rcode, freeseats,msg) VALUES (@rcode, @freeseats, @msg);
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_day_shuttles` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
DELIMITER ;;
CREATE DEFINER=`navbot_bot`@`localhost` PROCEDURE `get_day_shuttles`(v_date DATE)
BEGIN
SELECT t.`datetime`,t.`status`, CONCAT(CAST(8-IFNULL(SUM(t.nb),0) AS CHAR),"pl")  AS seats FROM (SELECT shuttle.`datetime` as `datetime`, shuttle.`status` as `status`, people.nb as nb FROM shuttle LEFT JOIN people ON  shuttle.id=people.shuttle_id  WHERE DATE(shuttle.`datetime`)=DATE(v_date)) AS t GROUP BY t.`datetime`;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_enrolled` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
DELIMITER ;;
CREATE DEFINER=`navbot_bot`@`localhost` PROCEDURE `get_enrolled`(timst DATETIME)
BEGIN
SELECT people.user, people.user_contact,people.user_id, CAST(SUM(people.nb) AS CHAR) AS nbtot  FROM shuttle INNER JOIN people ON shuttle.id = people.shuttle_id WHERE `datetime`=timst GROUP BY(people.user)  HAVING  SUM(people.nb)>0 ORDER BY nbtot DESC;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_freeseats_number` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
DELIMITER ;;
CREATE DEFINER=`navbot_bot`@`localhost` PROCEDURE `get_freeseats_number`(timest DATETIME)
BEGIN
SELECT CAST(8-SUM(people.nb) AS CHAR) AS free_seats FROM people INNER JOIN shuttle ON people.shuttle_id = shuttle.id WHERE `datetime`=timest;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_spam_ids` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
DELIMITER ;;
CREATE DEFINER=`navbot_bot`@`localhost` PROCEDURE `get_spam_ids`()
BEGIN
SELECT telegram_id FROM channel_user WHERE spam=1;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_today_shuttle` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
DELIMITER ;;
CREATE DEFINER=`navbot_bot`@`localhost` PROCEDURE `get_today_shuttle`()
BEGIN
SELECT `datetime`, `status` FROM shuttle WHERE `datetime`> NOW() AND `datetime` < NOW() + INTERVAL(24-HOUR(NOW())) HOUR;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_today_shuttles` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
DELIMITER ;;
CREATE DEFINER=`navbot_bot`@`localhost` PROCEDURE `get_today_shuttles`()
BEGIN
SELECT t.`datetime`,t.`status`, CONCAT(CAST(8-IFNULL(SUM(t.nb),0) AS CHAR),"pl")  AS seats FROM (SELECT shuttle.`datetime` as `datetime`, shuttle.`status` as `status`, people.nb as nb FROM shuttle LEFT JOIN people ON  shuttle.id=people.shuttle_id  WHERE shuttle.`datetime`> NOW() AND shuttle.`datetime` < (NOW() + INTERVAL(24-HOUR(NOW())) HOUR)) AS t GROUP BY t.`datetime`;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `list_future_shuttles` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
DELIMITER ;;
CREATE DEFINER=`navbot_bot`@`localhost` PROCEDURE `list_future_shuttles`()
BEGIN
SELECT DATE(`datetime`) as `date`,GROUP_CONCAT(DATE_FORMAT(`datetime`,"%H:%i") SEPARATOR ', ') as `hours` FROM (SELECT * from shuttle ORDER BY `datetime` ASC LIMIT 18446744073709551615) as shuttleo, `status` WHERE shuttleo.`datetime`> NOW() AND shuttleo.`datetime` < (NOW() + INTERVAL 15 DAY) GROUP BY DATE(shuttleo.`datetime`);

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `list_future_shuttles_timestamp` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
DELIMITER ;;
CREATE DEFINER=`navbot_bot`@`localhost` PROCEDURE `list_future_shuttles_timestamp`()
BEGIN
SELECT `datetime` FROM shuttle WHERE `datetime`> NOW() AND `datetime` < NOW() + INTERVAL(15) DAY;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `list_next_shuttles` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
DELIMITER ;;
CREATE DEFINER=`navbot_bot`@`localhost` PROCEDURE `list_next_shuttles`()
BEGIN
SELECT DATE(`datetime`) as `date`,GROUP_CONCAT(DATE_FORMAT(`datetime`,"%H:%i") SEPARATOR ', ') as `hours` FROM (SELECT * from shuttle ORDER BY `datetime` ASC LIMIT 18446744073709551615) as shuttleo  WHERE  shuttleo.`datetime`> (NOW() + INTERVAL (24 - HOUR(NOW())) HOUR) AND shuttleo.`datetime` < (NOW() + INTERVAL 7 DAY) GROUP BY DATE(shuttleo.`datetime`);
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `list_shuttle` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
DELIMITER ;;
CREATE DEFINER=`navbot_bot`@`localhost` PROCEDURE `list_shuttle`()
BEGIN
SELECT DATE(`datetime`) as `date`,GROUP_CONCAT(TIME(`datetime`)) as `hours` FROM shuttle WHERE `datetime`> (NOW() + INTERVAL (24 - HOUR(NOW())) HOUR) AND `datetime` < (NOW() + INTERVAL 5 DAY) GROUP BY DATE(`datetime`);
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `remove_shuttle` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
DELIMITER ;;
CREATE DEFINER=`navbot_bot`@`localhost` PROCEDURE `remove_shuttle`(timest DATETIME)
BEGIN
UPDATE   shuttle SET shuttle.`status`=  'cancelled' WHERE `datetime`=timest;
COMMIT;
SELECT "OK" AS rstatus;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;



