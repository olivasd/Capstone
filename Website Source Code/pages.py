import json
import gviz_api
import MySQLdb

def connect_db():
  db=MySQLdb.connect(host="aafd5d0dbwwprl.cz0r3iyamhjr.us-east-2.rds.amazonaws.com", 
          port=3306, 
          user="wipuser", 
          passwd="PolloLoco007!", 
          db="ebdb")
  return db

def test(months):
	page_template = """
	<html>
	  <script src="https://www.google.com/jsapi" type="text/javascript"></script>
	  <script>
	      google.load('visualization', '1', {packages:['corechart']});
	      google.setOnLoadCallback(drawChart);
	      google.load('visualization', '1', {packages:['table']});
	      google.setOnLoadCallback(drawTable);

	      function drawChart() {
	      %(chart_data)s
	      var chart = new google.visualization.PieChart(document.getElementById('chart_div'));
	      var options = {'title': 'Awards',
	      	'width': 600, 'height': 450};
	      chart.draw(award_data, options);
	      }

	      function drawTable() {
	      %(table_data)s
	      var table = new google.visualization.Table(document.getElementById('table_div'));
	      var options = {'width': 300, 'height': 100};
	      table.draw(award_data, options)
	      }
	    </script>
	    <body>
	      <div id="chart_div" align="center"></div>
	      <div id="table_div" align="center"></div>
	    </body>
	</html>
	"""

	award_description = {"name": ("string", "Award"), "amount": ("number", "Total")}

	db = connect_db()
	cur = db.cursor()

	if months == '13':
		query = '''SELECT tbl_Award_Types.award_name, COUNT(*) 
		FROM tbl_Award 
		INNER JOIN tbl_Award_Types ON tbl_Award.type_id = tbl_Award_Types.award_id 
	    GROUP BY tbl_Award.id'''
	else:
		query = '''
		SELECT tbl_Award_Types.award_name, COUNT(*) 
		FROM tbl_Award 
		INNER JOIN tbl_Award_Types ON tbl_Award.type_id = tbl_Award_Types.award_id 
		WHERE tbl_Award.date_awarded >= now()-interval %(months)s month
	    GROUP BY tbl_Award.id'''

	time = {"months": months}
	cur.execute(query % time)
	results = cur.fetchall()

	db.close()

	awards_data = [{"name": "Employee of the Week", "amount": 0}, {"name": "Employee of the Month", "amount": 0}, {"name": "Best Hat", "amount": 0}]

	for row in results:
		temp = {}
		if row[0] == "Employee of the Week":
			awards_data[0]["amount"] += row[1]
		elif row[0] == "Employee of the Month":
			awards_data[1]["amount"] += row[1]
		elif row[0] == "Best Hat":
			awards_data[2]["amount"] += row[1]

	# Loading it into gviz_api.DataTable
	data_chart = gviz_api.DataTable(award_description)
	data_chart.LoadData(awards_data)
	# Create a JavaScript code string.
	chart_data = data_chart.ToJSCode("award_data",columns_order=("name", "amount"))

	# Loading it into gviz_api.DataTable
	data_table = gviz_api.DataTable(award_description)
	data_table.LoadData(awards_data)
	# Create a JavaScript code string.
	table_data = data_chart.ToJSCode("award_data",columns_order=("name", "amount"))

	  
	with open('templates/file.html', 'w') as outfile:
		outfile.write(page_template % vars())

