#Oregon State Crux Final Project:
#Wip-Awards.com

import MySQLdb
import logging
import logging.handlers
import fnmatch
import os
import json
import urllib
import urllib2
import subprocess
import datetime
import base64
import jwt
import string
from Cookie import SimpleCookie
import random
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders
from wsgiref.simple_server import make_server
import cgi
from cgi import parse_qs, escape

import pages

#src: information for logging provided by Amazon Web Services
# "Getting Started with Python on AWS" guide

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Handler 
LOG_FILE = '/opt/python/log/wip-awards.log'
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1048576, backupCount=5)
handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Add Formatter to Handler
handler.setFormatter(formatter)

# add Handler to Logger
logger.addHandler(handler)

# db info
DB_HOST = 'wipawardsdb.c2iugyb7o9rr.us-west-2.rds.amazonaws.com'
DB_USER = os.environ['RDS_USERNAME']
DB_PASSWORD = os.environ['RDS_PASSWORD']
DB_NAME = 'wipawardsdb'

#JWT encode
encoder = 'wipencoded'

#homemade cookie killer, no source
#this is to hold userids of cookies that have been deleted or otherwise
#disallowed. This is in case we delete a user/admin and we cannot alter
#their cookie, we can make sure they cant access the site after deletion
#drawback: this gets emptied when a redeploy of application.py occurs
stale_cookie_jar = []

def add_stale_cookie_to_jar(int_userid):
	stale_cookie_jar.append(int_userid)

def notDeletedUser(int_userid):
	return int_userid not in stale_cookie_jar
	
def cookie_header():
	#source: https://jayconrod.com/posts/17/how-to-use-http-cookies-in-python
	#source: http://pwp.stevecassidy.net/wsgi/cookies.html
	
	expiration = datetime.datetime.now() + datetime.timedelta(days=7) #expire in a week
	
	data = {}
	data['userid'] = os.environ.get("userid")
	data['permission_level'] = os.environ.get("permission_level")
	
	#cleanup
	os.environ.pop("userid")
	os.environ.pop("permission_level")
	
	cookie = SimpleCookie()
	cookie["session"] = jwt.encode(data, encoder, algorithm='HS256')
	cookie["session"]["domain"] = ".wip-awards.us-west-2.elasticbeanstalk.com"
	cookie["session"]["path"] = "/"
	cookie["session"]["expires"] = expiration.strftime("%a, %d-%b-%Y %H:%M:%S PST")
	return ('Set-Cookie', cookie['session'].OutputString())

def log_out_user(environ, start_response):
	if validAdminCookiePresent(environ) or validNonAdmCookiePresent(environ):
	
		expiration = datetime.datetime.now() - datetime.timedelta(days=700) #expire in the past (delete)

		cookie = SimpleCookie()
		cookie["session"] = 'X'
		cookie["session"]["domain"] = ".wip-awards.us-west-2.elasticbeanstalk.com"
		cookie["session"]["path"] = "/"
		cookie["session"]["expires"] = expiration.strftime("%a, %d-%b-%Y %H:%M:%S PST")
		cookie_header = ('Set-Cookie', cookie['session'].OutputString())
		
		p_level = getPermissionLevel(environ)
		
		if p_level is 1:
			location_header = ('Location','/')
		elif p_level is 2:
			location_header = ('Location','adminlogin.html')
		else:
			return internal_server_error(environ, start_response)
		
		headers = [('content-type','text/html'), location_header, cookie_header]
		start_response('302 Found', headers)
		return '' #redirect to location specified by permission level

def file(environ, start_response):
	if validAdminCookiePresent(environ) is True:
		page = get_webpage('file.html', environ, start_response)
		start_response('200 OK', [('content-type','text/html'),])
		return [page]
	else:
		return admin_unauthorized(environ, start_response)

def analytics(environ, start_response):
	if validAdminCookiePresent(environ) is True:
		verb = environ['REQUEST_METHOD']
		if verb == 'GET':
			#fill up var for options selects on page; all same
			analytics_options = '''<select name="time" style="width:35%;">
								<option value="1">1 Month</option>
								<option value="2">2 Months</option>
								<option value="3">3 Months</option>
								<option value="4">4 Months</option>
								<option value="5">5 Months</option>
								<option value="6">6 Months</option>
								<option value="7">7 Months</option>
								<option value="8">8 Months</option>
								<option value="9">9 Months</option>
								<option value="10">10 Months</option>
								<option value="11">11 Months</option>
								<option value="12">Year</option>
								<option value="13">All Time</option>
							</select>'''
			page = get_webpage('analytics.html', environ, start_response)
			page = page.replace('{{selector}}', analytics_options)
			start_response('200 OK', [('content-type','text/html'),])
			return [page]
		elif verb == 'POST':
			post_size = get_post_body_size(environ)
			body = environ['wsgi.input'].read(post_size)
			parsed_post = parse_qs(body)
			graph = parsed_post.get('graph', [''])[0]
			time = parsed_post.get('time', [''])[0]
			if graph == '1':
				pages.test(time)
				return file(environ, start_response)
			elif graph == '2':
				pages.last_year()
				return file(environ, start_response)
			elif graph == '3':
				pages.user_given(time)
				return file(environ, start_response)
			elif graph == '4':
				pages.user_received(time)
				return file(environ, start_response)
			elif graph == '5':
				pages.given_by_domain(time)
				return file(environ, start_response)
			elif graph == '6':
				pages.received_by_domain(time)
				return file(environ, start_response)
	else:
		return admin_unauthorized(environ, start_response)

