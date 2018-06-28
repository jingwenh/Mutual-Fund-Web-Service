import json
import re
import time
import base64
import pymysql
import requests

    
def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': json.dumps(json.loads(json.dumps(err) if err else json.dumps(res))),
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
    validation_res = validateLoginSession(event)
    if validation_res[0] == False:
        return validation_res[1]
    db = pymysql.connect("****", user="****",passwd="**********",db="mutual_fund", connect_timeout=5)
    cursor = db.cursor()
    sql = "SELECT fund_name, number_of_shares, current_price FROM mutual_fund.portfolio_view WHERE customer_id = '" + validation_res[2] + "'"
    print(sql)
    cursor.execute(sql)
    results = cursor.fetchall()
    print(results)
    if results == None or len(results) == 0:
        res = {'message':'You don’t have any funds in your Portfolio'}
        return respond(None, res)       
    portfolio = []
    for name, shares, price in results:
        fund = {
            "name":"",
            "shares":"",
            "price":"",
        }        
        fund["name"] = name
        fund["shares"] = str(shares)
        fund["price"] = str(price)
        portfolio.append(fund)
    print(portfolio)
    
    cursor.execute("SELECT cash FROM customer_info WHERE customer_id = '" + validation_res[2] + "'")
    cash = str(cursor.fetchone()[0])
    res = {'message':'The action was successful', 'cash':cash, 'funds':portfolio}
    return respond(None, res)   