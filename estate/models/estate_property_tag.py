from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Real Estate Property Tag"
    _order = 'name' 

    name = fields.Char(string="Tag Name", required=True)

    # SQL Constraint to make tag names unique
    _sql_constraints = [
        ('property_tag_unique', 'UNIQUE(name)', 'The property tag name must be unique.')
    ]
  
                                          