def generate_random_password():
	#src: https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
	return (''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(10)))
	
def encode_id(raw):
	raw = str(int(raw) * 1024 * 1024)	#added layer
	#src: https://stackoverflow.com/questions/2490334/simple-way-to-encode-a-string-according-to-a-password
	enc = []
	for i in range(len(raw)):
		key_c = encoder[i % len(encoder)]
		enc_c = chr((ord(raw[i]) + ord(key_c)) % 256)
		enc.append(enc_c)
	return base64.urlsafe_b64encode("".join(enc))

def decode_id(enc):
	#src: https://stackoverflow.com/questions/2490334/simple-way-to-encode-a-string-according-to-a-password
	dec = []
	enc = base64.urlsafe_b64decode(enc)
	for i in range(len(enc)):
		key_c = encoder[i % len(encoder)]
		dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
		dec.append(dec_c)
	return str((int("".join(dec))/(1024 * 1024))) #reverse added layer
	
def get_webpage(page, environ, start_response):
	#src: https://docs.python.org/2/tutorial/inputoutput.html
	page = os.path.join('templates', page)
	try:
		with open(page, 'r') as file:
			page = file.read()
			file.close()
	except Exception, e:
		logger.error(str(e))
		return page_not_found(environ, start_response)

	return page

#this function is for mysql commands only (insert, update, delete, etc)
#reson for separation is for different needs of command/query in mysql/python accessing
def mysql_execute_command(start_response, environ, sp_name, args):
	con = None
	result = None
	try:
		#partial src: http://laviefrugale.blogspot.com/2011/03/python-and-mysql-autocommit.html
		con = MySQLdb.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)  
		con.autocommit(1)	#this took forever to figure out as inserts were buring identity ints but not committing!
		cursor = con.cursor()
		cursor.callproc(sp_name, args)
		cursor.close()
		con.close()
	except MySQLdb.Error, e:
		error = 'Error {0}: {1} -- '.format(e.args[0], e.args[1])
		logger.error(error)
		return internal_server_error(environ, start_response)		
	
	return result		
	
#this function is for mysql commands only (select)
#reson for separation is for different needs of command/query in mysql/python accessing
def mysql_execute_query(start_response, environ, sp_name, args):
	con = None
	result = None
	try:
		con = MySQLdb.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)  
		cursor = con.cursor()
		cursor.callproc(sp_name, args)
		if int(cursor.rowcount) == 0:
			cursor.close()
		else:
			result = cursor.fetchall()
			cursor.close()
	except MySQLdb.Error, e:
		logger.error('Error {0}: {1} -- '.format(e.args[0], e.args[1]))
		return internal_server_error(environ, start_response)		
	finally:
		if con:
			con.close()

	return result

def send_account_created_email(greeting, recipient, generated_password):
	#source: http://naelshiab.com/tutorial-send-email-python/
	fromaddr = 'noreply.wipawards@gmail.com'
	 
	msg = MIMEMultipart()
	 
	msg['From'] = 'noreply.wipawards.com'
	msg['To'] = recipient
	msg['Subject'] = greeting

	body = "http://wip-awards.us-west-2.elasticbeanstalk.com/\n\n"
	body += "Username: " + recipient + "\n"
	body += "Password: " + generated_password + "\n"

	msg.attach(MIMEText(body, 'plain'))
		 
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(fromaddr, 'PolloLoco007!')
	text = msg.as_string()
	server.sendmail(fromaddr, recipient, text)
	server.quit()
	
def send_latex_email(recipient, award_file_path):
	#source: http://naelshiab.com/tutorial-send-email-python/
	fromaddr = 'noreply.wipawards@gmail.com'
	 
	msg = MIMEMultipart()
	 
	msg['From'] = 'noreply.wipawards.com'
	msg['To'] = recipient
	msg['Subject'] = 'A Special Award for You'

	html = get_latex_content('Email')
	msg.attach(MIMEText(html, 'html'))

	attachment = open(award_file_path, "rb")
	 
	part = MIMEBase('application', 'octet-stream')
	part.set_payload((attachment).read())
	encoders.encode_base64(part)
	part.add_header('Content-Disposition', "attachment; filename= %s" % 'award.pdf')
	 
	msg.attach(part)
	 
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(fromaddr, 'PolloLoco007!')
	text = msg.as_string()
	server.sendmail(fromaddr, recipient, text)
	server.quit()
	
#reCAPTCHA_checker is to process the reCAPTCHA information passed on incoming web call
#checked against secret via google reCAPTCHA API 
#reference : https://stackoverflow.com/questions/28657935/new-google-recaptcha-with-django-recaptcha
def reCAPTCHA_checker(key):
	url = 'https://www.google.com/recaptcha/api/siteverify'
	values = {'secret' : '6LcsT0MUAAAAAC741cXYH5z_MqCyVGvxgdp6faY7','response' : key}

	rem = urllib.urlencode(values)
	req = urllib2.Request(url, rem)
	response = urllib2.urlopen(req)
	data = response.read()
	
	prs = json.loads(data)
	res = prs['success']
	
	if res == True:
		return 1
	else:
		return 0

def external_admin_landing(environ, start_response):
	if validAdminCookiePresent(environ) is True:
		page = get_webpage('adminlanding.html', environ, start_response)
		headers = [('content-type','text/html'),('Location','adminlanding.html')]
		start_response('200 OK', headers)
		return [page]
	else:
		return admin_unauthorized(environ, start_response)
	
def internal_admin_landing(environ, start_response):
	page = get_webpage('adminlanding.html', environ, start_response)
	headers = [('content-type','text/html'),('Location','adminlanding.html'),cookie_header()]
	start_response('200 OK', headers)
	return [page]

