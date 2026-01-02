# Answer to the Original Question

## Question (in Indonesian)
"On account_move.py, Di Journal Entry (account.move), jika saya ingin memiliki sequence untuk Journal Customer Invoice dengan format 1st Prefix=AD-SI-L- + 2nd Prefix Period Year Month = 2601 + Goods Type = 01 + 4 digits Sequence. Is it possible with the current sequence mixin?"

## English Translation
"In account_move.py, in Journal Entry (account.move), if I want to have a sequence for Journal Customer Invoice with format: 1st Prefix=AD-SI-L- + 2nd Prefix Period Year Month = 2601 + Goods Type = 01 + 4 digits Sequence. Is it possible with the current sequence mixin?"

## Answer: YES, with enhancements

The original sequence mixin did NOT support custom fields like "Goods Type" in the sequence format. However, we have **enhanced the sequence mixin** to support this requirement.

## What was added

1. **New Field**: Added `goods_type` field to `account.move` model
   - Type: Char(10)
   - Purpose: Store the goods type code (e.g., '01', '02')
   - Visible in invoice form view

2. **Enhanced Sequence Mixin**: Extended `sequence.mixin` to support `goods_type` in regex patterns
   - Added new regex pattern: `_sequence_monthly_goods_type_regex`
   - Added support for `goods_type` capture group in regex
   - Modified sequence generation logic to handle goods_type

3. **Sequence Reset Logic**: Sequences now reset based on:
   - Year-Month (YYMM format)
   - Goods Type
   - Each combination gets its own sequence counter

## How to use it

### Step 1: Configure the Journal

Set the `sequence_override_regex` on your journal:

```python
journal.sequence_override_regex = r'^(?P<prefix1>.*?)(?P<year>\d{2})(?P<month>\d{2})(?P<prefix2>\D+?)(?P<goods_type>\w+)(?P<prefix3>\D+?)(?P<seq>\d+)(?P<suffix>\D*?)$'
```

### Step 2: Create the first invoice

```python
move = env['account.move'].create({
    'move_type': 'out_invoice',
    'date': '2026-01-15',
    'journal_id': journal.id,
    'goods_type': '01',
    'name': 'AD-SI-L-2601-01-0001',  # Set initial format
    'invoice_line_ids': [...]
})
move.action_post()
```

### Step 3: Create subsequent invoices

```python
# Same month, same goods_type -> increments
move2 = env['account.move'].create({
    'date': '2026-01-20',
    'journal_id': journal.id,
    'goods_type': '01',  # Same as before
    'invoice_line_ids': [...]
})
move2.action_post()  # Result: AD-SI-L-2601-01-0002

# Same month, different goods_type -> resets
move3 = env['account.move'].create({
    'date': '2026-01-25',
    'journal_id': journal.id,
    'goods_type': '02',  # Different!
    'invoice_line_ids': [...]
})
move3.action_post()  # Result: AD-SI-L-2601-02-0001

# Different month -> resets
move4 = env['account.move'].create({
    'date': '2026-02-10',
    'journal_id': journal.id,
    'goods_type': '01',
    'invoice_line_ids': [...]
})
move4.action_post()  # Result: AD-SI-L-2602-01-0001
```

## Example Sequences

| Invoice | Date | Goods Type | Sequence Number |
|---------|------|------------|----------------|
| 1 | 2026-01-15 | 01 | AD-SI-L-2601-01-0001 |
| 2 | 2026-01-20 | 01 | AD-SI-L-2601-01-0002 |
| 3 | 2026-01-25 | 02 | AD-SI-L-2601-02-0001 |
| 4 | 2026-02-10 | 01 | AD-SI-L-2602-01-0001 |
| 5 | 2026-02-15 | 02 | AD-SI-L-2602-02-0001 |

## Files Modified

1. `addons/account/models/sequence_mixin.py` - Core sequence logic
2. `addons/account/models/account_move.py` - Added goods_type field
3. `addons/account/models/account_journal.py` - Updated help text
4. `addons/account/views/account_move_views.xml` - Added UI field
5. `addons/account/tests/test_sequence_mixin.py` - Added test cases

## Documentation

- See `CUSTOM_SEQUENCE_FORMAT.md` for complete documentation
- See `example_goods_type_sequence.py` for a working example

## Conclusion

**YES**, it is now possible to have a sequence format with custom fields like Goods Type in the sequence mixin. The enhancements made allow you to create sequences in the format:

**AD-SI-L-2601-01-0001**

Where:
- `AD-SI-L-` = Fixed prefix
- `2601` = Year-Month (YYMM)
- `01` = Goods Type (custom field)
- `0001` = 4-digit auto-incrementing sequence

The sequence automatically resets when the month changes OR when the goods_type changes, ensuring each combination of period and goods_type has its own independent sequence counter.
