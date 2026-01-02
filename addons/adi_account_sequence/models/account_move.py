# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountMove(models.Model):
    """Extension of account.move to add goods_type field and sequence support."""
    
    _inherit = 'account.move'

    # Add goods_type field
    goods_type = fields.Char(
        string='Goods Type',
        size=10,
        help='Goods type code used in the sequence number (e.g., 01 for goods type 1)',
        copy=False,
        tracking=True,
    )

    @property
    def _sequence_monthly_goods_type_regex(self):
        """Expose the monthly goods_type regex pattern."""
        return self.journal_id.sequence_override_regex or super()._sequence_monthly_goods_type_regex
