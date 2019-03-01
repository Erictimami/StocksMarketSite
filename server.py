import json
from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import connectToMySQL
import re #means regex for regular expression. using to sort( adding a long string after the real password before hashing )
from flask_bcrypt import Bcrypt    #for salting and hashing the password    
import datetime as dt 
import csv
# import matplotlib
# from matplotlib import pyplot as plt 
# from matplotlib import style
# import pandas as pd
# import pandas_datareader.data as web       
import urllib3
import certifi
import time
# create a regular expression object that we can use run operations on
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

#opening the app using Flask
app = Flask(__name__)
bcrypt = Bcrypt(app) 
app.secret_key="dajlhayjsvsckjfk" #secret key for opening the session
# arr=['','','','','','','','','','', '','','','','', '','','','','']
# arr_value=['','','','','','','','','','', '','','','','', '','','','','']
arr=[['','','','','','','','','','', '','','','','', '','','','',''], ['','','','','','','','','','', '','','','','', '','','','',''], ['','','','','','','','','','', '','','','','', '','','','',''], ['','','','','','','','','','', '','','','','', '','','','',''], ['','','','','','','','','','', '','','','','', '','','','','']]
arr_value=[['','','','','','','','','','', '','','','','', '','','','',''], ['','','','','','','','','','', '','','','','', '','','','',''], ['','','','','','','','','','', '','','','','', '','','','',''], ['','','','','','','','','','', '','','','','', '','','','',''], ['','','','','','','','','','', '','','','','', '','','','','']]
# ticker_value='TSLA'
data_response = ''
arr_ticker=['AAPL', 'GOOGL', 'TSLA', 'FB', 'MSFT']
all_data=['','','','','']
total_data=arr_value=[['','','','','','','','','','', '','','','','', '','','','',''], ['','','','','','','','','','', '','','','','', '','','','',''], ['','','','','','','','','','', '','','','','', '','','','',''], ['','','','','','','','','','', '','','','','', '','','','',''], ['','','','','','','','','','', '','','','','', '','','','','']]



# def convert():
#     txt_file = r"aapl_2.txt"
#     csv_file = r"aapl_2.csv"

#     # use 'with' if the program isn't going to immediately terminate
#     # so you don't leave files open
#     # the 'b' is necessary on Windows
#     # it prevents \x1a, Ctrl-z, from ending the stream prematurely
#     # and also stops Python converting to / from different line terminators
#     # On other platforms, it has no effect
#     in_txt = csv.reader(open(txt_file, "rb"), delimiter = '\t')
#     out_csv = csv.writer(open(csv_file, 'wb'))
    # out_csv.writerows(in_txt)




# def built_graph():
#     df = pd.read_csv('AAPL_2.txt', parse_dates=True, index_col=0)
#     df.plot()
#     plt.show()
#     return True

def create_data(para, j):
    try:   
        file_line = para+'.txt'
        url_link = "https://api.intrinio.com/data_point?ticker=" +para+ "&item=last_price"
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        headers = urllib3.util.make_headers(basic_auth='ceff0be4b99c9a49244c55c81e99b954:04ab7e228191ad7621e14c18f229adc4')
        response = http.request('GET', url_link, headers=headers)
        data_stock=response.data
        data_response = json.loads(data_stock)
        print('data_response '*4, data_response)
        print('arr'*10, arr)
        for i in range(19):
            arr[j][i]=arr[j][i+1]
            arr_value[j][i]=arr_value[j][i+1]
        print('pass here  '*10)
        arr[j][19]= data_response
        arr_value[j][19] = data_response['value']
        print('arr_value '*5, arr_value)
        print('after'*5)
        print(data_response["value"])
        print(data_stock)  

        save_file = open(file_line, 'a')
        print("A"*50)
        save_file.write(str(data_response["value"])+'\n')
        save_file.close()
        print('sleeping'*10)
        return arr_value
    except:
        print('NO'*10)


@app.route('/log_off')
def log_off():
    session.clear()
    flash("You have been logged out", 'logged_out')
    return redirect('/login_registration')

# *****************************
from threading import Timer
t = None

