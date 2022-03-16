from odoo import models, fields, api
from datetime import date, datetime, timedelta


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "estate property offer"
    _order = "price desc"

    price = fields.Float('Price', required=True)
    status = fields.Selection(
        selection=[('Accepted', 'Accepted'), ('Refused', 'Refused')],
        copy=False
    )
    validity = fields.Integer('Validity')
    date_deadline = fields.Date('Dead Line', compute='_compute_date_deadline', inverse='_inverse_date_deadline')
    partner_id = fields.Many2one('res.partner', string='Buyer', required=True)
    property_id = fields.Many2one('estate.property', string="Property", required=True, ondelete='cascade')
    property_type_id = fields.Many2one('estate.property.type', compute='_compute_property_type_id', string="PropertyType", store=True)
    _sql_constraints = [
        ('positive_price', 'CHECK(price > 0)', 'the price can only have positive value.')
    ]

    @api.depends('property_id')
    def _compute_property_type_id(self):
        for record in self:
            record.property_type_id = record.property_id.property_type_id

    @api.depends('validity')
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date + timedelta(days=record.validity)
            else:
                record.date_deadline = datetime.now() + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            if record.create_date:
                delta_days = record.date_deadline - record.create_date.date()
                record.validity = delta_days.days
            else:
                delta_days = record.date_deadline - date.today()
                record.validity = delta_days.days

    def action_accept(self):
        self.status = 'Accepted'
        self.property_id.state = 'OfferA'
        return True

    def action_reject(self):
        self.status = 'Refused'
        return True
