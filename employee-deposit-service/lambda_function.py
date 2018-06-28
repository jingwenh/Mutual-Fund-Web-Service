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
            'Content-Type': 'application/json'
        },
    }
    
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
    validation_res = validateLoginSession(event)
    if validation_res[0] == False:
        return validation_res[1]
    
    try:
        # cash_to_be_deposit = float(event["queryStringParameters"]['cash'])
        # username = event["queryStringParameters"]['username']
        body = event['body']
        body_dic = json.loads(body)
        cash = body_dic['cash']
        username = body_dic['username']
        if type(username) != type('a')  or type(cash) != type('a'):
            err = {"message":"All data should be string"}
            return respond(err, None)
        cash_to_be_deposit = float(cash)
        if cash_to_be_deposit <= 0:
            err = {'message':'Missing fields, or unacceptable format'}
            return respond(err, None)
    except:
        err = {'message':'Missing fields, or unacceptable format'}
        return respond(err, None)     
    
    db = pymysql.connect("****", user="****",passwd="**********",db="mutual_fund", connect_timeout=5)
    cursor = db.cursor()
    
    cursor.execute("SELECT cash FROM customer_info WHERE customer_id = '" + username + "'")
    result = cursor.fetchone()
    if result == None:
        res = {'message':'The user does not exist'}
        return respond(None, res)        
    cash = float(result[0])
    
    cursor.execute("UPDATE `mutual_fund`.`customer_info` SET `cash`='" + str(cash + cash_to_be_deposit) + "' WHERE `customer_id`='" + username + "';")
    db.commit()
    
    res = {'message':'The check was successfully deposited'}
    return respond(None, res)