def internal_landing(environ, start_response):
	page = get_webpage('landing.html', environ, start_response)
	headers = [('content-type','text/html'),('Location','landing.html'),cookie_header()]
	start_response('200 OK', headers)
	return [page]

def external_landing(environ, start_response):
	if validNonAdmCookiePresent(environ) is True:
		page = get_webpage('landing.html', environ, start_response)
		headers = [('content-type','text/html'),('Location','landing.html')]
		start_response('200 OK', headers)
		return [page]
	else:
		return unauthorized(environ, start_response)

def admin_pw_page(environ, start_response):
	page = get_webpage('adminresetpassword.html', environ, start_response)
	start_response('200 OK', [('content-type','text/html'),])
	return [page]

def reset_password(environ, start_response):
	verb = environ['REQUEST_METHOD']
	if verb == 'POST':
		parsed_post = getParsedPost(environ)

		userid = int(parsed_post.get('userid', [''])[0])
		q1id = int(parsed_post.get('q1id', [''])[0])
		q2id = int(parsed_post.get('q2id', [''])[0])
		q1ans = escape(parsed_post.get('q1ans', [''])[0])
		q2ans = escape(parsed_post.get('q2ans', [''])[0])
		password = escape(parsed_post.get('pword', [''])[0])

		args = [userid, q1id, q2id, q1ans, q2ans]
		result = mysql_execute_query(start_response, environ, 'sp_Evaluate_Security_Info', args)

		if int(result[0][0]) == 1:
			args = [userid, password]
			result = mysql_execute_command(start_response, environ, 'sp_Update_Password_By_UserId', args)
			start_response('200 OK', [('content-type','text/html'),])
			return ''
		else:
			start_response('400 BAD REQUEST', [('content-type','text/html'),])
			return ''
	else:
		return internal_server_error(environ, start_response)

def user_change_password(environ, start_response):
	if validNonAdmCookiePresent(environ) is True:
		verb = environ['REQUEST_METHOD']
		if verb == 'POST':
			parsed_post = getParsedPost(environ)	
			userid = decode_id(parsed_post.get('id', [''])[0])
			new_password = parsed_post.get('pwd', [''])[0]
			
			args = [userid, new_password]
			result = mysql_execute_command(start_response, environ, 'sp_Update_Password_By_UserId', args)

			start_response('200 OK', [('content-type','text/html'),])
			return ''
		else:
			start_response('400 BAD REQUEST', [('content-type','text/html'),])
			return ''
	else:
		return unauthorized(environ, start_response)
		
def admin_force_reset_password(environ, start_response):
	if validAdminCookiePresent(environ) is True:
		verb = environ['REQUEST_METHOD']
		if verb == 'POST':
			parsed_post = getParsedPost(environ)
			userid = decode_id(parsed_post.get('id', [''])[0])
			generated_password = generate_random_password()
			
			args = [int(userid), generated_password]
			result = mysql_execute_command(start_response, environ, 'sp_Update_Password_By_UserId', args)
			result2 = mysql_execute_query(start_response, environ, 'sp_Select_User_By_Id', [int(userid)])
			
			username = (result2[0])[0]
			
			send_account_created_email('Your password has been reset', username, generated_password)
			start_response('200 OK', [('content-type','text/html'),])
			return ''
		else:
			start_response('400 BAD REQUEST', [('content-type','text/html'),])
			return ''
	else:
		return admin_unauthorized(environ, start_response)

def awards_management_page(environ, start_response):
	if validNonAdmCookiePresent(environ) is True:
		page = get_webpage('awardsmanagement.html', environ, start_response)
		userid = getUserIdIntegerFromCookie(environ)
		args = [userid]
		
		result = mysql_execute_query(start_response, environ, 'sp_Select_Awards_Received_By_UserId', args)
		
		awards_rec_table = ''
		if result is None:
			t_row = '<tr><td> - </td><td> - </td><td> - </td></tr>'
			awards_rec_table += str(t_row)
		else:
			for row in result:
				t_row = '<tr><td>' + str(row[0]) + '</td><td>' + str(row[1]) + '</td><td>' + format_date(str(row[2])) + '</td></tr>'
				awards_rec_table += str(t_row)

		page = page.replace('{{Awards_Received}}', awards_rec_table)

		result = mysql_execute_query(start_response, environ, 'sp_Select_Awards_Sent_By_UserId', args)
		
		awards_sent_table = ''
		if result is None:
			t_row = '<tr><td> - </td><td> - </td><td> - </td><td></td></tr>'
			awards_sent_table += str(t_row)
		else:			
			for row in result:
				awrd_id = str(row[3])
				t_row = '<tr class="' + awrd_id + '"><td>' + str(row[0]) + '</td><td>' + str(row[1]) + '</td><td>' + format_date(str(row[2])) + '</td><td><button class="deleter" id="' + awrd_id +'">DELETE</button></td></tr>'
				awards_sent_table+=str(t_row)

		page = page.replace('{{Awards_Sent}}', awards_sent_table)

		headers = [('content-type','text/html'),]
		start_response('200 OK', headers)
		return [page]
	else:
		return unauthorized(environ, start_response)