def refresh():
    print("Refresh")
    for j in range(5):
        total_data=create_data(arr_ticker[j], j)
    print('total_data'*3, total_data)
    print('&'*50)
    # print('all data in session  '*2, session['all_data'])

    # session['arr_value']=create_data(ticker_value)
    global terminate
    t = Timer(20, refresh)
    t.daemon = True
    t.start()
# *****************************




@app.route('/')
def index(): 
    if data_response not in session:
        session['data_response'] = '' 
    refresh()
    return render_template("index.html")


@app.route('/process_registration', methods=['POST'])
def process_registration():
    
    if request.method != 'POST':
        return redirect('/login_registration')

    valid_form_ok = True
    # Let's add validation rules

    if (len(request.form['first_name']) <= 2) or (bool(re.search(r'\d', request.form['first_name'])) == True) :   #check if at least 2 characters and if only the letter by using REGEX
        flash("First name must contain at least two and contain only letters", 'first_name')
        valid_form_ok=False

    if (len(request.form['last_name']) <= 2) or (bool(re.search(r'\d', request.form['last_name'])) == True) :
        flash("Last name must contain at least two and contain only letters", 'last_name')
        valid_form_ok=False

    if not EMAIL_REGEX.match(request.form['email']):  #checking validation email
        flash("Invalid email address!", 'email')
        valid_form_ok=False
    else:
        mysql = connectToMySQL('stock_db')
        email_query = "SELECT * FROM users WHERE users.email LIKE %(new_email)s;"
        data = {"new_email": request.form['email']}
        if mysql.query_db(email_query,data):
            flash("This email is already used by another user", 'email')
            valid_form_ok=False

    if (len(request.form['password']) < 8) or (len(request.form['password']) > 15):
        flash("Password must contain a number, a capital letter, and be between 8-15 characters", 'password')
        valid_form_ok=False
    elif request.form['password'] != request.form['confirm_pw']:
        flash("Passwords must match", 'confirm_pw')
        valid_form_ok=False

    if valid_form_ok == False :
        if '_flashes' in session.keys():
            session['first_name'], session['last_name'], session['email'] = request.form['first_name'], request.form['last_name'], request.form['email']
            return redirect('/login_registration')
    else:
        # include some logic to validate user input before adding them to the database!
        # create the hash
        password_hash = bcrypt.generate_password_hash(request.form['password'])  
        print('=====================================================',password_hash)  
        # be sure you set up your database so it can store password hashes this long (60 characters)

        mysql = connectToMySQL('stock_db')
        insert_query = "INSERT INTO users (first_name, last_name, email, password, created_at) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s, now());"
        data = {
            "first_name": request.form['first_name'],
            "last_name": request.form['last_name'],
            "email": request.form['email'],
            "password": password_hash
            }
        id_new_user=mysql.query_db(insert_query, data)
        print(id_new_user)
        
        if ('logged' or 'id' or 'first_name') not in session:
            session['first_name']=request.form['first_name']
            session['logged']= True
            session['id']=id_new_user
        else:
            session['logged']= True
            session['id']=id_new_user
            session['first_name']=request.form['first_name']
        return redirect('/home')

@app.route('/process_login', methods=['POST'])
def process_loggin():

    if request.method != 'POST':
        return redirect('/login_registration')

    if not EMAIL_REGEX.match(request.form['email']):  #checking validation email
        flash("Email and/or password are INVALID!", 'login')
        return redirect('/login_registration')
    else:
        mysql = connectToMySQL('stock_db')
        query = "SELECT users.email, users.password, users.first_name, users.created_at, users.id FROM users WHERE users.email=%(new_email)s;"
        data = {"new_email": request.form['email'].strip().lower() }

        print('$$$$$$$$$$$$$$$$$$$$$$$$$$ new_email', data)
        result_data = mysql.query_db(query,data) 
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!result_data:', result_data)
        if not result_data:
            flash("Email and/or password are INVALID!", 'login') #this email never registered
            return redirect('/login_registration')
        elif bcrypt.check_password_hash(result_data[0]['password'], request.form['password']):
            # if we get True after checking the password, we may put the user id in session
            print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@', result_data)
            session['id'] = result_data[0]['id']
            session['logged']=True
            session['first_name']=result_data[0]['first_name']
            return redirect('/home')
    flash("Email and/or password are INVALID!", 'login')
    return redirect('/login_registration')