def last_year():
	page_template = """
		<html>
		  <script src="https://www.google.com/jsapi" type="text/javascript"></script>
		  <script>
		    google.load('visualization', '1', {packages:['corechart', 'bar']});
		    google.setOnLoadCallback(drawColColors);

		    function drawColColors() {
		    var data = google.visualization.arrayToDataTable([
		    %(master)s
			]);
		      var jscode_table = new google.visualization.ColumnChart(document.getElementById('chart_div'));
		      var options = {
		        width: 1200,
		        height: 500}
		      jscode_table.draw(data, options);
			}
		  </script>
		  <body>
		    <div align="center"><H2>Awards in the Last Year</H2></div>
		    <div id="chart_div"></div>
		  </body>
		</html>
		"""
	db = connect_db()
	cur = db.cursor()
	 
	query = '''SELECT tbl_Award.date_awarded, tbl_Award_Types.award_name FROM tbl_Award
	          JOIN tbl_Award_Types ON tbl_Award.type_id = tbl_Award_Types.award_id
	          WHERE tbl_Award.date_awarded >= now()-interval 12 month
	          order by MONTH(tbl_Award.date_awarded)'''

	cur.execute(query)
	results = cur.fetchall()

	db.close()

	months = [["month", "Employee of the Month", "Employee of the Week", "Best Hat"],
			  ["January",0 ,0 ,0], ["February",0 ,0 ,0], ["March",0 ,0 ,0], ["April",0 ,0 ,0],
	          ["May",0 ,0 ,0], ["June",0 ,0 ,0], ["July",0 ,0 ,0], ["August",0 ,0 ,0],
	          ["September",0 ,0 ,0], ["October",0 ,0 ,0], ["November",0 ,0 ,0], ["December",0 ,0 ,0]]

	for row in results:
		date = row[0].month
		if row[1] == "Employee of the Month":
	 		months[date][1] += 1
		elif row[1] == "Employee of the Week":
			months[date][2] += 1
		elif row[1] == "Best Hat":
	 		months[date][3] += 1
	master = ""
	for row in months:
		master += str(row) + ", "
	stuff = {"master": master}

	with open('templates/file.html', 'w') as outfile:
		outfile.write(page_template % stuff)


def user_given(months):
	page_template = """
	<html>
	  <script src="https://www.google.com/jsapi" type="text/javascript"></script>
	  <script>
	      google.load('visualization', '1', {packages:['corechart']});
	      google.setOnLoadCallback(drawChart);
	      google.load('visualization', '1', {packages:['table']});
	      google.setOnLoadCallback(drawTable);

	      function drawChart() {
	      %(chart_data)s
	      var chart = new google.visualization.PieChart(document.getElementById('chart_div'));
	      var options = {'title': 'Awards Given By User',
	                    'width': 600, 'height': 450};
	      chart.draw(award_data, options);
	      }
	      function drawTable() {
	      %(table_data)s
	      var table = new google.visualization.Table(document.getElementById('table_div'));
	      table.draw(user_data)
	      }
	    </script>
	    <body>
	      <div id="chart_div" align="center"></div>
	      <div id="table_div" align="center"></div>
	    </body>
	</html>
	"""

	award_description = {"name": ("string", "Award"), "amount": ("number", "Amount")}
  
	db = connect_db()
	cur = db.cursor()
	time = {"months": months}
	if months == '13':
		query = '''
		SELECT tbl_User.id, tbl_User.firstname, tbl_User.lastname, COUNT(*)
		FROM tbl_Award
		JOIN tbl_User ON tbl_Award.nominator_id = tbl_User.id
		JOIN tbl_Award_Types ON tbl_Award.type_id = tbl_Award_Types.award_id
		GROUP BY tbl_User.id'''
	else:
		query = '''
		SELECT tbl_User.id, tbl_User.firstname, tbl_User.lastname, COUNT(*)
		FROM tbl_Award
		JOIN tbl_User ON tbl_Award.nominator_id = tbl_User.id
		JOIN tbl_Award_Types ON tbl_Award.type_id = tbl_Award_Types.award_id
		WHERE tbl_Award.date_awarded >= now()-interval %(months)s month
		GROUP BY tbl_User.id'''

   
	cur.execute(query % time)
	results = cur.fetchall()

	db.close()

	awards_data = []

	for row in results:
		temp = {}
		temp["amount"] = row[3]
		temp["name"] = row[1] + " " + row[2]
		awards_data.append(temp)
		del temp

	db = connect_db()
	cur = db.cursor()
	if months == '13':
		query = '''
		SELECT tbl_User.id, tbl_User.firstname, tbl_User.lastname, tbl_Award_Types.award_name
		FROM tbl_User
		JOIN tbl_Award ON tbl_User.id = tbl_Award.nominator_id
		JOIN tbl_Award_Types ON tbl_Award.type_id = tbl_Award_Types.award_id
		ORDER BY tbl_User.id'''
	else:
		query = '''
		SELECT tbl_User.id, tbl_User.firstname, tbl_User.lastname, tbl_Award_Types.award_name
		FROM tbl_User
		JOIN tbl_Award ON tbl_User.id = tbl_Award.nominator_id
		JOIN tbl_Award_Types ON tbl_Award.type_id = tbl_Award_Types.award_id
		WHERE tbl_Award.date_awarded >= now()-interval %(months)s month
        ORDER BY tbl_User.id'''

	cur.execute(query % time)
	results = cur.fetchall()

	db.close()

	id_list = []
	working_data = []
	counter = -1
	user_data = []

	for rows in results:
		if rows[0] not in id_list:
			id_list.append(rows[0])
			temp = {'name': rows[1] + ' ' + rows[2], "Employee of the Week": 0, "Employee of the Month": 0, "Best Hat": 0, "Total": 0}
			another_temp = {}
			another_temp['id'] = rows[0]
			another_temp[rows[0]] = temp
			working_data.append(another_temp)
			del temp, another_temp
			counter += 1
			working_data[counter][id_list[counter]][rows[3]] += 1
			working_data[counter][id_list[counter]]["Total"] += 1
		else:
			working_data[counter][id_list[counter]][rows[3]] += 1
			working_data[counter][id_list[counter]]["Total"] += 1

	new_counter = 0
	for stuff in id_list:
		temp = working_data[new_counter][stuff]
		new_counter += 1
		user_data.append(temp)
		del temp

	user_description = {"name": ("string", "User"), "Employee of the Month": ("number", "Employee of the Month"),
                      "Employee of the Week": ("number", "Employee of the Week"), "Best Hat": ("number", "Best Hat"), "Total": ("number", "Total")}
  
	# Loading it into gviz_api.DataTable
	data_chart = gviz_api.DataTable(award_description)
	data_chart.LoadData(awards_data)
	# Create a JavaScript code string.
	chart_data = data_chart.ToJSCode("award_data",columns_order=("name", "amount"))


	# Loading it into gviz_api.DataTable
	data_table = gviz_api.DataTable(user_description)
	data_table.LoadData(user_data)
	# Create a JavaScript code string.
	table_data = data_table.ToJSCode("user_data",
                               columns_order=("name", "Employee of the Month", "Employee of the Week", "Best Hat", "Total"))
  
	with open('templates/file.html', 'w') as outfile:
		outfile.write(page_template % vars())