def create_award(environ, start_response):
	if validNonAdmCookiePresent(environ) is True:
		start_response('200 OK', [('content-type','text/html'),])
		verb = environ['REQUEST_METHOD']
		if verb == 'GET':
			userid = getUserIdIntegerFromCookie(environ)
			page = get_webpage('createaward.html', environ, start_response)
			combo = '''<option value="" disabled selected>Select Award Recipient</option>'''
			args = [userid]
			result = mysql_execute_query(start_response, environ, 'sp_Select_All_Users_Except', args)
			for row in result:
				option = '<option value="' + str(row[0]) + '" >' + str(row[1]) + ', ' + str(row[2]) + '</option>'
				combo+=str(option)

			page = page.replace('{{user_dropdown}}', combo)
			return [page]
		elif verb == 'POST':
			parsed_post = getParsedPost(environ)
			
			type = int(parsed_post.get('type', [''])[0])
			creatingUser = getUserIdIntegerFromCookie(environ)
			receivngUser = int(parsed_post.get('receivngUser', [''])[0])
			date = parsed_post.get('date', [''])[0]
			time = parsed_post.get('time', [''])[0]
			
			args = [type, creatingUser, receivngUser, date, time]
			result = mysql_execute_command(start_response, environ, 'sp_Insert_Award', args)
			
			result = mysql_execute_query(start_response, environ, 'sp_Check_Award_Existence', args)	

			if int(result[0][0]) == 1:
				DB_to_latex(type, creatingUser, receivngUser, date, time, environ, start_response)
				return '' #success
			else:
				return internal_server_error(environ, start_response)
		else:
			return internal_server_error(environ, start_response)
	else:
		return unauthorized(environ, start_response)

def security_question_register(environ, start_response):
	page = get_webpage('securityquestions.html', environ, start_response)
	combo = '''<option value="" disabled selected></option>'''
	result = mysql_execute_query(start_response, environ, 'sp_Select_All_Security_Questions', [])
	for row in result:
		option = '<option value="' + str(row[0]) + '" >' + str(row[1]) + '</option>'
		combo+=str(option)

	page = page.replace('{{security_questions}}', combo)
	start_response('200 OK', [('content-type','text/html'),('Location','securityquestions.html'),cookie_header()])
	return [page]
		
def reset_password_page(environ, start_response):
	page = get_webpage('resetpassword.html', environ, start_response)
	start_response('200 OK', [('content-type','text/html'),])
	return [page]
	
def capture_signature_page(environ, start_response):
	if validNonAdmCookiePresent(environ) is True:
		page = get_webpage('capturesignature.html', environ, start_response)
		start_response('201 OK', [('content-type','text/html'),('Location','capturesignature.html')])
		return [page]
	else:
		return unauthorized(environ, start_response)
		
def unauthorized(environ, start_response):
	page = get_webpage('unauthorized_user.html', environ, start_response)
	start_response('401 Unauthorized', [('content-type','text/html'),])
	return [page]

def admin_unauthorized(environ, start_response):
	page = get_webpage('unauthorized_admin.html', environ, start_response)
	start_response('401 Unauthorized', [('content-type','text/html'),])
	return [page]

def page_edit_user_profile(userid, environ, start_response):
	page = get_webpage('edituserprofile.html', environ, start_response)
	page = page.replace('{{userid}}', encode_id(userid))
	start_response('200 OK', [('content-type','text/html'),])
	return [page]
	
def page_not_found(environ, start_response):
	start_response('404 Not Found', [('content-type','text/html'),])
	page = get_webpage('NotFound.html', environ, start_response)
	return [page]

def internal_server_error(environ, start_response):
	start_response('500 Internal Server Error', [('content-type','text/html'),])
	return ["""<html><h1>Internal Server ERROR</h1><p>Oh boy...that's on us...</br> Return to the <a href="/">home page</a></p></html>""",]
	
def bad_request(environ, start_response):
	start_response('400 Bad Request', [('content-type','text/html'),])
	return ["""<html><h1>BAD REQUEST!</h1><p>It's not us, it's you :( </br> Return to the <a href="/">home page</a></p></html>""",]
	
def get_post_body_size(environ):
	post_size = None
	try:
		post_size = int(environ.get('CONTENT_LENGTH', 0))
	except (ValueError):
		post_size = 0
	return post_size

def check_for_username(start_response, environ, username_to_check):
	args = [username_to_check]
	result = mysql_execute_query(start_response, environ, 'sp_Check_UserName_Existence', args)
	return int(result[0][0])

def get_userid_by_email(start_response, environ, email):
	args = [email]
	result = mysql_execute_query(start_response, environ, 'sp_Select_UserId_By_Email', args)
	if result:
		return int(result[0][0])
	else:
		return None
	
def update_user_signature(userid, signature, start_response, environ):
	args = [userid, signature]	
	result = mysql_execute_command(start_response, environ, 'sp_Update_User_Signature', args)
	return result

def check_signature_exists(userid, start_response, environ):
	args = [userid]
	resultSig = mysql_execute_query(start_response, environ, 'sp_User_Check_Signature_Existence', args)
	return int(resultSig[0][0])

def getParsedPost(environ):
	post_size = get_post_body_size(environ)
	body = environ['wsgi.input'].read(post_size)
	parsed_post = parse_qs(body)
	return parsed_post
	
def get_user_pass_captch(environ):
	parsed_post = getParsedPost(environ)

	username = parsed_post.get('username', [''])[0]
	password = parsed_post.get('password', [''])[0]
	reCAPTCHA = parsed_post.get('g-recaptcha-response', [''])[0]
	
	#prevent injection
	username = escape(username)
	password = escape(password)
	
	return username, password, reCAPTCHA

