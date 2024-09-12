import json
from odoo import http
from odoo.http import request


class Property(http.Controller):
    # @http.route('/property/', methods=['GET'], type='http', auth='none', csrf=False)
    # def index(self, **kw):
    #     return "Hello, world"

    @http.route('/v1/property', methods=['POST'], auth='none', csrf=False, type='http')
    def create_property(self, **kw):
        print('create_property')
        args = request.httprequest.data.decode()
        vals = json.loads(args)

        if not vals.get('name'):
            return request.make_response(json.dumps({
                'message': 'Name is required',
            }), status=400)

        try:
            res = request.env['property'].sudo().create(vals)
            if res:
                return request.make_response(json.dumps({
                    'status': 'success',
                    'message': 'Property created successfully',
                    'id': res.id,
                    'name': res.name,
                }),
                    status=201)
        except Exception as e:
            return request.make_response(json.dumps({
                                                    'message': str(e),
                                                    }), status=400)

    @http.route('/v1/property/json', methods=['POST'], auth='none', csrf=False, type='json')
    def create_property_json(self, **kw):
        print('create_property_json')
        args = request.httprequest.data.decode()
        vals = json.loads(args)

        res = request.env['property'].sudo().create(vals)

        if res:
            return {'message': 'Property created successfully'}

    @http.route('/v1/property/<int:id>', methods=["PUT"], auth='none', csrf=False, type='http')
    def update_property(self, id, **kw):
        print('update_property')
        args = request.httprequest.data.decode()
        vals = json.loads(args)

        res = request.env['property'].sudo().search([('id', '=', id)], limit=1)
        if not res:
            return request.make_response(json.dumps({
                'message': 'Property not found',
            }), status=404)

        res.write(vals)
        return request.make_response(json.dumps({
            'message': 'Property updated successfully',
        }), status=200)
