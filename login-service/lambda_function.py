import json
import time
import base64
import pymysql
import types

def respond(err, res=None, token=None):
    # print("Decode cipher:")
    # print(base64.decodestring(generateToken(username).encode()))
    return {
        'statusCode': '400' if err else '200',
        'body': json.dumps(err) if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json'
        },
    }

def respondEmployee(err, res=None, token=None):
    # print("Decode cipher:")
    # print(base64.decodestring(generateToken(username).encode()))
    return {
        'statusCode': '400' if err else '200',
        'body': json.dumps(err) if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
            'Set-Cookie':'Auth=' + token + '; HttpOnly'
        },
    }

def respondCustomer(err, res=None, token=None):
    # print("Decode cipher:")
    # print(base64.decodestring(generateToken(username).encode()))
    return {
        'statusCode': '400' if err else '200',
        'body': json.dumps(err) if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
            'Set-Cookie':'Auth=' + token + '; HttpOnly'
        },
    }

def errRespond(err):
    return {
        'statusCode': '400',
        'body': json.dumps(err),
        'headers': {
            'Content-Type': 'application/json'
        },
    }

def generateToken(username=None):
    start_time = time.time()
    plaintext = username + "/" + str(start_time)
    cipher = base64.encodestring(plaintext.encode())
    return cipher.decode().strip()

def validateCustomer(username, password):
    db = pymysql.connect("************", user="root",passwd="**********",db="mutual_fund", connect_timeout=5)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM customer_credential WHERE customer_id = '" + username + "'")
    result = cursor.fetchone()
    if result == None:
        return None
    if result[1] != password:
        return None
    cursor.execute("SELECT * FROM customer_info WHERE customer_id = '" + username + "'")
    result = cursor.fetchone()
    print(result)
    return result

def validateEmployee(username, password):
    db = pymysql.connect("ian.ckmruh9i5xcv.us-east-1.rds.amazonaws.com", user="root",passwd="**********",db="mutual_fund", connect_timeout=5)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM employee_credential WHERE employee_id = '" + username + "'")
    result = cursor.fetchone()
    if result == None:
        return False
    if result[1] != password:
        return False
    return True

def lambda_handler(event, context):
    print('Input event: ' + str(event))
    try:
    # username = event['queryStringParameters']['username']
    # password = event['queryStringParameters']['password']
        body = event['body']
        print(body)
        body_dic = json.loads(body)
        username = body_dic['username']
        password = body_dic['password']
        # print(type(username))
        # print(type(password))
        # print(type('a'))
        if type(username) != type('a')  or type(password) != type('a'):
            err = {"message":"All data should be string"}
            return errRespond(err)
        # print(type(password))
    except:
        err = {"message":"Missing fields"}
        return errRespond(err)     
    if validateEmployee(username, password):
        token = generateToken(username)
        message = 'Welcome Jane'
        res = {"message":message}
        return respondEmployee(None, res, token)
    result = validateCustomer(username, password)
    if result != None:
        token = generateToken(username)
        message = 'Welcome ' + result[6]
        res = {"message":message}
        return respondCustomer(None, res, token)    
    else:
        res = {'message':'There seems to be an issue with the username/password combination that you entered'}
        return respond(None, res, username)