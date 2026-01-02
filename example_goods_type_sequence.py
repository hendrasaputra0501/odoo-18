#!/usr/bin/env python3
"""
Example script demonstrating how to use the custom sequence format with goods_type.

This script would be run in an Odoo environment to set up and test the sequence.
"""

# Step 1: Create or get a journal
journal = env['account.journal'].create({
    'name': 'Customer Invoice - Goods Type',
    'code': 'ADSI',
    'type': 'sale',
    # Set the custom regex that includes goods_type
    'sequence_override_regex': r'^(?P<prefix1>.*?)(?P<year>\d{2})(?P<month>\d{2})(?P<prefix2>\D+?)(?P<goods_type>\w+)(?P<prefix3>\D+?)(?P<seq>\d+)(?P<suffix>\D*?)$'
})

print(f"Created journal: {journal.name} (ID: {journal.id})")

# Step 2: Create the first invoice with goods_type='01' in January 2026
move1 = env['account.move'].create({
    'move_type': 'out_invoice',
    'date': '2026-01-15',
    'invoice_date': '2026-01-15',
    'partner_id': 1,  # Replace with actual partner ID
    'journal_id': journal.id,
    'goods_type': '01',
    'name': 'AD-SI-L-2601-01-0001',  # Set initial sequence format
    'invoice_line_ids': [
        (0, 0, {
            'name': 'Product A',
            'quantity': 1,
            'price_unit': 1000.0,
            'account_id': env['account.account'].search([('account_type', '=', 'income')], limit=1).id,
        }),
    ]
})
move1.action_post()
print(f"Move 1: {move1.name} (Expected: AD-SI-L-2601-01-0001)")

# Step 3: Create second invoice with same goods_type in same month
move2 = env['account.move'].create({
    'move_type': 'out_invoice',
    'date': '2026-01-20',
    'invoice_date': '2026-01-20',
    'partner_id': 1,
    'journal_id': journal.id,
    'goods_type': '01',
    'invoice_line_ids': [
        (0, 0, {
            'name': 'Product B',
            'quantity': 2,
            'price_unit': 2000.0,
            'account_id': env['account.account'].search([('account_type', '=', 'income')], limit=1).id,
        }),
    ]
})
move2.action_post()
print(f"Move 2: {move2.name} (Expected: AD-SI-L-2601-01-0002)")

# Step 4: Create third invoice with different goods_type in same month
move3 = env['account.move'].create({
    'move_type': 'out_invoice',
    'date': '2026-01-25',
    'invoice_date': '2026-01-25',
    'partner_id': 1,
    'journal_id': journal.id,
    'goods_type': '02',
    'invoice_line_ids': [
        (0, 0, {
            'name': 'Product C',
            'quantity': 1,
            'price_unit': 1500.0,
            'account_id': env['account.account'].search([('account_type', '=', 'income')], limit=1).id,
        }),
    ]
})
move3.action_post()
print(f"Move 3: {move3.name} (Expected: AD-SI-L-2601-02-0001)")

# Step 5: Create fourth invoice in next month with first goods_type
move4 = env['account.move'].create({
    'move_type': 'out_invoice',
    'date': '2026-02-10',
    'invoice_date': '2026-02-10',
    'partner_id': 1,
    'journal_id': journal.id,
    'goods_type': '01',
    'invoice_line_ids': [
        (0, 0, {
            'name': 'Product D',
            'quantity': 3,
            'price_unit': 3000.0,
            'account_id': env['account.account'].search([('account_type', '=', 'income')], limit=1).id,
        }),
    ]
})
move4.action_post()
print(f"Move 4: {move4.name} (Expected: AD-SI-L-2602-01-0001)")

# Step 6: Create fifth invoice back in January with goods_type='01'
move5 = env['account.move'].create({
    'move_type': 'out_invoice',
    'date': '2026-01-28',
    'invoice_date': '2026-01-28',
    'partner_id': 1,
    'journal_id': journal.id,
    'goods_type': '01',
    'invoice_line_ids': [
        (0, 0, {
            'name': 'Product E',
            'quantity': 1,
            'price_unit': 500.0,
            'account_id': env['account.account'].search([('account_type', '=', 'income')], limit=1).id,
        }),
    ]
})
move5.action_post()
print(f"Move 5: {move5.name} (Expected: AD-SI-L-2601-01-0003)")

print("\nSequence demonstration complete!")
print("\nSummary:")
print(f"  - Sequences reset monthly (YYMM format)")
print(f"  - Sequences reset per goods_type")
print(f"  - Each combination of year-month-goods_type has its own counter")