def get_user_pass_fname_lname_captch(environ):
	parsed_post = getParsedPost(environ)

	username = parsed_post.get('username', [''])[0]
	password = parsed_post.get('password', [''])[0]
	fname = parsed_post.get('firstname', [''])[0]
	lname = parsed_post.get('lastname', [''])[0]
	reCAPTCHA = parsed_post.get('g-recaptcha-response', [''])[0]

	#prevent injection
	username = escape(username)
	password = escape(password)
	fname = escape(fname)
	lname = escape(lname)

	return username, password, fname, lname, reCAPTCHA
	
def check_username(environ, start_response):
	start_response('200 OK', [('content-type','text/html'),])
	username_to_check = environ['PATH_INFO'].split("/")[2]
	
	username_preexists = check_for_username(start_response, environ, username_to_check)

	if username_preexists is 1:
		return 'true'
	else:
		return 'false'

def check_security_questions_exist(userid, start_response, environ):
	args = [userid]
	result = mysql_execute_query(start_response, environ, 'sp_User_Check_Security_Questions_Existence', args)
	return int(result[0][0])
	
def getPermissionLevel(environ):
	if "HTTP_COOKIE" in environ:
		cookie = SimpleCookie(environ['HTTP_COOKIE'])
		decoded_json = jwt.decode((cookie["session"].value), encoder, algorithms=['HS256'])
		if int(decoded_json['permission_level']) == 1:
			return 1
		else:
			return 2
	else:
		return 0

def validNonAdmCookiePresent(environ):
	if "HTTP_COOKIE" in environ:
		cookie = SimpleCookie(environ['HTTP_COOKIE'])
		decoded_json = jwt.decode((cookie["session"].value), encoder, algorithms=['HS256'])
		if int(decoded_json['permission_level']) == 1 and notDeletedUser(int(decoded_json['userid'])):
			return True
		else:
			return False
	else:
		return False

def validAdminCookiePresent(environ):
	if "HTTP_COOKIE" in environ:
		cookie = SimpleCookie(environ['HTTP_COOKIE'])
		decoded_json = jwt.decode((cookie["session"].value), encoder, algorithms=['HS256'])
		if int(decoded_json['permission_level']) > 1 and notDeletedUser(int(decoded_json['userid'])):
			return True
		else:
			return False
	else:
		return False

def getUserIdIntegerFromCookie(environ):
	if "HTTP_COOKIE" in environ:
		cookie = SimpleCookie(environ['HTTP_COOKIE'])
		decoded_json = jwt.decode((cookie["session"].value), encoder, algorithms=['HS256'])
		return int(decoded_json['userid'])
	else:
		return ''
		
def submit_security_questions(environ, start_response):
	start_response('200 OK', [('content-type','text/html'),])
	if validNonAdmCookiePresent(environ) is True:
		verb = environ['REQUEST_METHOD']
		if verb == 'POST':
			parsed_post = getParsedPost(environ)

			userid = getUserIdIntegerFromCookie(environ)
			q1 = parsed_post.get('q1id', [''])[0]
			q2 = parsed_post.get('q2id', [''])[0]
			# prevent injection
			a1 = escape(parsed_post.get('q1ans', [''])[0])
			a2 = escape(parsed_post.get('q2ans', [''])[0])

			args = [int(userid), q1, q2, a1, a2]
			result = mysql_execute_command(start_response, environ, 'sp_Insert_Security_Questions', args)

			return '' #200OK reroutes to signature page in jquery
		else:
			return bad_request(environ, start_response)
	else:
		return unauthorized(environ, start_response)

def delete_user(environ, start_response):
	if validAdminCookiePresent(environ) is True:
		if environ['REQUEST_METHOD'] == 'DELETE':
			user_id = int(environ['PATH_INFO'].split("/")[2])
	
			args = [user_id]
			result = mysql_execute_command(start_response, environ, 'sp_Delete_User', args)
	
			result_check = mysql_execute_query(start_response, environ, 'sp_Select_Single_User_By_Id', args)
			
			if int(result_check[0][0]) == 0:
				#add to stale_cookie_jar to prevent login with valid cookie
				add_stale_cookie_to_jar(user_id)
				start_response('200 OK', [('content-type','text/html'),])
				return ''
			else:
				start_response('500 Internal Server Error', [('content-type','text/html'),])
				return ''
		else:
			return bad_request(environ, start_response)
	else:
		return admin_unauthorized(environ, start_response)
		
def delete_award(environ, start_response):
	if validNonAdmCookiePresent(environ) is True:
		if environ['REQUEST_METHOD'] == 'DELETE':
			award_id = environ['PATH_INFO'].split("/")[2]
	
			args = [int(award_id)]
			result = mysql_execute_command(start_response, environ, 'sp_Delete_Award', args)
	
			result_check = mysql_execute_query(start_response, environ, 'sp_Select_Single_Award_By_Id', args)
			
			if int(result_check[0][0]) == 0:
				start_response('200 OK', [('content-type','text/html'),])
				return ''
			else:
				start_response('500 Internal Server Error', [('content-type','text/html'),])
				return ''
		else:
			return bad_request(environ, start_response)
	else:
		return unauthorized(environ, start_response)

def check_username_for_pw_reset(environ, start_response):
	verb = environ['REQUEST_METHOD']
	if verb == 'POST':
		parsed_post = getParsedPost(environ)
		
		username = escape(parsed_post.get('username', [''])[0])
		userid = get_userid_by_email(start_response, environ, username)
		
		if userid != None:
			args = [userid]	
			security_info = mysql_execute_query(start_response, environ, 'sp_Select_Security_Question_Info_By_User_Id', args)

			data = {}
			data['userid'] = userid
			data['question1id'] = (security_info[0])[0]
			data['question1'] = (security_info[0])[1]
			data['question2id'] = (security_info[1])[0]
			data['question2'] = (security_info[1])[1]

			start_response('200 OK', [('content-type','text/html'),])
			return json.dumps(data)
		else:
			start_response('404 NOT FOUND', [('content-type','text/html'),])
			return ''
	else:
		return bad_request(environ, start_response)

