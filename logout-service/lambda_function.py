import json
import requests

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': json.dumps(err) if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
            'Set-cookie':'Auth=reset',
        },
    }

def lambda_handler(event, context):
    print(event)
    if 'Cookie' not in event['headers']:
        res = {'message':'You are not currently logged in'}
        return respond(None, res)
    
    url = "https://4nmtn6rw1c.execute-api.us-east-1.amazonaws.com/test/customer-access-controller"
    headers= {'Cookie':event['headers']['Cookie']}
    response = requests.request("POST", url, headers=headers)
    response1 = eval(response.text)
    print(response1)
    
    url = "https://4nmtn6rw1c.execute-api.us-east-1.amazonaws.com/test/employee-access-controller"
    headers= {'Cookie':event['headers']['Cookie']}
    response = requests.request("POST", url, headers=headers)
    response2 = eval(response.text)
    print(response2)   
    
    if 'username' not in response1 and 'username' not in response2:
        res = {'message':'You are not currently logged in'}
        return respond(None, res)
    else:
        res = {'message':'You have been successfully logged out'}
        return respond(None, res)

# lambda_handler(s)
