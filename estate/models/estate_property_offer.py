from odoo import api, fields, models
from datetime import timedelta
from odoo.exceptions import UserError

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"
    _order = "price desc"

    # Price of the offer
    price = fields.Float(string='Price', required=True)
    
    # Status of the offer: Accepted or Refused
    status = fields.Selection([
        ('accepted', 'Accepted'),
        ('refused', 'Refused')
    ], string='Status', copy=False)
    
    # Partner (buyer) who made the offer
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    
    # Property to which the offer is related
    property_id = fields.Many2one('estate.property', string='Property', required=True)

    # Validity and deadline
    create_date = fields.Datetime(string='Created on', default=fields.Datetime.now)
    validity = fields.Integer(string="Validity (days)", default=7)
    date_deadline = fields.Date(string="Deadline", compute="_compute_date_deadline", inverse="_inverse_date_deadline", store=True)
    
    # SQL Constraints
    _sql_constraints = [
        ('offer_price_positive', 'CHECK(price > 0)', 'The offer price must be strictly positive.')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        # This will hold property_ids that are being processed
        property_ids = []
        
        # First, gather all property_ids from vals_list
        for vals in vals_list:
            property_ids.append(vals.get('property_id'))

        # Check for existing offers for each property_id
        for vals in vals_list:
            property_id = vals.get('property_id')
            property = self.env['estate.property'].browse(property_id)

            # Check for existing offers with a higher price
            existing_offers = self.search([('property_id', '=', property.id), ('price', '>=', vals.get('price', 0))])
            if existing_offers:
                raise exceptions.UserError("You cannot create an offer with a price lower than or equal to an existing offer.")

            # Set the property state to 'Offer Received'
            property.state = 'offer_received'
        
        # Call the super method to perform the actual creation
        return super(EstatePropertyOffer, self).create(vals_list)


    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for offer in self:
            if offer.create_date:
                # Compute the deadline as create_date + validity days
                offer.date_deadline = offer.create_date.date() + timedelta(days=offer.validity)
            else:
                # Fallback to avoid crashing if create_date is not yet set
                offer.date_deadline = fields.Date.today() + timedelta(days=offer.validity)

    def _inverse_date_deadline(self):
        for offer in self:
            if offer.create_date and offer.date_deadline:
                # Calculate the difference between date_deadline and create_date
                delta = (offer.date_deadline - offer.create_date.date()).days
                offer.validity = delta
  
    # Method to accept the offer
    def action_accept_offer(self):
        for record in self:
            if record.property_id.offer_ids.filtered(lambda offer: offer.status == 'accepted'):
                raise UserError("Only one offer can be accepted for a given property!")
            
        self.status = 'accepted'
        for offer in self:
            offer.property_id.selling_price = offer.price
            offer.property_id.buyer_id = offer.partner_id


    # Method to refuse the offer
    def action_refuse_offer(self):
        self.status = 'refused'
                                          

