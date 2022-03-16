from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "estate property"
    _order = "id desc"

    name = fields.Char('Name', required=True)
    description = fields.Text('Your Description')
    postcode = fields.Char('Postal Code')
    date_availability = fields.Date('Available From', copy=False, default=lambda self: fields.Datetime.now())
    expected_price = fields.Float('Expected Price', required=True)
    selling_price = fields.Float('Selling Price', readonly=True, copy=False)
    bedrooms = fields.Integer('Bedrooms', default=2)
    living_area = fields.Integer('Living Area')
    facades = fields.Integer('Facades')
    garage = fields.Boolean('Garage', default=True)
    garden = fields.Boolean('Garden', default=True)
    garden_area = fields.Integer('Garden Area')
    total_area = fields.Integer('Total Area', compute='_compute_total_area')
    best_price = fields.Float('Best Price', compute='_compute_best_price')
    garden_orientation = fields.Selection(
        string='Orientation',
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
        help="chose garden orientation"
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[('New', 'New'), ('OfferR', 'Offer Received'), ('OfferA', 'Offer Accepted'), ('Sold', 'Sold'), ('Canceled', 'Canceled')],
        default='New'
    )
    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    buyer_id = fields.Many2one('res.partner', string='Buyer', copy=False)
    sales_person_id = fields.Many2one('res.users', string='Sales Person', default=lambda self: self.env.user)
    tag_ids = fields.Many2many('estate.property.tag', string='Tags')
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Offer')
    _sql_constraints = [
        ('positive_expected_price', 'CHECK(expected_price >= 0)', 'the price should only have positive value.'),
        ('positive_selling_price', 'CHECK(selling_price >= 0)', 'the price should only have positive value.')
    ]

    @api.constrains('expected_price', 'selling_price')
    def _check_percentage(self):
        if self.expected_price > 0:
            if (self.selling_price != 0) & (float_compare(0.90, self.selling_price/self.expected_price, 2) > 0):
                raise ValidationError('selling price should be greater than 90 percent of the expected price.')

    @api.onchange('offer_ids')
    def _onchange_offer(self):
        if len(self.offer_ids) > 0:
            self.state = 'OfferR'

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = None

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for records in self:
            records.total_area = records.living_area + records.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            buyer_id = self.buyer_id
            selling_price = self.selling_price
            max_amount_current = 0
            for line in record.offer_ids:
                if (max_amount_current < line.price) & (line.status == 'Accepted'):
                    max_amount_current = line.price
                    buyer_id = line.partner_id
                    selling_price = max_amount_current
            record.best_price = max_amount_current
            self.buyer_id = buyer_id
            self.selling_price = selling_price

    def sold(self):
        if self.state != 'Canceled':
            self.state = 'Sold'
        else:
            raise UserError('Cancelled item can not be sold.')
        return True

    def cancel(self):
        if self.state != 'Sold':
            self.state = 'Canceled'
        else:
            raise UserError('Sold item can not be cancelled.')
        return True
