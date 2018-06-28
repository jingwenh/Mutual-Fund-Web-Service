import json
import re
import time
import base64
import pymysql
import requests
import datetime
import uuid

    
def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': '' if err else json.dumps(res).replace('\\', ''),
        'headers': {
            'Content-Type': 'application/json'
        },
    }
    
def validateLoginSession(event):
    if 'Cookie' not in event['headers']:
        res = {'message':'You are not currently logged in'}
        return (False, respond(None, res))
    
    # Check whether the user logged in as an employee
    url = "https://4nmtn6rw1c.execute-api.us-east-1.amazonaws.com/test/employee-access-controller"
    headers= {'Cookie':event['headers']['Cookie']}
    response = requests.request("POST", url, headers=headers)
    response = eval(response.text)
    employee_login = False
    if 'username' in response:
        employee_login = True
    
    # Check whether the user logged in as an customer
    url = "https://4nmtn6rw1c.execute-api.us-east-1.amazonaws.com/test/customer-access-controller"
    headers= {'Cookie':event['headers']['Cookie']}
    response = requests.request("POST", url, headers=headers)
    response = eval(response.text)
    print(response)
    customer_login = False
    if 'username' in response:
        customer_login = True
    
    
    if customer_login == False and employee_login == True:
        res = {'message':'You must be a customer to perform this action'}
        return (False, respond(None, res), None)
    if customer_login == False:
        res = {'message':'You are not currently logged in'}
        return (False, respond(None, res), None)        
    return (True, None, response['username'])    

def lambda_handler(event, context):
    print(event)
    validation_res = validateLoginSession(event)
    if validation_res[0] == False:
        return validation_res[1]
    
    body_str = event['body']
    body_dict = json.loads(body_str)
    
    try:
        if type(body_dict['cashValue']) != type('a'):
            err = {"message":"All data should be string"}
            return respond(err, None)
        cash_to_be_withdraw = float(body_dict['cashValue'])
        if cash_to_be_withdraw <= 0:
            err = {'message':'Missing fields, or unacceptable format'}
            return respond(err, None)
    except:
        err = {'message':'Missing fields'}
        return respond(err, None)     
    
    db = pymysql.connect("****", user="****",passwd="**********",db="mutual_fund", connect_timeout=5)
    cursor = db.cursor()
    cursor.execute("SELECT cash FROM customer_info WHERE customer_id = '" + validation_res[2] +"'")
    balance = cursor.fetchone()[0]
    print("Balance: " + str(balance))
    
    if balance - cash_to_be_withdraw < 0:
        res = {'message':"You don't have sufficient funds in your account to cover the requested check", 'available_balance':balance}
        return respond(None, res)
    else:
        cursor.execute("UPDATE `mutual_fund`.`customer_info` SET `cash`='" + str(balance - cash_to_be_withdraw) + "' WHERE `customer_id`='" + validation_res[2] + "';")
        db.commit()
        res = {'message':'The check has been successfully requested'}
        return respond(None, res)