def user_received(months):
	page_template = """
	<html>
	  <script src="https://www.google.com/jsapi" type="text/javascript"></script>
	  <script>
	      google.load('visualization', '1', {packages:['corechart']});
	      google.setOnLoadCallback(drawChart);
	      google.load('visualization', '1', {packages:['table']});
	      google.setOnLoadCallback(drawTable);

	      function drawChart() {
	      %(chart_data)s
	      var chart = new google.visualization.PieChart(document.getElementById('chart_div'));
	      var options = {'title': 'Awards Received By User',
	                    'width': 600, 'height': 450};
	      chart.draw(award_data, options);
	      }
	      function drawTable() {
	      %(table_data)s
	      var table = new google.visualization.Table(document.getElementById('table_div'));
	      table.draw(user_data)
	      }
	    </script>
	    <body>
	      <div id="chart_div"></div>
	      <div id="table_div"></div>
	    </body>
	</html>
	"""

	award_description = {"name": ("string", "Award"), "amount": ("number", "Amount")}
  
	db = connect_db()
	cur = db.cursor()
	time = {"months": months}
	if months == '13':
		query = '''
		SELECT tbl_User.id, tbl_User.firstname, tbl_User.lastname, COUNT(*)
		FROM tbl_Award
		JOIN tbl_User ON tbl_Award.nominee_id = tbl_User.id
		JOIN tbl_Award_Types ON tbl_Award.type_id = tbl_Award_Types.award_id
		GROUP BY tbl_User.id'''
	else:
		query = '''
		SELECT tbl_User.id, tbl_User.firstname, tbl_User.lastname, COUNT(*)
		FROM tbl_Award
		JOIN tbl_User ON tbl_Award.nominee_id = tbl_User.id
		JOIN tbl_Award_Types ON tbl_Award.type_id = tbl_Award_Types.award_id
		WHERE tbl_Award.date_awarded >= now()-interval %(months)s month
		GROUP BY tbl_User.id'''

   
	cur.execute(query % time)
	results = cur.fetchall()

	db.close()

	awards_data = []

	for row in results:
		temp = {}
		temp["amount"] = row[3]
		temp["name"] = row[1] + " " + row[2]
		awards_data.append(temp)
		del temp

	db = connect_db()
	cur = db.cursor()
	if months == '13':
		query = '''
		SELECT tbl_User.id, tbl_User.firstname, tbl_User.lastname, tbl_Award_Types.award_name
		FROM tbl_User
		JOIN tbl_Award ON tbl_User.id = tbl_Award.nominee_id
		JOIN tbl_Award_Types ON tbl_Award.type_id = tbl_Award_Types.award_id
		ORDER BY tbl_User.id'''
	else:
		query = '''
		SELECT tbl_User.id, tbl_User.firstname, tbl_User.lastname, tbl_Award_Types.award_name
		FROM tbl_User
		JOIN tbl_Award ON tbl_User.id = tbl_Award.nominee_id
		JOIN tbl_Award_Types ON tbl_Award.type_id = tbl_Award_Types.award_id
		WHERE tbl_Award.date_awarded >= now()-interval %(months)s month
        ORDER BY tbl_User.id'''

	cur.execute(query % time)
	results = cur.fetchall()

	db.close()

	id_list = []
	working_data = []
	counter = -1
	user_data = []

	for rows in results:
		if rows[0] not in id_list:
			id_list.append(rows[0])
			temp = {'name': rows[1] + ' ' + rows[2], "Employee of the Week": 0, "Employee of the Month": 0, "Best Hat": 0, "Total": 0}
			another_temp = {}
			another_temp['id'] = rows[0]
			another_temp[rows[0]] = temp
			working_data.append(another_temp)
			del temp, another_temp
			counter += 1
			working_data[counter][id_list[counter]][rows[3]] += 1
			working_data[counter][id_list[counter]]["Total"] += 1
		else:
			working_data[counter][id_list[counter]][rows[3]] += 1
			working_data[counter][id_list[counter]]["Total"] += 1

	new_counter = 0
	for stuff in id_list:
		temp = working_data[new_counter][stuff]
		new_counter += 1
		user_data.append(temp)
		del temp

	user_description = {"name": ("string", "User"), "Employee of the Month": ("number", "Employee of the Month"),
                      "Employee of the Week": ("number", "Employee of the Week"), "Best Hat": ("number", "Best Hat"), "Total": ("number", "Total")}
  
	# Loading it into gviz_api.DataTable
	data_chart = gviz_api.DataTable(award_description)
	data_chart.LoadData(awards_data)
	# Create a JavaScript code string.
	chart_data = data_chart.ToJSCode("award_data",columns_order=("name", "amount"))


	# Loading it into gviz_api.DataTable
	data_table = gviz_api.DataTable(user_description)
	data_table.LoadData(user_data)
	# Create a JavaScript code string.
	table_data = data_table.ToJSCode("user_data",
                               columns_order=("name", "Employee of the Month", "Employee of the Week", "Best Hat", "Total"))
  
	with open('templates/file.html', 'w') as outfile:
		outfile.write(page_template % vars())

