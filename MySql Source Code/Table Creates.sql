--Table Creates MySql

CREATE TABLE `tbl_Award` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type_id` int(11) NOT NULL,
  `nominator_id` int(11) NOT NULL,
  `nominee_id` int(11) NOT NULL,
  `date_awarded` date NOT NULL,
  `time_awarded` time NOT NULL,
  PRIMARY KEY (`id`),
  KEY `employee_id` (`nominator_id`),
  CONSTRAINT `tbl_Award_ibfk_1` FOREIGN KEY (`nominator_id`) REFERENCES `tbl_User` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=latin1;

CREATE TABLE `tbl_Award_Types` (
  `award_id` int(11) NOT NULL,
  `award_name` varchar(90) NOT NULL,
  PRIMARY KEY (`award_id`),
  UNIQUE KEY `award_name_UNIQUE` (`award_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `tbl_Security_Questions` (
  `id` smallint(6) NOT NULL AUTO_INCREMENT,
  `question` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1;

CREATE TABLE `tbl_User` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `firstname` varchar(50) DEFAULT NULL,
  `lastname` varchar(50) DEFAULT NULL,
  `password` varchar(100) NOT NULL,
  `signature_data` longtext,
  `isAdmin` tinyint(1) NOT NULL,
  `Created_Date` datetime(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email_UNIQUE` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=229 DEFAULT CHARSET=latin1;

CREATE TABLE `tbl_User_Security` (
  `userid` int(11) NOT NULL,
  `qid` int(11) NOT NULL,
  `answer` varchar(256) NOT NULL,
  KEY `userid_idx` (`userid`),
  CONSTRAINT `userid` FOREIGN KEY (`userid`) REFERENCES `tbl_User` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
