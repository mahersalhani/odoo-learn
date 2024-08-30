from odoo import models, fields, api

class Owner(models.Model):
    _name = 'owner'

    name = fields.Char(required=True)
    phone = fields.Char()
    address = fields.Text()

    # Relationships
    property_ids = fields.One2many('property', 'owner_id')