def given_by_domain(months):
	page_template = """
	<html>
	  <script src="https://www.google.com/jsapi" type="text/javascript"></script>
	  <script>
	      google.load('visualization', '1', {packages:['corechart']});
	      google.setOnLoadCallback(drawChart);
	      google.load('visualization', '1', {packages:['table']});
	      google.setOnLoadCallback(drawTable);

	      function drawChart() {
	      %(chart_data)s
	      var chart = new google.visualization.PieChart(document.getElementById('chart_div'));
	      var options = {'title': 'Awards Given By Email Domain',
	                    'width': 600, 'height': 450};
	      chart.draw(award_data, options);
	      }
	      function drawTable() {
	      %(table_data)s
	      var table = new google.visualization.Table(document.getElementById('table_div'));
	      table.draw(user_data)
	      }
	    </script>
	    <body>
	      <div id="chart_div" align="center"></div>
	      <div id="table_div" align="center"></div>
	    </body>
	</html>
	"""

	award_description = {"name": ("string", "Award"), "amount": ("number", "Amount")}
	  
	db = connect_db()
	cur = db.cursor() 
	time = {"months": months}
	if months == '13':
		query = '''
		SELECT right(tbl_User.email, length(tbl_User.email)-INSTR(tbl_User.email, '@')), COUNT(*)
		FROM tbl_Award
		JOIN tbl_User ON tbl_Award.nominator_id = tbl_User.id
		JOIN tbl_Award_Types ON tbl_Award.type_id = tbl_Award_Types.award_id
		GROUP BY right(tbl_User.email, length(tbl_User.email)-INSTR(tbl_User.email, '@'))'''
	else:
		query = '''
		SELECT right(tbl_User.email, length(tbl_User.email)-INSTR(tbl_User.email, '@')), COUNT(*)
		FROM tbl_Award
		JOIN tbl_User ON tbl_Award.nominator_id = tbl_User.id
		JOIN tbl_Award_Types ON tbl_Award.type_id = tbl_Award_Types.award_id
		WHERE tbl_Award.date_awarded >= now()-interval 1 month
		GROUP BY right(tbl_User.email, length(tbl_User.email)-INSTR(tbl_User.email, '@'))'''

	   
	cur.execute(query % time)
	results = cur.fetchall()

	db.close()

	awards_data = []

	for row in results:
		temp = {}
		temp["amount"] = row[1]
		temp["name"] = row[0]
		awards_data.append(temp)
		del temp

	db = connect_db()
	cur = db.cursor()
	time = {"months": months}
	if months == '13':
		query = '''
		SELECT right(tbl_User.email, length(tbl_User.email)-INSTR(tbl_User.email, '@')), tbl_Award_Types.award_name
		FROM tbl_User
		JOIN tbl_Award ON tbl_User.id = tbl_Award.nominator_id
		JOIN tbl_Award_Types ON tbl_Award.type_id = tbl_Award_Types.award_id
		ORDER BY right(tbl_User.email, length(tbl_User.email)-INSTR(tbl_User.email, '@'))'''
	else:
		query = '''
		SELECT right(tbl_User.email, length(tbl_User.email)-INSTR(tbl_User.email, '@')), tbl_Award_Types.award_name
		FROM tbl_User
		JOIN tbl_Award ON tbl_User.id = tbl_Award.nominator_id
		JOIN tbl_Award_Types ON tbl_Award.type_id = tbl_Award_Types.award_id
		WHERE tbl_Award.date_awarded >= now()-interval %(months)s month
		ORDER BY right(tbl_User.email, length(tbl_User.email)-INSTR(tbl_User.email, '@'))'''

	cur.execute(query % time)
	results = cur.fetchall()

	db.close()

	id_list = []
	counter = -1
	user_data = []

	for rows in results:
		if rows[0] not in id_list:
			id_list.append(rows[0])
			temp = {"name": rows[0], "Employee of the Week": 0, "Employee of the Month": 0, "Best Hat": 0, "Total": 0}
			temp[rows[1]] += 1
			temp["Total"] += 1
			user_data.append(temp)
			del temp
			counter += 1
		else:
			user_data[counter][rows[1]] += 1
			user_data[counter]["Total"] += 1

	user_description = {"name": ("string", "User"), "Employee of the Month": ("number", "Employee of the Month"),
                      "Employee of the Week": ("number", "Employee of the Week"), "Best Hat": ("number", "Best Hat"), "Total": ("number", "Total")}
  
	# Loading it into gviz_api.DataTable
	data_chart = gviz_api.DataTable(award_description)
	data_chart.LoadData(awards_data)
	# Create a JavaScript code string.
	chart_data = data_chart.ToJSCode("award_data",columns_order=("name", "amount"))


	# Loading it into gviz_api.DataTable
	data_table = gviz_api.DataTable(user_description)
	data_table.LoadData(user_data)
	# Create a JavaScript code string.
	table_data = data_table.ToJSCode("user_data",
                               columns_order=("name", "Employee of the Month", "Employee of the Week", "Best Hat", "Total"))
  
	with open('templates/file.html', 'w') as outfile:
		outfile.write(page_template % vars())

