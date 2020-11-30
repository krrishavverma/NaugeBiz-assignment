import boto3
from boto3.dynamodb.conditions import Key
import json
from dynamodb_json import json_util
from decimal import Decimal


dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')


# for fetching the details of the required users
def users_borrow_data(users):
    try:
        response = dynamodb_client.scan(TableName='money_borrow_details')
        users_details = response['Items']
        users_details = json_util.loads(users_details)
        if users == None:
            return users_details
        else:
            particular_user_details = []
            for user_details in users_details:
                if user_details['name'] in users:
                    particular_user_details.append(user_details)
            return (particular_user_details)

    except dynamodb_client.exceptions.ResourceNotFoundException as e:
        ("Caught exception : {} while getting data from medicine_details table".format(
            e.response.get("Error", None).get("Message", None))), 400

    except Exception as e:
        return e


# for creating new user in the database
def new_user_entry(user_name):
    try:
        response = dynamodb_client.get_item(
            Key={
                'name': {
                    'S': user_name,
                }
            },
            TableName='money_borrow_details',
        )

        user_data = response['Item']
        return ({"message": "{} user already exist".format(user_name)})

    except KeyError:
        new_user_data = {"name": user_name}
        table = dynamodb_resource.Table('money_borrow_details')
        table.put_item(
            Item=new_user_data
        )
        users = [user_name]
        user_data = users_borrow_data(users)
        return user_data

    except dynamodb_client.exceptions.ResourceNotFoundException as e:
        return ("Caught exception : {} while adding user to the user_details table".format(e.response.get("Error", None).get("Message", None))), 400
    except Exception as e:
        return e


# for creating IOU entry in the database
def new_iou_entry(new_iou_data):
    try:
        users = [new_iou_data["lender"], new_iou_data["borrower"]]
        # fetching the lender iou from the database
        lender_user_detail = dynamodb_client.get_item(
            Key={
                'name': {
                    'S': new_iou_data["lender"],
                }
            },
            TableName='money_borrow_details',
        )

        lender_user_detail = lender_user_detail["Item"]
        lender_user_detail = json_util.loads(lender_user_detail)
        try:
            owed_by_data = lender_user_detail["owed_by"]
        except KeyError:
            owed_by_data = {}
        
        borrower_name = new_iou_data["borrower"]
        owed_by_data[borrower_name] = new_iou_data["amount"]
        lender_user_detail["owed_by"] = owed_by_data
        owed_by_money = 0
        owes_money = 0
        
        try:
            for name, money in lender_user_detail["owes"].items():
                owes_money += money
        except KeyError:
            owes_money = 0
        try:
            for name, money in lender_user_detail["owed_by"].items():
                owed_by_money += money
        except KeyError:
            owed_by_money = 0
        balance_amount = owed_by_money - owes_money
        lender_user_detail["balance"] = balance_amount

        lender_user_detail = json.loads(json.dumps(
            lender_user_detail), parse_float=Decimal)

        # updating the lender iou in the database
        table = dynamodb_resource.Table('money_borrow_details')
        table.put_item(
            Item=lender_user_detail
        )
    except KeyError:
        return {"message": "User {} does not exist".format(new_iou_data["lender"])}

    try:
        # fetching the borrower iou from the database
        borrower_user_detail = dynamodb_client.get_item(
            Key={
                'name': {
                    'S': new_iou_data["borrower"],
                }
            },
            TableName='money_borrow_details',
        )

        borrower_user_detail = borrower_user_detail["Item"]
        borrower_user_detail = json_util.loads(borrower_user_detail)
        try:
            owes_data = borrower_user_detail["owes"]
        except KeyError:
            owes_money = {}
        lender_name = new_iou_data["lender"]
        owes_data[lender_name] = new_iou_data["amount"]
        borrower_user_detail["owes"] = owes_data
        owed_by_money = 0
        owes_money = 0
        try:
            for name, money in borrower_user_detail["owes"].items():
                owes_money += money
        except KeyError:
            owes_money = 0
        try:
            for name, money in borrower_user_detail["owed_by"].items():
                owed_by_money += money
        except KeyError:
            owed_by_money = 0
        balance_amount = owed_by_money - owes_money
        borrower_user_detail["balance"] = balance_amount

        borrower_user_detail = json.loads(json.dumps(
            borrower_user_detail), parse_float=Decimal)

        # updating the borrower iou in the database
        table = dynamodb_resource.Table('money_borrow_details')
        table.put_item(
            Item=borrower_user_detail
        )
        user_data = users_borrow_data(users)
        return user_data

    except KeyError:
        borrower_user_detail = {"name": new_iou_data["borrower"], "owes": {
            new_iou_data["lender"]: new_iou_data["amount"]}, "balance": -1 * new_iou_data["amount"]}
        borrower_user_detail = json.loads(json.dumps(
            borrower_user_detail), parse_float=Decimal)
        # updating the borrower iou in the database
        table = dynamodb_resource.Table('money_borrow_details')
        table.put_item(
            Item=borrower_user_detail
        )

        user_data = users_borrow_data(users)
        return user_data
    except Exception as e:
        return e
