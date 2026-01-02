# Custom Sequence Format with Goods Type

This document explains how to use the enhanced sequence mixin to create custom sequence formats that include additional fields like goods_type.

## Overview

The sequence mixin has been extended to support a `goods_type` field in the sequence format. This allows you to create sequences like:

**Format**: `AD-SI-L-2601-01-0001`

Where:
- `AD-SI-L-` = Fixed prefix
- `2601` = Period (Year-Month in YYMM format)
- `01` = Goods Type (custom field value)
- `0001` = 4-digit sequence number

## Setup

### Step 1: Set the goods_type field value

When creating or editing an invoice/move, set the `goods_type` field:

```python
move = self.env['account.move'].create({
    'move_type': 'out_invoice',
    'date': '2026-01-15',
    'partner_id': partner.id,
    'journal_id': journal.id,
    'goods_type': '01',  # Set your goods type here
    'line_ids': [...]
})
```

### Step 2: Configure the Journal Sequence Regex

Set the `sequence_override_regex` field on the journal to include the `goods_type` capture group:

```python
journal.sequence_override_regex = r'^(?P<prefix1>.*?)(?P<year>\d{2})(?P<month>\d{2})(?P<prefix2>\D+?)(?P<goods_type>\w+)(?P<prefix3>\D+?)(?P<seq>\d+)(?P<suffix>\D*?)$'
```

### Step 3: Set the initial sequence format

Create the first move with the desired sequence format:

```python
move.name = 'AD-SI-L-2601-01-0001'
move.action_post()
```

## Sequence Behavior

The sequence will:
- **Reset monthly**: The sequence resets at the start of each month (because year and month are in the regex)
- **Reset per goods_type**: Different goods types maintain separate sequence counters
- **Auto-increment**: Subsequent moves with the same year-month-goods_type combination will increment the sequence

## Example

```python
# Create a journal
journal = self.env['account.journal'].create({
    'name': 'Customer Invoice',
    'code': 'ADSI',
    'type': 'sale',
    'sequence_override_regex': r'^(?P<prefix1>.*?)(?P<year>\d{2})(?P<month>\d{2})(?P<prefix2>\D+?)(?P<goods_type>\w+)(?P<prefix3>\D+?)(?P<seq>\d+)(?P<suffix>\D*?)$'
})

# First invoice - January 2026, goods type 01
move1 = self.env['account.move'].create({
    'move_type': 'out_invoice',
    'date': '2026-01-15',
    'journal_id': journal.id,
    'goods_type': '01',
    'name': 'AD-SI-L-2601-01-0001',
    ...
})
move1.action_post()
# Result: AD-SI-L-2601-01-0001

# Second invoice - January 2026, goods type 01
move2 = self.env['account.move'].create({
    'move_type': 'out_invoice',
    'date': '2026-01-20',
    'journal_id': journal.id,
    'goods_type': '01',
    ...
})
move2.action_post()
# Result: AD-SI-L-2601-01-0002 (auto-incremented)

# Third invoice - January 2026, goods type 02
move3 = self.env['account.move'].create({
    'move_type': 'out_invoice',
    'date': '2026-01-25',
    'journal_id': journal.id,
    'goods_type': '02',
    ...
})
move3.action_post()
# Result: AD-SI-L-2601-02-0001 (new goods type, resets sequence)

# Fourth invoice - February 2026, goods type 01
move4 = self.env['account.move'].create({
    'move_type': 'out_invoice',
    'date': '2026-02-10',
    'journal_id': journal.id,
    'goods_type': '01',
    ...
})
move4.action_post()
# Result: AD-SI-L-2602-01-0001 (new month, resets sequence)
```

## Regex Capture Groups

The following capture groups are supported in `sequence_override_regex`:

- `prefix1`, `prefix2`, `prefix3`: Separator strings (non-numeric characters)
- `year`: Year (2 or 4 digits)
- `month`: Month (2 digits)
- `goods_type`: Custom field value (alphanumeric)
- `seq`: Sequence number (numeric)
- `suffix`: Trailing separator string

## Important Notes

1. **Goods Type Format**: The goods_type field accepts alphanumeric characters. Format it as needed (e.g., "01", "02", "A1", etc.)

2. **Sequence Reset**: The sequence resets based on the regex pattern. If year and month are included, it resets monthly. If goods_type is included, each goods_type has its own sequence counter.

3. **First Sequence**: Always set the name explicitly on the first move to establish the sequence pattern. Subsequent moves will follow this pattern automatically.

4. **Posted Moves**: The sequence is only assigned when the move is posted. Draft moves show a placeholder.

## Technical Details

### Files Modified

1. `addons/account/models/sequence_mixin.py`:
   - Added `goods_type` regex pattern
   - Added `_sequence_monthly_goods_type_regex` 
   - Updated `_deduce_sequence_number_reset()` to recognize month_goods_type pattern
   - Updated `_get_sequence_date_range()` to handle month_goods_type reset
   - Updated `_get_sequence_format_param()` to extract and format goods_type
   - Updated `_get_next_sequence_format()` to populate goods_type from record

2. `addons/account/models/account_move.py`:
   - Added `goods_type` field (Char, size=10)
   - Added `_sequence_monthly_goods_type_regex` property

3. `addons/account/models/account_journal.py`:
   - Updated `sequence_override_regex` help text to document goods_type

4. `addons/account/views/account_move_views.xml`:
   - Added goods_type field to invoice form view

### Sequence Detection Logic

The system uses regex patterns to detect the sequence format and determine when to reset:

1. `year_range_month`: Resets yearly with fiscal year range and month
2. `month_goods_type`: Resets monthly with goods_type (NEW)
3. `month`: Resets monthly
4. `year_range`: Resets yearly with fiscal year range
5. `year`: Resets yearly
6. `never`: Never resets

The patterns are checked in order, and the first matching pattern is used.
