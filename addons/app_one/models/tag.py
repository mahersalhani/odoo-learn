from odoo import models, fields


class Tag(models.Model):
    _name = 'tag'

    name = fields.Char(required=1)

    # Relationships
    property_ids = fields.Many2many('property')