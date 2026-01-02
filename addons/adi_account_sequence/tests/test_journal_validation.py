# -*- coding: utf-8 -*-
from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install')
class TestJournalSequenceValidation(TransactionCase):
    """Test sequence_override_regex validation on account.journal."""

    def test_valid_sequence_regex(self):
        """Test that valid regex patterns are accepted."""
        # Test with goods_type pattern
        journal = self.env['account.journal'].create({
            'name': 'Test Valid Goods Type',
            'code': 'VGT',
            'type': 'sale',
            'sequence_override_regex': r'^(?P<prefix1>.*?)(?P<year>\d{2})(?P<month>\d{2})(?P<prefix2>\D+?)(?P<goods_type>\w+)(?P<prefix3>\D+?)(?P<seq>\d+)(?P<suffix>\D*?)$'
        })
        self.assertTrue(journal.id, "Journal with valid goods_type regex should be created")
        
        # Test with monthly pattern
        journal2 = self.env['account.journal'].create({
            'name': 'Test Valid Monthly',
            'code': 'VML',
            'type': 'sale',
            'sequence_override_regex': r'^(?P<prefix1>.*?)(?P<year>\d{4})(?P<prefix2>\D*?)(?P<month>\d{2})(?P<prefix3>\D+?)(?P<seq>\d+)(?P<suffix>\D*?)$'
        })
        self.assertTrue(journal2.id, "Journal with valid monthly regex should be created")
        
        # Test with simple pattern
        journal3 = self.env['account.journal'].create({
            'name': 'Test Valid Simple',
            'code': 'VSP',
            'type': 'sale',
            'sequence_override_regex': r'^(?P<prefix1>.*?)(?P<seq>\d+)(?P<suffix>\D*?)$'
        })
        self.assertTrue(journal3.id, "Journal with valid simple regex should be created")

    def test_invalid_sequence_regex_no_seq_group(self):
        """Test that regex without seq group is rejected."""
        with self.assertRaises(ValidationError) as cm:
            self.env['account.journal'].create({
                'name': 'Test Invalid No Seq',
                'code': 'INS',
                'type': 'sale',
                'sequence_override_regex': r'^(?P<prefix1>.*?)(?P<year>\d{2})(?P<month>\d{2})$'
            })
        self.assertIn('seq grouping keys', str(cm.exception))

    def test_invalid_sequence_regex_syntax(self):
        """Test that invalid regex syntax is rejected."""
        with self.assertRaises(ValidationError) as cm:
            self.env['account.journal'].create({
                'name': 'Test Invalid Syntax',
                'code': 'IVS',
                'type': 'sale',
                'sequence_override_regex': r'^(?P<prefix1>.*?)(?P<seq>\d+[)$'  # Missing closing parenthesis
            })
        self.assertIn('invalid', str(cm.exception).lower())

    def test_empty_sequence_regex(self):
        """Test that empty regex is allowed (uses default)."""
        journal = self.env['account.journal'].create({
            'name': 'Test Empty Regex',
            'code': 'TER',
            'type': 'sale',
            'sequence_override_regex': False
        })
        self.assertTrue(journal.id, "Journal with empty regex should be created")

    def test_update_journal_with_invalid_regex(self):
        """Test that updating journal with invalid regex is rejected."""
        journal = self.env['account.journal'].create({
            'name': 'Test Update',
            'code': 'TUP',
            'type': 'sale',
        })
        
        with self.assertRaises(ValidationError) as cm:
            journal.sequence_override_regex = r'^(?P<prefix1>.*?)(?P<year>\d{2})$'  # No seq group
        self.assertIn('seq grouping keys', str(cm.exception))
