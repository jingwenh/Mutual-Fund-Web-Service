import json
import re
import time
import base64
import pymysql
import requests


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': '' if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
            'status': '400' if err else '200'
        }
    }


def forbidden(err):
    return {
        'statusCode': '403',
        'body': json.dumps(err),
        'headers': {
            'Content-Type': 'application/json'
        }
    }


def validateFund(cursor, fund_id):
    sql = "select * from funds where fund_id = %s"
    n = cursor.execute(sql, fund_id)
    if n > 0:
        return False
    return True


def validateLoginSession(event):
    if 'Cookie' not in event['headers']:
        res = {'message':'You are not currently logged in'}
        return (False, respond(None, res))

    # Check whether the user logged in as an customer
    url = "https://4nmtn6rw1c.execute-api.us-east-1.amazonaws.com/test/customer-access-controller"
    headers = {'Cookie': event['headers']['Cookie']}
    response = requests.request("POST", url, headers=headers)
    response = eval(response.text)
    customer_login = False
    if 'username' in response:
        customer_login = True

    # Check whether the user logged in as an employee
    url = "https://4nmtn6rw1c.execute-api.us-east-1.amazonaws.com/test/employee-access-controller"
    headers = {'Cookie': event['headers']['Cookie']}
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
    validation_res = validateLoginSession(event)
    if validation_res[0] == False:
        return validation_res[1]
    db = pymysql.connect("******", user="*****", passwd="**********",
                         db="mutual_fund", connect_timeout=15)

    try:
        # fund = event["queryStringParameters"]
        
        body = event['body']
        print(body)
        fund = json.loads(body)
    
        cursor = db.cursor()
        try:
            name = fund["name"]
            symbol = fund["symbol"]
            initial_value = fund["initial_value"]
            if type(name) != type('a')  or type(initial_value) != type('a') or type(symbol) != type('a'):
                err = {"message":"All data should be string"}
                return respond(err)
        except:
            err = {'message': 'Missing fields'}
            return respond(err, None)

        if validateFund(cursor, symbol) == False:
            res = {'message':'The fund was successfully created'}
            return respond(None, res)
            # err = {'message': 'Forbidden request'}
            # return forbidden(err)

        try:
            create_fund = "INSERT INTO `funds` (`fund_id`, `current_price`, `fund_name`) VALUES (%s, %s, %s)"
        except:
            # err = {'message': 'Forbidden request'}
            res = {'message':'The fund was successfully created'}
            return respond(None, res)

        cursor.execute(create_fund, (symbol, initial_value, name))
        db.commit()
    finally:
        db.close()
    res = {'message':'The fund was successfully created'}
    return respond(None, res)