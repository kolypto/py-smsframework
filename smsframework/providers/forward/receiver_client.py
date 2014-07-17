from flask import Blueprint
from flask.globals import request, g

from .provider import jsonex_loads, jsonex_api

bp = Blueprint('smsframework-forward-client', __name__, url_prefix='/')


@bp.route('/im', methods=['POST'])
@jsonex_api
def im():
    """ Incoming message handler: forwarded by ForwardServerProvider """
    req = jsonex_loads(request.get_data())
    message = g.provider._receive_message(req['message'])
    return {'message': message}


@bp.route('/status', methods=['POST'])
@jsonex_api
def status():
    """ Incoming status handler: forwarded by ForwardServerProvider """
    req = jsonex_loads(request.get_data())
    status = g.provider._receive_status(req['status'])
    return {'status': status}