def received_by_domain(months):
	page_template = """
	<html>
	  <script src="https://www.google.com/jsapi" type="text/javascript"></script>
	  <script>
	      google.load('visualization', '1', {packages:['corechart']});
	      google.setOnLoadCallback(drawChart);
	      google.load('visualization', '1', {packages:['table']});
	      google.setOnLoadCallback(drawTable);

	      function drawChart() {
	      %(chart_data)s
	      var chart = new google.visualization.PieChart(document.getElementById('chart_div'));
	      var options = {'title': 'Received By Email Domain',
	                    'width': 600, 'height': 450};
	      chart.draw(award_data, options);
	      }
	      function drawTable() {
	      %(table_data)s
	      var table = new google.visualization.Table(document.getElementById('table_div'));
	      table.draw(user_data)
	      }
	    </script>
	    <body>
	      <div id="chart_div" align="center"></div>
	      <div id="table_div" align="center"></div>
	    </body>
	</html>
	"""

	award_description = {"name": ("string", "Award"), "amount": ("number", "Amount")}
	  
	db = connect_db()
	cur = db.cursor() 
	time = {"months": months}
	if months == '13':
		query = '''
		SELECT right(tbl_User.email, length(tbl_User.email)-INSTR(tbl_User.email, '@')), COUNT(*)
		FROM tbl_Award
		JOIN tbl_User ON tbl_Award.nominee_id = tbl_User.id
		JOIN tbl_Award_Types ON tbl_Award.type_id = tbl_Award_Types.award_id
		GROUP BY right(tbl_User.email, length(tbl_User.email)-INSTR(tbl_User.email, '@'))'''
	else:
		query = '''
		SELECT right(tbl_User.email, length(tbl_User.email)-INSTR(tbl_User.email, '@')), COUNT(*)
		FROM tbl_Award
		JOIN tbl_User ON tbl_Award.nominee_id = tbl_User.id
		JOIN tbl_Award_Types ON tbl_Award.type_id = tbl_Award_Types.award_id
		WHERE tbl_Award.date_awarded >= now()-interval 1 month
		GROUP BY right(tbl_User.email, length(tbl_User.email)-INSTR(tbl_User.email, '@'))'''

	   
	cur.execute(query % time)
	results = cur.fetchall()

	db.close()

	awards_data = []

	for row in results:
		temp = {}
		temp["amount"] = row[1]
		temp["name"] = row[0]
		awards_data.append(temp)
		del temp

	db = connect_db()
	cur = db.cursor()
	time = {"months": months}
	if months == '13':
		query = '''
		SELECT right(tbl_User.email, length(tbl_User.email)-INSTR(tbl_User.email, '@')), tbl_Award_Types.award_name
		FROM tbl_User
		JOIN tbl_Award ON tbl_User.id = tbl_Award.nominee_id
		JOIN tbl_Award_Types ON tbl_Award.type_id = tbl_Award_Types.award_id
		ORDER BY right(tbl_User.email, length(tbl_User.email)-INSTR(tbl_User.email, '@'))'''
	else:
		query = '''
		SELECT right(tbl_User.email, length(tbl_User.email)-INSTR(tbl_User.email, '@')), tbl_Award_Types.award_name
		FROM tbl_User
		JOIN tbl_Award ON tbl_User.id = tbl_Award.nominee_id
		JOIN tbl_Award_Types ON tbl_Award.type_id = tbl_Award_Types.award_id
		WHERE tbl_Award.date_awarded >= now()-interval %(months)s month
		ORDER BY right(tbl_User.email, length(tbl_User.email)-INSTR(tbl_User.email, '@'))'''

	cur.execute(query % time)
	results = cur.fetchall()

	db.close()

	id_list = []
	counter = -1
	user_data = []

	for rows in results:
		if rows[0] not in id_list:
			id_list.append(rows[0])
			temp = {"name": rows[0], "Employee of the Week": 0, "Employee of the Month": 0, "Best Hat": 0, "Total": 0}
			temp[rows[1]] += 1
			temp["Total"] += 1
			user_data.append(temp)
			del temp
			counter += 1
		else:
			user_data[counter][rows[1]] += 1
			user_data[counter]["Total"] += 1

	user_description = {"name": ("string", "User"), "Employee of the Month": ("number", "Employee of the Month"),
                      "Employee of the Week": ("number", "Employee of the Week"), "Best Hat": ("number", "Best Hat"), "Total": ("number", "Total")}
  
	# Loading it into gviz_api.DataTable
	data_chart = gviz_api.DataTable(award_description)
	data_chart.LoadData(awards_data)
	# Create a JavaScript code string.
	chart_data = data_chart.ToJSCode("award_data",columns_order=("name", "amount"))


	# Loading it into gviz_api.DataTable
	data_table = gviz_api.DataTable(user_description)
	data_table.LoadData(user_data)
	# Create a JavaScript code string.
	table_data = data_table.ToJSCode("user_data",
                               columns_order=("name", "Employee of the Month", "Employee of the Week", "Best Hat", "Total"))
  
	with open('templates/file.html', 'w') as outfile:
		outfile.write(page_template % vars())

#https://developers.google.com/chart/interactive/docs/dev/gviz_api_lib
#https://stackoverflow.com/questions/2628138/how-to-select-domain-name-from-email-address
