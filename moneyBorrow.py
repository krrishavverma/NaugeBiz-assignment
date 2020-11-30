from flask_restful import Resource, reqparse
from flask import request
import json
from dataBaseFunction import users_borrow_data, new_user_entry, new_iou_entry


# for fetching the details of the required users
class UsersDetails(Resource):
    def get(self):
        try:
            users = request.get_json()['users']
            borrow_details = users_borrow_data(users)
            return borrow_details
        except TypeError:
            users = None
            borrow_details = users_borrow_data(users)
            return borrow_details
        except KeyError:
            return ({"error_msg": "Entered details are not in valid format, please enter the details in valid format"})
        except Exception:
            return ({"error_msg": "Invalid input details"})


# for creating new user in the database
class CreateUser(Resource):
    def post(self):
        try:
            new_user_data = request.get_json()['user']
            new_user_detail = new_user_entry(new_user_data)
            return new_user_detail
        except KeyError:
            return ({"error_msg": "Entered details are not in valid format, please enter the details in valid format"})
        except Exception:
            return ({"error_msg": "Invalid input details"})


# for creating IOU entry in the database
class CreateIOU(Resource):
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('lender',
                                type=str,
                                required=True)
            parser.add_argument('borrower',
                                type=str,
                                required=True)
            parser.add_argument('amount',
                                type=float,
                                required=True)
            new_iou_data = parser.parse_args()
            users_details = new_iou_entry(new_iou_data)
            return users_details
        except KeyError:
            return ({"error_msg": "Entered details are not in valid format, please enter the details in valid format"})
        except Exception:
            return ({"error_msg": "Invalid input details"})
