-- Stored Procedure Creates

DELIMITER $$
CREATE DEFINER=`wipuser`@`%` PROCEDURE `sp_Authenticate_Admin`(
	enteredEmail VARCHAR(255),
    enteredPassword VARCHAR(100)
)
BEGIN

	IF (SELECT COUNT(*) FROM tbl_User WHERE email = enteredEmail) = 0 THEN
		SELECT false AS 'Authenticated';
	ELSE
		SELECT 
			IF(password = enteredPassword AND isAdmin > 0, true, false) AS 'Authenticated', id
		FROM tbl_User
		WHERE email = enteredEmail;
	END IF;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`wipuser`@`%` PROCEDURE `sp_Authenticate_User`(
	enteredEmail VARCHAR(255),
    enteredPassword VARCHAR(100)
)
BEGIN

	IF (SELECT COUNT(*) FROM tbl_User WHERE email = enteredEmail) = 0 THEN
		SELECT false AS 'Authenticated';
	ELSE
		SELECT 
			IF(password = enteredPassword AND isAdmin = 0, true, false) AS 'Authenticated'
		FROM tbl_User
		WHERE email = enteredEmail;
	END IF;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`wipuser`@`%` PROCEDURE `sp_Check_Award_Existence`(
	awardType INT,
    nominator INT,
    nominee INT,
    dateAwarded DATE,
    timeAwarded TIME
)
BEGIN
	IF (SELECT COUNT(*) FROM tbl_Award 
			WHERE type_id = awardType
            AND nominator_id = nominator
            AND nominee_id = nominee
            AND date_awarded = dateAwarded
            AND time_awarded = timeAwarded) = 0 THEN
		SELECT false AS 'Exists';
	ELSE
		SELECT true AS 'Exists';
	END IF;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`wipuser`@`%` PROCEDURE `sp_Check_UserName_Existence`(
	enteredEmail VARCHAR(255)
)
BEGIN
	IF (SELECT COUNT(*) FROM tbl_User WHERE email = enteredEmail) = 0 THEN
		SELECT false AS 'Exists';
	ELSE
		SELECT true AS 'Exists';
	END IF;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`wipuser`@`%` PROCEDURE `sp_Delete_Award`(
	award_id INT
)
BEGIN
	DELETE from tbl_Award
    WHERE id = award_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`wipuser`@`%` PROCEDURE `sp_Delete_User`(
	userid INT
)
BEGIN
	DELETE
    FROM tbl_User
    WHERE id = userid;