def edit_user_profile(environ, start_response):
	if validNonAdmCookiePresent(environ) is True:
		verb = environ['REQUEST_METHOD']
		if verb == 'GET':
			userid = str(getUserIdIntegerFromCookie(environ))
			return page_edit_user_profile(userid, environ, start_response)
		elif verb == 'POST':
			parsed_post = getParsedPost(environ)
		
			userid = getUserIdIntegerFromCookie(environ)
			#prevent injection
			fname = escape(parsed_post.get('fname', [''])[0])
			lname = escape(parsed_post.get('lname', [''])[0])

			result = mysql_execute_query(start_response, environ, 'sp_Select_User_By_Id', [int(userid)])
			username = str(result[0][0])

			if(fname == ''):
				fname = str(result[0][1])
			if(lname == ''):
				lname = str(result[0][2])
					
			args = [int(userid), fname, lname, username]
			result = mysql_execute_command(start_response, environ, 'sp_Update_User', args)
			
			start_response('200 OK', [('content-type','text/html'),])
			return ''
		else:
			return bad_request(environ, start_response)
	else:
		return unauthorized(environ, start_response)

def update_signature(environ, start_response):
	if validNonAdmCookiePresent(environ) is True:
		verb = environ['REQUEST_METHOD']
		if verb == 'GET':
			userid = getUserIdIntegerFromCookie(environ)
			page = get_webpage('updatesignature.html', environ, start_response)
			page = page.replace('{{userid}}', encode_id(userid))
			start_response('200 OK', [('content-type','text/html'),])
			return [page]
		elif verb == 'POST':
			parsed_post = getParsedPost(environ)
		
			userid = decode_id(parsed_post.get('userid', [''])[0])
			signature = parsed_post.get('signature', [''])[0]

			updateResult = update_user_signature(int(userid), signature, start_response, environ)

			start_response('200 OK', [('content-type','text/html'),])
			return ''
		else:
			return bad_request(environ, start_response)
	else:
		return unauthorized(environ, start_response)
		
def save_signature(environ, start_response):
	if validNonAdmCookiePresent(environ) is True:
		start_response('200 OK', [('content-type','text/html'),])
		verb = environ['REQUEST_METHOD']
		if verb == 'POST':
			parsed_post = getParsedPost(environ)
		
			userid = getUserIdIntegerFromCookie(environ)
			signature = parsed_post.get('signature', [''])[0]

			updateResult = update_user_signature(userid, signature, start_response, environ)
			signature_exists = check_signature_exists(str(userid), start_response, environ)
				
			if signature_exists is 1:
				os.environ["userid"] = str(userid)
				os.environ["permission_level"] = "1"
				return internal_landing(environ, start_response)
			else:
				return internal_server_error(environ, start_response)
		else:
			return bad_request(environ, start_response)
	else:
		return unauthorized(environ, start_response)

def register(environ, start_response):
	verb = environ['REQUEST_METHOD']
	if verb == 'GET':
		page = get_webpage('register.html', environ, start_response)
		start_response('200 OK', [('content-type','text/html'),('Location','register.html')])
		return [page]
	elif verb == 'POST':
		username, password, fname, lname, reCAPTCHA = get_user_pass_fname_lname_captch(environ)

		if reCAPTCHA_checker(reCAPTCHA) == 1:
			args = [username, fname, lname, password, 0]
			result = mysql_execute_command(start_response, environ, 'sp_Insert_User', args)

			if check_for_username(start_response, environ, username) is 1:
				userid = get_userid_by_email(start_response, environ, username)
				os.environ["userid"] = str(userid)
				os.environ["permission_level"] = "1"
				return security_question_register(environ, start_response)
			else:
				return internal_server_error(environ, start_response)				
		else:
			return unauthorized(environ, start_response)	
	else:
		return page_not_found(environ, start_response)

def format_time(time):
	period = ''
	hr, min = time.split(":")
	hours = int(hr)
	if hours > 12:
		period = 'PM'
		hours = hours - 12
	else:
		period = 'AM'
	
	time = '{}:{} {}'.format(str(hours), min, period)
	return time

def format_date(date):
	try:
		yy, mm, dd = date.split("-")
		mm = datetime.date(1900, int(mm), 1).strftime('%B')
		date = '{} {}, {}'.format(mm, str(int(dd)), yy) #str(int(dd)) to trim off extra leading '0' if present
		return date
	except:
		return format_date('01-01-1970') #failsafe

def get_latex_content(content_type):
	content_type = '{}.txt'.format(content_type)
	content = os.path.join('latex/content', content_type)
	try:
		with open(content, 'r') as file:
			content = file.read()
			file.close()
	except Exception, e:
		logger.error(str(e))

	return content

