import requests
import json


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': json.dumps(err) if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json'
        },
    }


def logged_in_as_employee(event):
    if 'Cookie' not in event['headers']:
        res = {'message': 'You are not currently logged in'}
        return False, respond(None, res)

    # Check whether the user logged in as an customer
    url = "https://4nmtn6rw1c.execute-api.us-east-1.amazonaws.com/test/customer-access-controller"
    headers = {'Cookie': event['headers']['Cookie']}
    response = requests.request("POST", url, headers=headers)
    response = eval(response.text)
    print(response)
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

    if not employee_login and not customer_login:
        res = {'message': 'You are not currently logged in'}
        return False, respond(None, res), None

    if customer_login and not employee_login:
        res = {'message': 'You must be an employee to perform this action'}
        return False, respond(None, res), None

    return True, None, response['username']


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': json.dumps(err) if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json'
        },
    }

