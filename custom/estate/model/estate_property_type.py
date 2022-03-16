from odoo import models, fields,api


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'estate property type description'
    _order = "name"

    name = fields.Char('Name', required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id', string='Properties')
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id', string='Offers     ')
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    offer_count = fields.Integer('Offer Counts', compute='_compute_count')

    _sql_constraints = [
        ('unique_tag', 'UNIQUE(name)', 'tag name should be unique.')
    ]

    @api.depends('offer_ids')
    def _compute_count(self):
        for record in self:
            self.offer_count = len(self.offer_ids)
