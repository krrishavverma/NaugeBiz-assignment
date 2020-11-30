from flask import Flask, request
from flask_restful import Api
from moneyBorrow import UsersDetails, CreateUser, CreateIOU


application = app = Flask(__name__)
api = Api(app)

# endpoints
api.add_resource(UsersDetails, '/users')
api.add_resource(CreateUser, '/add')
api.add_resource(CreateIOU, '/iou')


if __name__ == '__main__':
    app.run(debug=True)
