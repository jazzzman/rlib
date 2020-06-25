import json
from flask import Blueprint

bp = Blueprint('filters', __name__)

@bp.app_template_filter('jsonPresOrd')
def json_preserve_order(input):
    return json.dumps(input)


@bp.app_template_filter('to_gost')
def auth_gost(input, rus=False):
    return [a.to_gost(rus) for a in input]

bp.add_app_template_filter(json_preserve_order)
bp.add_app_template_filter(auth_gost)

