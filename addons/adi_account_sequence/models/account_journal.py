# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import re


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

    @api.constrains('sequence_override_regex')
    def _check_sequence_override_regex(self):
        """Validate that the sequence_override_regex contains at least the seq grouping key."""
        for journal in self:
            if journal.sequence_override_regex:
                # Check if the regex is valid syntax
                try:
                    compiled_regex = re.compile(journal.sequence_override_regex)
                except re.error as e:
                    raise ValidationError(_(
                        'The sequence regex is invalid: %s\n\n'
                        'Please provide a valid regular expression.'
                    ) % str(e))
                
                # Check if the regex contains the required 'seq' named group
                if 'seq' not in compiled_regex.groupindex:
                    raise ValidationError(_(
                        'The sequence regex should at least contain the seq grouping keys. For instance:\n'
                        r'^(?P<prefix1>.*?)(?P<seq>\d+)(?P<suffix>\D*?)$'
                    ))
                
                # Validate that the regex can actually match a sequence with digits in the seq group
                # Try to match test sequences to ensure the regex is functional
                test_sequences = [
                    'TEST0001',              # Simple pattern
                    'AD-SI-L-2601-01-0001',  # Complex month_goods_type pattern
                    'INV/2026/01/0001',      # Monthly pattern
                    'INV/2026/0001',         # Yearly pattern
                ]
                
                matched = False
                for test_seq in test_sequences:
                    match = compiled_regex.match(test_seq)
                    if match:
                        groupdict = match.groupdict()
                        # Check if seq group exists and has a value (not None and not empty)
                        if 'seq' in groupdict and groupdict['seq']:
                            matched = True
                            break
                
                if not matched:
                    raise ValidationError(_(
                        'The sequence regex should at least contain the seq grouping keys. For instance:\n'
                        r'^(?P<prefix1>.*?)(?P<seq>\d+)(?P<suffix>\D*?)$'
                    ))
