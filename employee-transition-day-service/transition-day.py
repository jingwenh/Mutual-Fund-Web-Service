import random
import AuthUtils.auth as auth
from pony.orm import *

db = Database()
db_url = '*****************'
db.bind(provider='mysql', host=db_url, user='root', passwd='**********', db='mutual_fund')


class Funds(db.Entity):
    _table_ = "funds"
    fund_id = PrimaryKey(str)
    current_price = Optional(float)
    fund_name = Optional(str)


db.generate_mapping(create_tables=False)


@db_session
def update_price():
    funds = Funds.select()
    for fund in funds:
        percent = random.randint(-10, 10)
        rate = percent / 100.0
        fund.current_price *= (1 - rate)

    db.commit()


def lambda_handler(event, context):
    print(event)
    validation_res = auth.logged_in_as_employee(event)
    if not validation_res[0]:
        return validation_res[1]

    update_price()
    res = {"message": "The fund prices have been successfully recalculated"}

    return auth.respond(None, res)
