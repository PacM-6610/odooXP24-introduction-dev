from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import date_utils
from datetime import date
from odoo.tools.float_utils import float_compare, float_is_zero

class EstateProperty(models.Model):
    _inherit = "estate.property"

    # Override the action_set_sold method
    def action_set_sold(self):
        for record in self:
            # Fetch the default sales journal
            journal = self.env['account.bank.statement.line'].with_context(journal_type='sale')._get_default_journal() 
            if not journal:
                raise UserError("No sales journal found! Please configure a sales journal.")
            
            # Create an empty account.move (Customer Invoice) with the buyer as the partner
            invoice_vals = {
                'partner_id': record.buyer_id.id,  # Take the partner (buyer) from the current estate.property
                'move_type': 'out_invoice',  # Set as a Customer Invoice
                'journal_id': journal.id,  # Use the found sales journal
                'invoice_line_ids': [
                    # First line: 6% commission on the selling price
                    (0, 0, {
                        'name': f"Commission for the sale of property {record.title}",  # Description of the commission
                        'quantity': 1,
                        'price_unit': record.selling_price * 0.06,  # 6% of the selling price
                    }),
                    # Second line: Fixed administrative fee of 100.00
                    (0, 0, {
                        'name': "Administrative fees",  # Description for the administrative fee
                        'quantity': 1,
                        'price_unit': 100.00,  # Fixed fee
                    })
                ],
            }
            
            # Create the invoice
            invoice = self.env['account.move'].create(invoice_vals)

        return super().action_set_sold()