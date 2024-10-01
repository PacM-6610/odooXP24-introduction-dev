from odoo import api, fields, models

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "estate property type"
    _order = 'sequence, name' 

    name = fields.Char('Title', required=True)
    sequence = fields.Integer(string="Sequence", default=1)  # Default sequence value
    property_ids = fields.One2many('estate.property', 'property_type_id', string="Properties")
                                    
    # SQL Constraint to make property type names unique
    _sql_constraints = [
        ('property_type_unique', 'UNIQUE(name)', 'The property type name must be unique.')
    ]
