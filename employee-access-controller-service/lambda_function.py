import json
import re
import time
import base64
import pymysql

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': json.dumps(err) if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json'
        },
    }

def validateUser(username):
    db = pymysql.connect("****", user="****",passwd="**********",db="mutual_fund", connect_timeout=5)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM employee_credential WHERE employee_id = '" + username + "'")
    result = cursor.fetchone()
    if result == None:
        return None
    print(result)
    return result

def lambda_handler(event, context):
    print(event)
    try:
        cookie = event['headers']['Cookie']
    except:
        err = {'message':'Missing fields'}
        return respond(err, None)
    cookies = cookie.split(";")
    pattern = 'Auth=(.*)'
    token = ''
    for s in cookies:
        if 'Auth' in s:
            token = s
    try:
        cipher = re.search(pattern, token).group(1)
        print(cipher)
        plain_text = base64.decodestring(cipher.encode()).decode()
        username = plain_text.split('/')[0]
        time_stamp = float(plain_text.split('/')[1])
    except:
        err = {'message':'Invalid token'}
        return respond(err, None)
    
    if validateUser(username) == None:
        print(username)
        err = {'message':'User does not exist'}
        return respond(err, None)        
    
    time_diff = float(time.time()) - time_stamp
    if time_diff > 900:
        err = {'message':'Your session already expired'}
        return respond(err, None)
        
    res = {'message':'Success', "username":username}
    return respond(None, res)    
# lambda_handler(s)
