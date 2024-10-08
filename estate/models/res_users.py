from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    # One2many field for the properties associated with the salesperson
    property_ids = fields.One2many(
        comodel_name="estate.property",
        inverse_name='salesperson_id',   
        domain="[('state', 'in', ['new', 'offer_received'])]"  
    )