def DB_to_latex(type, creatingUser, receivngUser, date, time, environ, start_response):
	nominee_args = [receivngUser]
	nominee_info = mysql_execute_query(start_response, environ, 'sp_Select_User_By_Id', nominee_args)

	nominator_args = [creatingUser]
	nominator_info = mysql_execute_query(start_response, environ, 'sp_Select_User_By_Id', nominator_args)

	nominee_email = (nominee_info[0])[0]
	nominee_name = ((nominee_info[0])[1] + ' ' + (nominee_info[0])[2])

	nominator_name = ((nominator_info[0])[1] + ' ' + (nominator_info[0])[2])
	header, nominator_signature = ((nominator_info[0])[3]).split(',')
	
	jpgs_sig_img_path = os.path.join('latex/images', 'signature.jpg')

	#https://stackoverflow.com/questions/5368669/convert-base64-to-image-in-python
	jpg = open(jpgs_sig_img_path, "w")
	jpg.write(nominator_signature.decode('base64'))
	jpg.close()

	time = format_time(time)
	date = format_date(date)

	user_data = {'name': nominee_name, 'date': date, 'time': time, 'sender': nominator_name}

	content = ''
	if type == 1: #employee of the week
		content = get_latex_content('EOTW')
	elif type == 2: #employee of the month
		content = get_latex_content('EOTMNTH')
	elif type == 3: #best hat
		content = get_latex_content('HAT')

	filename = '{}_{}'.format('USRID', datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
	directory = 'latex/tex'
	file = os.path.join(directory, ''.join([filename,'.tex']))
	
	with open(file, 'w') as f:
		f.write(content % user_data)

	cmd = ['pdflatex', '-interaction', 'nonstopmode', '-output-directory', directory, file]
	proc = subprocess.Popen(cmd)
	proc.communicate()

	created_pdf_path = os.path.join(directory,''.join([filename,'.pdf']))
	
	retcode = proc.returncode
	if not retcode == 0:
		os.unlink(created_pdf_path)
		raise ValueError('Error {} executing command: {}'.format(retcode, ' '.join(cmd)))

	os.unlink(file)
	os.unlink(os.path.join(directory,''.join([filename,'.log'])))
	os.unlink(os.path.join(directory,''.join([filename,'.aux'])))

	#read file into variable
	pdf = None
	try:
		with open(created_pdf_path, 'r') as file:
			pdf = file.read()
			file.close()
	except Exception, e:
		logger.error(str(e))
		return internal_server_error(environ, start_response)
	
	#send file	
	send_latex_email(nominee_email, created_pdf_path)
	#delete file	
	os.unlink(created_pdf_path)
	#delete signature file
	os.unlink(jpgs_sig_img_path)
	return 

def admin_add_user(environ, start_response):
	if validAdminCookiePresent(environ) is True:
		verb = environ['REQUEST_METHOD']
		if verb == 'GET':
			page = get_webpage('adduser.html', environ, start_response)
			start_response('200 OK', [('content-type','text/html'),])
			return [page]
		elif verb == 'POST':
			parsed_post = getParsedPost(environ)
			username = parsed_post.get('username', [''])[0]
			fname = escape(parsed_post.get('fname', [''])[0])
			lname = escape(parsed_post.get('lname', [''])[0])
			access_level = parsed_post.get('type', [''])[0]
			
			#generate random 10 char password
			generated_password = generate_random_password()
			
			args = [username, fname, lname, generated_password, int(access_level)]
			result = mysql_execute_command(start_response, environ, 'sp_Insert_User', args)

			if check_for_username(start_response, environ, username) is 1:
				send_account_created_email('Your newly created WIP Awards account', username, generated_password)
				start_response('201 Created', [('content-type','text/html'),])
				return ''
			else:
				return internal_server_error(environ, start_response)	
		else:
			return bad_request(environ, start_response)
	else:
		return admin_unauthorized(environ, start_response)
	
def admin_edit_users(environ, start_response):
	if validAdminCookiePresent(environ) is True:
		verb = environ['REQUEST_METHOD']
		if verb == 'GET':
			keys = parse_qs(environ['QUERY_STRING'])
			userid_to_edit = keys.get('id', [''])[0]
			page = get_webpage('edituser.html', environ, start_response)
			
			result = mysql_execute_query(start_response, environ, 'sp_Select_User_By_Id', [int(userid_to_edit)])
			page = page.replace('{{username}}', str(result[0][0]))
			page = page.replace('{{firstname}}', str(result[0][1]))
			page = page.replace('{{lastname}}', str(result[0][2]))
			page = page.replace('{{userid}}', encode_id(userid_to_edit))
			if int(result[0][4]) == 1:
				page = page.replace('{{type}}', 'Admin')
			else:
				page = page.replace('{{type}}', 'User')
			start_response('200 OK', [('content-type','text/html'),])
			return [page]
		elif verb == 'POST':
			parsed_post = getParsedPost(environ)
			username = parsed_post.get('username', [''])[0]
			fname = escape(parsed_post.get('fname', [''])[0])
			lname = escape(parsed_post.get('lname', [''])[0])
			userid = decode_id(parsed_post.get('id', [''])[0])

			args = [int(userid), fname, lname, username]
			result = mysql_execute_command(start_response, environ, 'sp_Update_User', args)

			start_response('200 OK', [('content-type','text/html'),])
			return ''
		else:
			return bad_request(environ, start_response)
	else:
		return admin_unauthorized(environ, start_response)

def admin_manage_users(environ, start_response):
	if validAdminCookiePresent(environ) is True:
		page = get_webpage('manageusers.html', environ, start_response)
		
		admin_editing_id = getUserIdIntegerFromCookie(environ)

		result = mysql_execute_query(start_response, environ, 'sp_Select_All_Users_By_Level', [1])

		admin_table = ''
		if result is None:
			t_row = '<tr><td> - </td><td> - </td><td> - </td><td> - </td></tr>'
			admin_table += str(t_row)
		else:
			for row in result:
				a_id = str(row[5])
				t_row = '<tr class="' + a_id + '"><td>' + str(row[0]) + '</td><td>' + str(row[1]) + '</td><td>' + str(row[2]) + '</td><td>' + format_date(row[3]) + " " + format_time(row[4]) + '</td><td><a href="editusers.html?id=' + a_id + '"><button class="editer">EDIT</button></a></td>'
				if(int(row[5]) != int(admin_editing_id)):
					t_row += '<td><button class="deleter" id="' + a_id +'">DELETE</button></td>'
				else:
					t_row += '<td></td>'
				t_row += '</tr>'
				admin_table += str(t_row)

		page = page.replace('{{Admin_List}}', admin_table)

		result_user = mysql_execute_query(start_response, environ, 'sp_Select_All_Users_By_Level', [0])

		user_table = ''
		if result_user is None:
			t_row = '<tr><td> - </td><td> - </td><td> - </td><td> - </td></tr>'
			user_table += str(t_row)
		else:
			for urow in result_user:
				u_id = str(urow[5])
				t_row = '<tr class="' + u_id + '"><td>' + str(urow[0]) + '</td><td>' + str(urow[1]) + '</td><td>' + str(urow[2]) + '</td><td>' + format_date(urow[3]) + " " + format_time(urow[4]) + '</td><td><a href="editusers.html?id=' + u_id + '"><button class="editer">EDIT</button></a></td><td><button class="deleter" id="' + u_id +'">DELETE</button></td></tr>'
				user_table += str(t_row)

		page = page.replace('{{User_List}}', user_table)

		start_response('200 OK', [('content-type','text/html'),])
		return [page]
	else:
		return admin_unauthorized(environ, start_response)
		
def adminlogin(environ, start_response):
	start_response('200 OK', [('content-type','text/html'),])
	verb = environ['REQUEST_METHOD']
	if verb == 'GET':
		page = get_webpage('adminlogin.html', environ, start_response)
		start_response('200 OK', [('content-type','text/html'),('Location','adminlogin.html')])
		return [page]
	elif verb == 'POST':
		username, password, reCAPTCHA = get_user_pass_captch(environ)

		if reCAPTCHA_checker(reCAPTCHA) == 1:
			args = [username, password]
			result = mysql_execute_query(start_response, environ, 'sp_Authenticate_Admin', args)

			if int(result[0][0]) == 1:
				userid = int(result[0][1])
				os.environ["userid"] = str(userid)
				os.environ["permission_level"] = "2"
				return internal_admin_landing(environ, start_response)
			else:
				return admin_unauthorized(environ, start_response)
		else:
			return admin_unauthorized(environ, start_response)
	else:
		return bad_request(environ, start_response)

def index(environ, start_response):
	start_response('200 OK', [('content-type','text/html'),])
	verb = environ['REQUEST_METHOD']
	if verb == 'GET':
		if validNonAdmCookiePresent(environ) is True:
			return external_landing(environ, start_response)
		elif validAdminCookiePresent(environ) is True:
			return external_admin_landing(environ, start_response) 
		else:
			page = get_webpage('index.html', environ, start_response)
			start_response('200 OK', [('content-type','text/html'),('Location','index.html')])
			return [page]
	elif verb == 'POST':
		username, password, reCAPTCHA = get_user_pass_captch(environ)

		if reCAPTCHA_checker(reCAPTCHA) == 1:
			args = [username, password]
			result = mysql_execute_query(start_response, environ, 'sp_Authenticate_User', args)

			if int(result[0][0]) == 1:
				userid = get_userid_by_email(start_response, environ, username)
				os.environ["userid"] = str(userid)
				os.environ["permission_level"] = "1"

				if check_security_questions_exist(userid, start_response, environ) is 1:
					if check_signature_exists(userid, start_response, environ) is 1:
						return internal_landing(environ, start_response)
					else:
						return capture_signature_page(userid, environ, start_response)
				else:
					return security_question_register(environ, start_response)
			else:
				return unauthorized(environ, start_response)
		else:
			return unauthorized(environ, start_response)
	else:
		return bad_request(environ, start_response)

routes = [	('/',							index),
			('/register.html',				register),
			('/submitsignature.html',		save_signature),
			('/landing.html', 				external_landing),
			('/capturesignature.html',		capture_signature_page),
			('/adminlogin.html',			adminlogin),
			('/adminlanding.html',			external_admin_landing),
			('/createaward.html',			create_award),
			('/submitsecurity.html',		submit_security_questions),
			('/resetpassword.html', 		reset_password_page),
			('/checkUsername/*', 			check_username),
			('/testusernameforreset', 		check_username_for_pw_reset),
			('/tryresetpassword',			reset_password),
			('/forceresetpassword',			admin_force_reset_password),
			('/userchangepwd',				user_change_password),
			('/awardsmanagement.html',		awards_management_page),
			('/deleteaward/*', 				delete_award),
			('/deleteuser/*',				delete_user),
			('/edituserprofile.html',		edit_user_profile),
			('/adduser.html',				admin_add_user),
			('/manageusers.html',			admin_manage_users),
			('/editusers.html',				admin_edit_users),
			('/analytics.html',				analytics),
			('/adminresetpassword.html',	admin_pw_page),
			('/updatesignature.html',		update_signature),
			('/file', 						file),
			('/logout',						log_out_user)
		]

def application(environ, start_response):
	for path, app in routes:
		if fnmatch.fnmatch((environ['PATH_INFO']), path):
			return app(environ, start_response)
	return page_not_found(environ, start_response)

if __name__ == '__main__':
    httpd = make_server('', 8000, application)
    httpd.serve_forever()