# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountJournal(models.Model):
    """Extension of account.journal to update sequence_override_regex help text."""
    
    _inherit = 'account.journal'

    # Override the help text to include goods_type documentation
    sequence_override_regex = fields.Text(
        help="Technical field used to enforce complex sequence composition that the system would normally misunderstand.\n"
             "This is a regex that can include all the following capture groups: prefix1, year, prefix2, month, prefix3, goods_type, seq, suffix.\n"
             "The prefix* groups are the separators between the year, month, goods_type and the actual increasing sequence number (seq).\n"
             "The goods_type group is optional and can be used to include a custom field value in the sequence.\n"
             r"e.g: ^(?P<prefix1>.*?)(?P<year>\d{4})(?P<month>\d{2})(?P<prefix2>\D*?)(?P<goods_type>\w+)(?P<prefix3>\D+?)(?P<seq>\d+)(?P<suffix>\D*?)$"
    )