END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`wipuser`@`%` PROCEDURE `sp_Evaluate_Security_Info`(
	user_id INT,
    sq1_id INT,
    sq2_id INT,
    ans1txt varchar(256),
    ans2txt varchar(256)
)
BEGIN
	IF((SELECT answer 
        FROM tbl_User_Security
        WHERE userid = user_id
			AND qid = sq1_id) = ans1txt
	AND
    (SELECT answer 
        FROM tbl_User_Security
        WHERE userid = user_id
			AND qid = sq2_id) = ans2txt) = 0 THEN
		SELECT false AS 'Exists';
	ELSE
		SELECT true AS 'Exists';
	END IF;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`wipuser`@`%` PROCEDURE `sp_Insert_Award`(
	awardType INT,
    nominator INT,
    nominee INT,
    dateAwarded DATE,
    timeAwarded TIME
)
INSERT INTO tbl_Award
(
	type_id,
	nominator_id,
    nominee_id,
	date_awarded,
	time_awarded
)
VALUES
(
	awardType,
    nominator,
    nominee,
    dateAwarded,
    timeAwarded
)$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`wipuser`@`%` PROCEDURE `sp_Insert_Security_Questions`(
	user_id INT,
    sq1_id INT,
    sq2_id INT,
    ans1txt varchar(256),
    ans2txt varchar(256)
)
BEGIN
	#Q1
    INSERT INTO tbl_User_Security (`userid`, `qid`, `answer`) VALUES (user_id, sq1_id, ans1txt);
    #Q2
    INSERT INTO tbl_User_Security (`userid`, `qid`, `answer`) VALUES (user_id, sq2_id, ans2txt);
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`wipuser`@`%` PROCEDURE `sp_Insert_User`(
	IN userEmail varchar(50),
    IN userFname varchar(50),
    IN userLname varchar(50),
    IN userPassword varchar(100),
    IN userIsAdmin TINYINT(1)
)
BEGIN
	INSERT INTO tbl_User
	(
		email,
		firstname,
		lastname,
		password,
		isAdmin,
        Created_Date
	)
	VALUES
	(
		userEmail,
		userFname,
		userLname,
		userPassword,
		userIsAdmin,
        now()
	);
    
    SHOW COUNT(*) ERRORS;
	SELECT @@error_count;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`wipuser`@`%` PROCEDURE `sp_Insert_User_By_Admin`(
	userEmail varchar(50),
    userFname varchar(50),
    userLname varchar(50),
    generatedPassword varchar(100),
    userLevel TINYINT(1)
)
BEGIN
	INSERT INTO tbl_User
	(
		email,
		firstname,
		lastname,
		password,
		isAdmin,
        Created_Date
	)
	VALUES
	(
		userEmail,
		userFname,
		userLname,
		generatedPassword,
		userLevel,
        now()
	);
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`wipuser`@`%` PROCEDURE `sp_Select_All_Security_Questions`()
BEGIN
	Select
		id,
		question
	FROM tbl_Security_Questions;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`wipuser`@`%` PROCEDURE `sp_Select_All_Users_By_Level`(
	access_level tinyint(1)
)
BEGIN
	SELECT
		email,
        firstname,
		lastname,
        DATE_FORMAT(left(Created_Date, 10), "%Y-%m-%d") as 'Created_Date',
        left((right(Created_Date, 10)), 5) as 'Created_Time',
		id
	FROM tbl_User
    WHERE isAdmin = access_level; 
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`wipuser`@`%` PROCEDURE `sp_Select_All_Users_Except`(
	creating_user_id INT
)
BEGIN
	SELECT 
		id,
        lastname,
        firstname
	FROM tbl_User
    WHERE id <> creating_user_id
	AND isAdmin = 0;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`wipuser`@`%` PROCEDURE `sp_Select_Awards_Received_By_UserId`(
	user_id INT
)
BEGIN
	select atp.award_name, concat(user.firstname,' ',user.lastname) as 'sender', aw.date_awarded
	from tbl_Award aw 
		join tbl_Award_Types atp on aw.type_id = atp.award_id
		join tbl_User nuser on aw.nominee_id = nuser.id
        join tbl_User user on aw.nominator_id = user.id
	where aw.nominee_id = user_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`wipuser`@`%` PROCEDURE `sp_Select_Awards_Sent_By_UserId`(
	user_id INT
)
BEGIN
	select atp.award_name, concat(neuser.firstname,' ',neuser.lastname) as 'sender', aw.date_awarded, aw.id
	from tbl_Award aw 
		join tbl_Award_Types atp on aw.type_id = atp.award_id
		join tbl_User user on aw.nominator_id = user.id
        join tbl_User neuser on aw.nominee_id = neuser.id
	where aw.nominator_id = user_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`wipuser`@`%` PROCEDURE `sp_Select_Security_Question_Info_By_User_Id`(
	user_id INT
)
BEGIN
	SELECT qid, question
    FROM tbl_User_Security us JOIN tbl_Security_Questions sq 
    ON us.qid = sq.id
    WHERE us.userid = user_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`wipuser`@`%` PROCEDURE `sp_Select_Single_Award_By_Id`(
	award_id INT
)
BEGIN
    SELECT
		IF(COUNT(*) > 0, true, false) as 'Exists'
	FROM tbl_Award
    WHERE id = award_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`wipuser`@`%` PROCEDURE `sp_Select_Single_User_By_Id`(
	user_id INT
)
BEGIN
    SELECT
		IF(COUNT(*) > 0, true, false) as 'Exists'
	FROM tbl_User
    WHERE id = user_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`wipuser`@`%` PROCEDURE `sp_Select_User_By_Id`(
	userid INT
)
BEGIN
	SELECT 
		email,
		firstname,
        lastname,
        signature_data,
        isAdmin
	FROM tbl_User
    WHERE id = userid;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`wipuser`@`%` PROCEDURE `sp_Select_UserId_By_Email`(
	EmailParam VARCHAR(255)
)
BEGIN
	SELECT id
    FROM tbl_User
    WHERE email = EmailParam
    and isAdmin <> 2;	#no super admin
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`wipuser`@`%` PROCEDURE `sp_Update_Password_By_UserId`(
	UserId INT,
    pass_word varchar(100)
)
BEGIN
	UPDATE tbl_User
    SET password = pass_word
    WHERE id = UserId;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`wipuser`@`%` PROCEDURE `sp_Update_Security_Questions`(
	user_id INT,
    sq1_id INT,
    sq2_id INT,
    ans1txt varchar(256),
    ans2txt varchar(256)
)
BEGIN
	#Q1
    INSERT INTO tbl_User_Security (`userid`, `qid`, `answer`) VALUES (user_id, sq1_id, ans1txt);
    #Q2
    INSERT INTO tbl_User_Security (`userid`, `qid`, `answer`) VALUES (user_id, sq2_id, ans2txt);
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`wipuser`@`%` PROCEDURE `sp_Update_User`(
	user_id INT,
    userFname varchar(50),
	userLname varchar(50),
    username varchar(255)
)
BEGIN
	UPDATE tbl_User
	SET 
		lastname = userLname,
		firstname = userFname,
        email = username
	WHERE id = user_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`wipuser`@`%` PROCEDURE `sp_Update_User_Signature`(
	UserId INT,
    SignatureData LONGTEXT
)
BEGIN
	UPDATE tbl_User
    SET signature_data = SignatureData
    WHERE id = UserId;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`wipuser`@`%` PROCEDURE `sp_User_Check_Security_Questions_Existence`(
	user_Id INT
)
BEGIN
    SELECT
		IF(COUNT(*) = 2, true, false) as 'Exists'
	FROM tbl_User_Security 
    WHERE userid = user_Id;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`wipuser`@`%` PROCEDURE `sp_User_Check_Signature_Existence`(
	userId INT
)
BEGIN
	SELECT
		IF(signature_data is NOT null, true, false) as 'Signature_Exists'
	FROM tbl_User 
    WHERE id = userId;
END$$
DELIMITER ;
