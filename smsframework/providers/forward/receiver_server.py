from flask import Blueprint
from flask.globals import request, g

from .provider import jsonex_loads, jsonex_dumps, jsonex_api

bp = Blueprint('smsframework-forward-server', __name__, url_prefix='/')


@bp.route('/im', methods=['POST'])
@jsonex_api
def im():
    """ Incoming message handler: sent by ForwardClientProvider """
    req = jsonex_loads(request.get_data())
    message = g.provider.send(req['message'])
    return {'message': message}
