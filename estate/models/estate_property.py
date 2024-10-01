from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import date_utils
from datetime import date
from odoo.tools.float_utils import float_compare, float_is_zero

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"
    _order = 'id desc'

    title = fields.Char('Title', required=True)
    description = fields.Text('Description')
    postcode = fields.Char('Postcode', required=True)
    date_availability = fields.Date('Available From', copy=False, default=date_utils.add(date.today(), months=3))
    expected_price = fields.Float('Expected Price', required=True)
    selling_price = fields.Float('Selling Price', readonly=True, copy=False)
    bedrooms = fields.Integer('Bedrooms', default=2)
    living_area = fields.Integer('Living Area (sqm)')
    facades = fields.Integer('Facades')
    garage = fields.Boolean('Garage')
    garden = fields.Boolean('Garden')
    garden_area = fields.Integer('Garden Area')
    garden_orientation = fields.Selection(string='Garden Orientation', 
                                          selection=[('north', 'North'), ('south','South'), ('east','East'), ('west','West')],
                                          help="4 possible garden orientations")
    active = fields.Boolean('Active', default=True)
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('cancelled', 'Cancelled'),
            ],
        string='Status',
        required=True,
        copy=False,
        default='new',
    )
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    buyer_id = fields.Many2one('res.partner', string="Buyer", copy=False)
    salesperson_id = fields.Many2one('res.users', string="Salesperson", default=lambda self: self.env.user)

    tag_ids = fields.Many2many('estate.property.tag', string="Tags")
    
    # One2many relation to track offers for each property
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Offers')

    total_area = fields.Float(string="Total Area (sqm)", compute="_compute_total_area")

    # SQL Constraints
    _sql_constraints = [
        ('expected_price_positive', 'CHECK(expected_price > 0)', 'The expected price must be strictly positive.'),
        ('selling_price_positive', 'CHECK(selling_price >= 0)', 'The selling price must be positive.')
    ]

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self:
            # Skip check if selling price is zero (no accepted offer yet)
            if float_is_zero(record.selling_price, precision_rounding=0.01):
                continue  # Skip this constraint for zero selling price
            
            # Check if the expected_price is not zero
            if not float_is_zero(record.expected_price, precision_rounding=0.01):
                # Check if selling price is lower than 90% of expected price
                if float_compare(record.selling_price, record.expected_price * 0.9, precision_rounding=0.01) < 0:
                    raise ValidationError("The selling price cannot be lower than 90% of the expected price.")
                    
    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for property in self:
            property.total_area = property.living_area + property.garden_area

    best_offer = fields.Float(string="Best Offer", compute="_compute_best_offer")

    @api.depends('offer_ids.price')
    def _compute_best_offer(self):
        for property in self:
            offer_prices = property.offer_ids.mapped('price')
            property.best_offer = max(offer_prices) if offer_prices else 0.0

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            # Set default values when the garden is checked
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            # Clear the fields when the garden is unchecked
            self.garden_area = False
            self.garden_orientation = False

    # Method to set the property as sold
    def action_set_sold(self):
        for record in self:
            if record.state == 'cancelled':
                raise UserError("Cancelled properties cannot be set as sold.")
            record.state = 'sold'

    # Method to set the property as cancelled
    def action_set_cancelled(self):
        for record in self:
            if record.state == 'sold':
                raise UserError("Sold properties cannot be cancelled.")
            record.state = 'cancelled'

    @api.ondelete(at_uninstall=False)  # This will be called on normal deletion
    def _check_property_deletable(self):
        for property in self:
            if property.state not in ['new', 'cancelled']:
                raise exceptions.UserError("You cannot delete a property that is not in 'New' or 'Cancelled' state.")
