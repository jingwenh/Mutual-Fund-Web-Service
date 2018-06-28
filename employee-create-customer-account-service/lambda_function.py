import json
import pymysql
import requests

def respond(err, res=None):
    statusCode = '400' if err else '200'
    if err and 'code' in err:
        return {
            'statusCode': err['code']
        }
    body = json.dumps(err) if err else json.dumps(res)
    return {
        'statusCode': statusCode,
        'body': body,
        'headers': {
            'Content-Type': 'application/json'
        },
    }

def validateUser(username):
    db = pymysql.connect("****", user="****",passwd="**********",db="mutual_fund", connect_timeout=5)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM customer_credential WHERE customer_id = '" + username + "'")
    result = cursor.fetchone()
    if result == None:
        return None
    print(result)
    return result
    
def validateLoginSession(event):
    if 'Cookie' not in event['headers']:
        res = {'message':'You are not currently logged in'}
        return (False, respond(None, res))
    
    # Check whether the user logged in as an customer
    url = "https://4nmtn6rw1c.execute-api.us-east-1.amazonaws.com/test/customer-access-controller"
    headers= {'Cookie':event['headers']['Cookie']}
    response = requests.request("POST", url, headers=headers)
    response = eval(response.text)
    customer_login = False
    if 'username' in response:
        customer_login = True
        
    # Check whether the user logged in as an employee
    url = "https://4nmtn6rw1c.execute-api.us-east-1.amazonaws.com/test/employee-access-controller"
    headers= {'Cookie':event['headers']['Cookie']}
    response = requests.request("POST", url, headers=headers)
    response = eval(response.text)
    employee_login = False
    if 'username' in response:
        employee_login = True

    if employee_login == False and customer_login == True:
        res = {'message':'You must be an employee to perform this action'}
        return (False, respond(None, res), None)
    if employee_login == False:
        res = {'message':'You are not currently logged in'}
        return (False, respond(None, res), None)        
    return (True, None, response['username'])      

def lambda_handler(event, context):
    print(event)
    # Handle not logged in and not employee cases
    validation_res = validateLoginSession(event)
    if validation_res[0] == False:
        return validation_res[1]
    
    body_str = event['body']
    print(body_str)
    body_dict = json.loads(body_str)
    new_customer = body_dict
    
    # Missing required fields
    fields = ['fname', 'lname', 'address', 'city', 'state', 'zip', 'email', 'username', 'password']
    input_fields = new_customer.keys()
    for field in fields:
        if field not in input_fields:
            err = {"code": "400"}
            print("Missing required field %s" % field)
            return respond(err) 
    
    
    if 'cash' not in input_fields:
        if len(input_fields) != 9:
            err = {"code": "400"}
            print("input length == 10 but cash does not appear")
            return respond(err) 
        else:
            new_customer['cash'] = '0'
    
    # Empty input and type of input
    for key, value in new_customer.items():
        if type(value) != type('a'):
            err = {'code':'400'}
            print("Input %s is not a string" % key)
            return respond(err)
        if len(value) == 0:
            if key != 'cash': 
                err = {'code':'400'}
                print("Input %s's length is 0" % key)
                return respond(err) 
            else:
                print("Input: cash is empty string")
                new_customer['cash'] = '0'
                
    # Validate cash format
    cash = new_customer['cash']
    if '.' in cash:
        # have decimal point
        numbers = cash.strip().split('.')
        # more than 1 decimal point
        if (len(numbers) != 2):
            print("more than 1 decimal point")
            err = {'code': '400'}
            return respond(err)
        else:
            if not numbers[0].isdigit() or not numbers[1].isdigit():
                print("One of two parts is not digits.")
                err = {'code' : '400'}
                return respond(err)
            elif len(numbers[1]) > 2:
                print("The decimal place is more than 2.")
                err = {'code' : '400'}
                return respond(err)
    else:            
        if not cash.isdigit():
            print("No decimal point and contain characters other than [0-9]")
            err = {'code' : '400'}
            return respond(err)
            
    # Validate cash value
    cash = float(cash)
    if cash < 0.0:
        print("Cash value is negative.")
        err = {'code' : '400'}
        return respond(err) 
    
    # Validate if the user name is duplicate
    customer_id = body_dict["username"]
    validate_user_res = validateUser(customer_id)
    if validate_user_res != None:
        res = {'message':'The input you provided is not valid'}
        return respond(None, res)
    
    # Create account
    passwd = new_customer["password"]
    
    # Connect to db
    db = pymysql.connect("*****", user="root",passwd="**********",db="mutual_fund", connect_timeout=5, charset='utf8')
    cursor = db.cursor()
    try:
        sql_cc = "INSERT INTO `customer_credential` (`customer_id`, `password`) VALUES (%s, %s)"
        cursor.execute(sql_cc, (customer_id, passwd))

        sql_ci = "INSERT INTO `customer_info` (`fname`, `lname`, `address`, `city`, `state`, `zip`, `email`, `cash`, `customer_id`) \
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql_ci, (new_customer["fname"], new_customer["lname"], new_customer["address"], new_customer["city"], \
                             new_customer["state"], new_customer["zip"], new_customer["email"], float(new_customer["cash"]), customer_id))
        # connection is not autocommit by default. So you must commit to save
        # your changes.
    except:
        db.rollback()
        db.close()
        err = {'code':'400'}
        return respond(err)
    db.commit()
    db.close()
        
    res = {'message':'' + new_customer["fname"] + ' was registered successfully'}
    return respond(None, res)   
