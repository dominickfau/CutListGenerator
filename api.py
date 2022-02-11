from __future__ import annotations
import datetime
import logging
from socket import gethostname, gethostbyname
from flask import Flask
from flask_restful import Api, Resource, abort, request, reqparse
from dataclasses import dataclass
from secrets import token_hex
from waitress import serve

import cutlistgenerator
from cutlistgenerator import errors, database, statuscodes
from cutlistgenerator.thread import register as thread_register

from cutlistgenerator.database.models.cutjob import CutJob, CutJobStatus, PartCutHistory
from cutlistgenerator.database.models.salesorder import (
    SalesOrder,
    SalesOrderItem,
    SalesOrderStatus,
)
from cutlistgenerator.database.models.user import User
from cutlistgenerator.settings import API_TOKEN_VALIDITY, FLASK_SECRET_KEY


logger = logging.getLogger("flask")


flask_app = Flask(__name__)
flask_app.config["SECRET_KEY"] = FLASK_SECRET_KEY
api = Api(flask_app)

login_post_parser = reqparse.RequestParser()
login_post_parser.add_argument(
    "username", type=str, required=True, help="Username is required."
)
login_post_parser.add_argument(
    "password", type=str, required=True, help="Password is required."
)

api_request_parser = reqparse.RequestParser()
api_request_parser.add_argument(
    "api_token",
    type=str,
    required=True,
    help="API token is required. Please provide a valid API token.",
)


@dataclass
class ApiToken:
    user: User
    token: str
    expires: datetime.datetime = datetime.datetime.now() + datetime.timedelta(
        days=API_TOKEN_VALIDITY
    )

    def expired(self) -> bool:
        return self.expires < datetime.datetime.now()

    @staticmethod
    def generate() -> str:
        """Generates a new API token key."""
        return token_hex(32)


api_tokens = (
    list()
)  # type: list[ApiToken] # FIXME: Find a better way to store API tokens.


def api_token_watchdog() -> None:
    """API token watchdog. Used in a thread for removing expired API tokens."""
    global api_tokens

    while True:
        for token in api_tokens:
            if token.expired():
                logger.info(f"Removing expired API token: {token.token}")
                api_tokens.remove(token)


def validate_api_token(api_token: str) -> tuple[bool, ApiToken]:
    """Validates an API token."""
    for token in api_tokens:
        if token.token == api_token:
            return True, token
    return False, None


# decorator to check for valid API token
def requires_api_token(f):
    def decorated(*args, **kwargs):
        args = api_request_parser.parse_args()
        api_token = args["api_token"]
        if not api_token:
            abort(statuscodes.HTTP_INVALID_TOKEN, message="API token is invalid.")
        valid, token = validate_api_token(api_token)
        if not valid:
            abort(statuscodes.HTTP_UNAUTHORIZED, message="API token is invalid.")
        if token.expired():
            abort(statuscodes.HTTP_UNAUTHORIZED, message="API token has expired.")

        token.expires = datetime.datetime.now() + datetime.timedelta(seconds=20)
        return f(*args, **kwargs)

    return decorated


class OpenCutJobs(Resource):
    # @requires_api_token
    def get(self):
        """Returns a list of open cut jobs."""
        with database.Session() as session:
            fullfilled_status = (
                session.query(CutJobStatus)
                .filter(CutJobStatus.name == "Fulfilled")
                .first()
            )
            cut_jobs = (
                session.query(CutJob)
                .filter(CutJob.status_id < fullfilled_status.id)
                .all()
            )
            return [cut_job.to_dict() for cut_job in cut_jobs]


class OpenSalesOrders(Resource):
    # @requires_api_token
    def get(self):
        """Returns a list of open sales orders."""
        with database.Session() as session:
            fullfilled_status = (
                session.query(SalesOrderStatus)
                .filter(SalesOrderStatus.name == "Fulfilled")
                .first()
            )
            sales_orders = (
                session.query(SalesOrder)
                .filter(SalesOrder.status_id < fullfilled_status.id)
                .all()
            )
            return [sales_order.to_dict() for sales_order in sales_orders]


class UncutSalesOrders(Resource):
    # @requires_api_token
    def get(self):
        """Returns a list of uncut sales orders."""
        with database.Session() as session:
            fullfilled_status = (
                session.query(SalesOrderStatus)
                .filter(SalesOrderStatus.name == "Fulfilled")
                .first()
            )
            sales_orders = (
                session.query(SalesOrder)
                .join(SalesOrderItem)
                .filter(
                    SalesOrder.status_id < fullfilled_status.id,
                    SalesOrderItem.is_cut == 0,
                )
                .all()
            )
            return [sales_order.to_dict() for sales_order in sales_orders]


class PartCutHistoryResource(Resource):
    # @requires_api_token
    def get(self, part_number: str):
        with database.Session() as session:
            part_cut_history_list = PartCutHistory.find_by_part_number(
                part_number, session=session
            )
            if part_cut_history_list is None:
                abort(
                    statuscodes.HTTP_NOT_FOUND,
                    message="Part {} not found".format(part_number),
                )
            return [
                part_cut_history.to_dict() for part_cut_history in part_cut_history_list
            ]


class LoginResource(Resource):
    def get(self):
        args = login_post_parser.parse_args()
        username = args["username"]
        password = args["password"]

        try:
            user = User.authenticate(username, password)
            for api_token in api_tokens:
                if api_token.user == user:
                    return {
                        "message": "User already logged in.",
                        "api_token": api_token.token,
                    }
            api_token = ApiToken(user, ApiToken.generate())
            api_tokens.append(api_token)
        except errors.AuthenticationError as e:
            abort(statuscodes.HTTP_UNAUTHORIZED, message=str(e))
        return {"user": user.to_dict(), "token": api_token.token}


class LogoutResource(Resource):
    @requires_api_token
    def get(self):
        args = api_request_parser.parse_args()
        api_token = args["api_token"]

        logged_out = False

        for i, token in enumerate(api_tokens):
            if token.token == api_token:
                del api_tokens[i]
                logged_out = True
                break
        if not logged_out:
            abort(statuscodes.HTTP_INVALID_TOKEN, message="API token invalid")
        return {"message": "Logged out successfully"}


# api.add_resource(Part, '/part/<int:part_id>')
api.add_resource(OpenCutJobs, "/api/cutjobs/open")
api.add_resource(UncutSalesOrders, "/api/salesorders/uncut")
api.add_resource(OpenSalesOrders, "/api/salesorders/open")
api.add_resource(PartCutHistoryResource, "/api/partcuthistory/<string:part_number>")

api.add_resource(LoginResource, "/api/login")
api.add_resource(LogoutResource, "/api/logout")


thread_register(api_token_watchdog)


def start_api(host: str = "0.0.0.0", port: int = 5000) -> None:
    """Starts the API server."""
    logger.info("Starting API server")
    host_ = host
    host_name = gethostname()
    host_ip = gethostbyname(host_name)
    if host_ == "0.0.0.0":
        host_ = host_ip
    logger.info(f"API server listening on {host_}:{port}")
    serve(flask_app, host=host_, port=port, threads=1)


if __name__ == "__main__":
    database.create()
    start_api()