@app.route('/login_registration')
def login_registration():
    if ('logged' or 'id' or 'first_name') not in session:
        session['logged']=False
        session['id']=0
        session['first_name']=""
    elif session['logged']==None:
        flash("You have been logged out", 'logged_out')
    return render_template('login_registration.html')


@app.route('/home')
def home():  
    
    if session['logged']==False or request.method != "GET":
        return redirect('/login_registration')
    refresh()
    # the companies that user is following
    mysql = connectToMySQL('stock_db')
    query= "SELECT * FROM companies LEFT JOIN users_companies ON companies.id=users_companies.companies_id LEFT JOIN users ON users_companies.users_id=users.id WHERE users_companies.users_id = %(users_id)s;"
    data={
        'users_id': session['id']
    }
    result_me=mysql.query_db(query, data)
    print('+++++++++++++++result++++++++++++++++++++++', result_me)

    # get the id of the companies followed
    mysql = connectToMySQL('stock_db')
    query= "SELECT companies.id FROM companies LEFT JOIN users_companies ON companies.id=users_companies.companies_id LEFT JOIN users ON users_companies.users_id=users.id WHERE users_companies.users_id =%(users_id)s;"
    data={
        'users_id': session['id']
    }
    other=mysql.query_db(query, data)
    print('+++++++++++++++other++++++++++++++++++++++', other)

    # companies that are not followed by user for many scenario
    if len(other)==0:
        query= "SELECT * FROM companies;"
        result_other=mysql.query_db(query, data)

    if len(other)==1:
        query= "SELECT * FROM companies WHERE companies.id NOT IN (%(para_1)s);"
        data = {
            'para_1': other[0]['id']
        }
    if len(other)==2:
        query= "SELECT * FROM companies WHERE companies.id NOT IN (%(para_1)s, %(para_2)s );"
        data = {
            'para_1': other[0]['id'],
            'para_2': other[1]['id']
        }
    if len(other)==3:
        query= "SELECT * FROM companies WHERE companies.id NOT IN (%(para_1)s, %(para_2)s, %(para_3)s);"
        data = {
            'para_1': other[0]['id'],
            'para_2': other[1]['id'],
            'para_3': other[2]['id']
        }
    if len(other)==4:
        query= "SELECT * FROM companies WHERE companies.id NOT IN (%(para_1)s, %(para_2)s, %(para_3)s, %(para_4)s );"
        data = {
            'para_1': other[0]['id'],
            'para_2': other[1]['id'],
            'para_3': other[2]['id'],
            'para_4': other[3]['id']
        }
    mysql = connectToMySQL('stock_db')
    result_other=mysql.query_db(query, data)
    print('+++++++++++++++result_other++++++++++++++++++++++', result_other)

    # return render_template("home.html", result_me=result_me, result_other=result_other)
    return render_template("home.html", result_me=result_me, result_other=result_other, other_len=len(other), me_len=len(result_me), all_data=total_data)

@app.route('/graphs/<graph_id>')
def graphs(graph_id):  
    refresh()
    if session['logged'] != True:
        redirect('/login_registration')
    return render_template('my_graph.html')

@app.route('/other_graphs/<graph_id>')
def other_graphs(graph_id):  
    if session['logged'] != True:
        redirect('/login_registration')
    return render_template('other_graph.html')

@app.route('/history/<x>')
def user(x):  
    if session['logged'] != True:
        redirect('/login_registration')
    return render_template('history.html')

