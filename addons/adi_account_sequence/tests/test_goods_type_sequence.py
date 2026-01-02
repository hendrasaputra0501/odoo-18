# -*- coding: utf-8 -*-
from odoo.tests import tagged
from odoo.addons.account.tests.test_sequence_mixin import TestSequenceMixinCommon


@tagged('post_install', '-at_install')
class TestAdiSequenceGoodsType(TestSequenceMixinCommon):
    """Test goods_type field integration in sequence generation."""

    def test_goods_type_in_sequence(self):
        """Test that goods_type field can be included in sequence using custom regex."""
        # Create a journal with a custom sequence regex that includes goods_type
        journal = self.env['account.journal'].create({
            'name': 'Test Goods Type Journal',
            'code': 'ADSI',
            'type': 'sale',
            'sequence_override_regex': r'^(?P<prefix1>.*?)(?P<year>\d{2})(?P<month>\d{2})(?P<prefix2>\D+?)(?P<goods_type>\w+)(?P<prefix3>\D+?)(?P<seq>\d+)(?P<suffix>\D*?)$'
        })
        
        # Create first move with goods_type
        move1 = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'date': '2026-01-15',
            'invoice_date': '2026-01-15',
            'partner_id': self.partner_a.id,
            'journal_id': journal.id,
            'goods_type': '01',
            'name': 'AD-SI-L-2601-01-0001',
            'line_ids': [
                (0, 0, {
                    'name': 'Test Product',
                    'account_id': self.company_data['default_account_revenue'].id,
                    'price_unit': 1000.0,
                }),
            ]
        })
        move1.action_post()
        self.assertEqual(move1.name, 'AD-SI-L-2601-01-0001')
        
        # Create second move with same goods_type in same month
        move2 = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'date': '2026-01-20',
            'invoice_date': '2026-01-20',
            'partner_id': self.partner_a.id,
            'journal_id': journal.id,
            'goods_type': '01',
            'line_ids': [
                (0, 0, {
                    'name': 'Test Product 2',
                    'account_id': self.company_data['default_account_revenue'].id,
                    'price_unit': 2000.0,
                }),
            ]
        })
        move2.action_post()
        self.assertEqual(move2.name, 'AD-SI-L-2601-01-0002')
        
        # Create third move with different goods_type in same month (should reset sequence)
        move3 = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'date': '2026-01-25',
            'invoice_date': '2026-01-25',
            'partner_id': self.partner_a.id,
            'journal_id': journal.id,
            'goods_type': '02',
            'line_ids': [
                (0, 0, {
                    'name': 'Test Product 3',
                    'account_id': self.company_data['default_account_revenue'].id,
                    'price_unit': 3000.0,
                }),
            ]
        })
        move3.action_post()
        self.assertEqual(move3.name, 'AD-SI-L-2601-02-0001')
        
        # Create fourth move in a different month with first goods_type (should reset sequence)
        move4 = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'date': '2026-02-10',
            'invoice_date': '2026-02-10',
            'partner_id': self.partner_a.id,
            'journal_id': journal.id,
            'goods_type': '01',
            'line_ids': [
                (0, 0, {
                    'name': 'Test Product 4',
                    'account_id': self.company_data['default_account_revenue'].id,
                    'price_unit': 4000.0,
                }),
            ]
        })
        move4.action_post()
        self.assertEqual(move4.name, 'AD-SI-L-2602-01-0001')
