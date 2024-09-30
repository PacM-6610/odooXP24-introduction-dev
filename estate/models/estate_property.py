from odoo import fields, models

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "estate property class"

    title = fields.Char('Title', required=True)
    description = fields.Text('Description')
    postcode = fields.Char('Postcode', required=True)
    date_availability = fields.Date('Available From')
    expected_price = fields.Float('Expected Price', required=True)
    selling_price = fields.Float('Selling Price', readonly=True, copy=False)
    bedrooms = fields.Integer('Bedrooms')
    living_area = fields.Integer('Living Area')
    facades = fields.Integer('Facades')
    garage = fields.Boolean('Garage')
    garden = fields.Boolean('Garden')
    garden_area = fields.Integer('Garden Area')
    garden_orientation = fields.Selection(string='Garden Orientation', 
                                          selection=[('north', 'North'), ('south','South'), ('east','East'), ('west','West')],
                                          help="4 possible garden orientations")
                                          