@app.route("/process_setting_graph/<graph_id>", methods=["POST"])
def process_setting_graph(graph_id):  
    if session['logged'] != True or request.method != 'POST':
        redirect('/login_registration')

    valid_form_ok = True
    # Let's add validation rules

    if (len(request.form['stock_min']) <= 2) or (bool(re.search(r'\d', request.form['stock_min'])) == True) :   #check if at least 2 characters and if only the letter by using REGEX
        flash("Must contain  only number with at least a digit", 'stock_min')
        valid_form_ok=False

    if (len(request.form['stock_max']) <= 2) or (bool(re.search(r'\d', request.form['stock_max'])) == True) :
        flash("Must contain  only number with at least a digit", 'stock_max')
        valid_form_ok=False

    if (len(request.form['speed_up']) <= 2) or (bool(re.search(r'\d', request.form['speed_up'])) == True) :
        flash("Must contain  only number with at least a digit", 'speed_up')
        valid_form_ok=False

    if (len(request.form['speed_down']) <= 2) or (bool(re.search(r'\d', request.form['speed_down'])) == True) :
        flash("Must contain  only number with at least a digit", 'speed_down')
        valid_form_ok=False

    if (len(request.form['stock_avg']) <= 2) or (bool(re.search(r'\d', request.form['stock_avg'])) == True) :
        flash("Must contain  only number with at least a digit", 'stock_avg')
        valid_form_ok=False


    if valid_form_ok == False :
        if '_flashes' in session.keys():
            session['stock_min'], session['stock_max'], session['speed_up'] = request.form['stock_min'], request.form['stock_max'], request.form['stock_min']
            session['speed_down'], session['stock_avg'] = request.form['speed_down'], request.form['stock_avg'] 
            return redirect('/my_graph/graph_id')
    else:
        # include some logic to validate user input before adding them to the database!
        # create the hash
        # be sure you set up your database so it can store password hashes this long (60 characters)

        # mysql = connectToMySQL('stock_db')
        # insert_query = "INSERT INTO users (first_name, last_name, email, password, created_at) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s, now());"
        # data = {
        #     "first_name": request.form['first_name'],
        #     "last_name": request.form['last_name'],
        #     "email": request.form['email'],
        #     "password": password_hash
        #     }
        # id_new_user=mysql.query_db(insert_query, data)
        # print(id_new_user)
        
        flash("Must contain  only number with at least a digit", "success")
        return redirect('/home')

@app.route('/remove_graph/<comp_id>')
def remove_graph(comp_id):  
    if session['logged'] != True:
        return redirect('/login_registration')
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    query = "DELETE FROM users_companies WHERE users_id=%(users_id)s AND companies_id=%(comp_id)s;"
    data = {
        'users_id': session['id'],
        'comp_id': comp_id
    }
    mysql = connectToMySQL('stock_db')
    mysql.query_db(query, data)
    return redirect('/home')

@app.route('/add_graph/<comp_id>')
def add_graph(comp_id):  
    if session['logged'] != True:
        return redirect('/login_registration')
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    query = "INSERT INTO users_companies (users_id, companies_id) VALUES (%(users_id)s, %(comp_id)s);"
    data = {
        'users_id': session['id'],
        'comp_id': comp_id
    }
    mysql = connectToMySQL('stock_db')
    mysql.query_db(query, data)
    return redirect('/home')



# def timer():
#     print("test"*1000)
#     global ticker_value
#     create_data(ticker_value)
#     session['data_response']=data_response
#     print("*"*50, "UPATED", "*"*50)
#     time.sleep(10)
#     timer()
# {"identifier":"FB","item":"last_price","value":149.19}



if __name__ == "__main__":
    app.run(debug = True)


# {
#     "data":[
#         {"date":"2018-10-24","value":19.4036},
#         {"date":"2018-10-23","value":19.5528},
#         {"date":"2018-10-22","value":19.3702},
#         {"date":"2018-10-19","value":19.2526},
#         {"date":"2018-10-18","value":18.9638},
#         {"date":"2018-10-17","value":19.4176},
#         {"date":"2018-10-16","value":19.5019},
#         {"date":"2018-10-15","value":19.0814},
#         {"date":"2018-10-12","value":19.4984},
#         {"date":"2018-10-11","value":18.8259},
#         {"date":"2018-10-10","value":18.9936},
#         {"date":"2018-10-09","value":19.9162},
#         {"date":"2018-10-08","value":19.6441},
#         {"date":"2018-10-05","value":19.6898},
#         {"date":"2018-10-04","value":20.0146},
#         {"date":"2018-10-03","value":20.3727},
#         {"date":"2018-10-02","value":20.1278},
#         {"date":"2018-10-01","value":19.9505}
#         ],
#     "identifier":"AAPL",
#     "item":"pricetoearnings",
#     "result_count":18,
#     "page_size":100,
#     "current_page":1,
#     "total_pages":1,
#     "api_call_credits":1
# }
