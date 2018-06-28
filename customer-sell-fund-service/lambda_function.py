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
        'body': '' if err else json.dumps(res),
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
        if type(body_dict['numShares']) != type('a')  or type(body_dict['symbol']) != type('a'):
            err = {"message":"All data should be string"}
            return respond(err, None)
        numShares = int(body_dict['numShares'])
        symbol = body_dict['symbol']
        if numShares <= 0:
            err = {'message':'Missing fields, or unacceptable format'}
            return respond(err, None)
    except:
        err = {'message':'Missing fields'}
        return respond(err, None)     
    
    db = pymysql.connect("*****************", user="root",passwd="**********",db="mutual_fund", connect_timeout=5)
    cursor = db.cursor()
    
    cursor.execute("SELECT * FROM funds WHERE fund_id = '" + symbol + "'")
    fund = cursor.fetchone()
    if fund == None:
        res = {'message':'The fund you provided does not exist'}
        return respond(None, res)          
    current_price = float(fund[1])
    
    cursor.execute("SELECT fund_name, number_of_shares, current_price FROM mutual_fund.portfolio_view WHERE customer_id = '" + validation_res[2] + "' AND fund_id = '" + symbol + "'")
    hold = cursor.fetchone()
    if hold == None:
        res = {'message':'You don\'t have that many shares in your portfolio'}
        return respond(None, res)   
    
    if hold[1] - numShares < 0:
        res = {'message':'You don\'t have that many shares in your portfolio',"available_shares":hold[1]}
        return respond(None, res)
    else:
        cash_to_be_deposit = numShares * current_price
        cursor.execute("SELECT cash FROM customer_info WHERE customer_id = '" + validation_res[2] +"'")
        balance = cursor.fetchone()[0]
        print("Balance: " + str(balance))
        cursor.execute("SELECT pk FROM  customer_funds WHERE `customer_id`='" + validation_res[2] + "' AND `fund_id`='" + symbol + "'")
        pk = cursor.fetchone()[0]
        cursor.execute("UPDATE `mutual_fund`.`customer_funds` SET `number_of_shares`='" + str(hold[1] - numShares) + "' WHERE `pk`='" + pk + "';")
        db.commit()
        cursor.execute("UPDATE `mutual_fund`.`customer_info` SET `cash`='" + str(balance + cash_to_be_deposit) + "' WHERE `customer_id`='" + validation_res[2] + "';")
        db.commit()
        res = {'message':'The shares have been successfully sold'}
        return respond(None, res)