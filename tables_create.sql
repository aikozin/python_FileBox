CREATE TABLE `session` (
  `id_session` varchar(255) NOT NULL,
  `time_start` timestamp NOT NULL,
  `time_end` timestamp NOT NULL,
  `web_ip` varchar(255) DEFAULT NULL,
  `web_agent` varchar(255) DEFAULT NULL,
  `mobile_ip` varchar(255) DEFAULT NULL,
  `mobile_agent` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_session`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `data` (
  `id_file` bigint unsigned NOT NULL AUTO_INCREMENT,
  `id_session` varchar(255) NOT NULL,
  `type` varchar(255) NOT NULL,
  `file_name_real` varchar(255) NOT NULL,
  `file_name_fs` varchar(255) NOT NULL,
  `time_birth` timestamp NOT NULL,
  `time_death` timestamp NOT NULL,
  `status` varchar(255) NOT NULL,
  PRIMARY KEY (`id_file`),
  KEY `fk_id_session` (`id_session`),
  CONSTRAINT `fk_id_session` FOREIGN KEY (`id_session`) REFERENCES `session` (`id_session`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;