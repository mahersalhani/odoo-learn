from odoo import models, fields, api


class Property(models.Model):
    _name = 'property'
    _description = 'Property Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    ref = fields.Char(readonly=True, default='New')
    name = fields.Char(required=True, default='New', size=12)
    description = fields.Text(tracking=True)
    postcode = fields.Char(required=1)  # Required field
    # Enable tracking on the date_availability field
    date_availability = fields.Date(tracking=True)
    expected_selling_date = fields.Date(tracking=1)
    is_late = fields.Boolean()
    # expected_price = fields.Float(digits=(0, 5)) # 5 digits before the decimal point
    expected_price = fields.Float()
    diff = fields.Float(compute='_compute_diff', store=True)
    selling_price = fields.Float()
    bedrooms = fields.Integer(required=True)  # Required field
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West'),
    ], Default='north')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('sold', 'Sold'),
        ('closed', 'Closed')
    ], Default='draft')
    active = fields.Boolean(default=True)
    create_time = fields.Datetime(default=fields.Datetime.now)

    # Relationships
    owner_id = fields.Many2one('owner')
    owner_phone = fields.Char(related='owner_id.phone', readonly=False)
    owner_address = fields.Text(related='owner_id.address', readonly=0)
    tag_ids = fields.Many2many('tag')
    line_ids = fields.One2many('property.line', 'property_id')

    # Constraints
    _sql_constraints = [
        ('unique_name', 'unique(name)', 'The name of the property must be unique.'),
    ]

    # Computed Fields
    # Decorator to add a dependency on the expected_price and selling_price fields
    @api.depends('expected_price', 'selling_price')
    def _compute_diff(self):
        for record in self:
            print('inside _compute_diff method')
            record.diff = record.expected_price - record.selling_price

    # Decorator to add an onchange on the bedrooms field
    @api.onchange('expected_price')
    def _onchange_expected_price(self):
        for rec in self:
            print('inside _onchange_expected_price method')
            # if rec.expected_price < 0:
            #     rec.expected_price = 0
            return {
                'warning': {
                    'title': 'Warning',
                    'message': 'The expected price should be greater than 0.',
                    'type': 'notification'
                }
            }

    # Decorator to add a constraint on the bedrooms field
    @api.constrains('bedrooms')
    # self is like this in Python, it refers to the current instance of the class
    def _check_bedrooms_gt_0(self):
        for record in self:
            if record.bedrooms <= 0:
                raise ValueError(
                    'The number of bedrooms must be greater than 0.')

    def action_draft(self):
        for rec in self:
            print('inside action_draft method')
            rec.create_history_record(rec.state, 'draft')
            rec.state = 'draft'

    def action_pending(self):
        for rec in self:
            rec.create_history_record(rec.state, 'pending')
            rec.write({'state': 'pending'})

    def action_sold(self):
        for rec in self:
            rec.create_history_record(rec.state, 'sold')
            rec.state = 'sold'

    def action_closed(self):
        for rec in self:
            rec.create_history_record(rec.state, 'closed')
            rec.state = 'closed'

    def check_selling_date(self):
        property_ids = self.search([])
        for record in property_ids:
            if record.expected_selling_date and record.expected_selling_date < fields.Date.today():
                record.is_late = True
            else:
                record.is_late = False

        print('inside check_selling_date method')

    def action_open_change_state_wizard(self):
        action = self.env['ir.actions.actions']._for_xml_id(
            'app_one.change_state_wizard_action')
        action['context'] = {'default_property_id': self.id}
        return action

    # CRUD Operations
    @api.model_create_multi
    def create(self, vals):
        res = super(Property, self).create(vals)
        print('inside create method')
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code(
                'property_seq') or 'New'
        return res

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        res = super(Property, self)._search(
            domain, offset, limit, order, access_rights_uid)
        print('inside search method')
        return res

    def write(self, vals):
        res = super(Property, self).write(vals)
        print('inside write method')
        return res

    def unlink(self):
        res = super(Property, self).unlink()
        print('inside unlink method')
        return res

    def create_history_record(self, old_state, new_state, reason=""):
        for rec in self:
            print('inside create_history_record method')
            self.env['property.history'].create({
                'user_id': rec.env.uid,
                'property_id': rec.id,
                'old_state': old_state,
                'new_state': new_state,
                'reason': reason,
                'line_ids': [(0, 0, {'area': line.area, 'description': line.description}) for line in rec.line_ids],
            })


class PropertyLine(models.Model):
    _name = 'property.line'

    area = fields.Float()
    description = fields.Text()
    property_id = fields.Many2one('property')
