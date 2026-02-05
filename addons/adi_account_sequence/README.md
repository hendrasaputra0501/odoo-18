# ADI Account Sequence with Goods Type

This module extends Odoo's accounting sequence mixin to support custom fields (like goods_type) in invoice sequence formats.

## Features

- **Custom Sequence Format**: Create sequences like `AD-SI-L-2601-01-0001`
  - `AD-SI-L-` = Fixed prefix
  - `2601` = Year-Month (YYMM format)
  - `01` = Goods Type (custom field)
  - `0001` = 4-digit auto-incrementing sequence

- **Automatic Reset**: Sequences reset when:
  - Month changes
  - Goods type changes

- **Independent Counters**: Each year-month-goods_type combination maintains its own sequence

- **Regex Validation**: Immediate validation when configuring journal sequence patterns

- **Backward Compatible**: Existing sequences continue to work without modification

## Installation

1. Copy this module to your Odoo addons directory
2. Update the app list: Apps → Update Apps List
3. Install the module: Apps → Search "ADI Account Sequence" → Install

## Configuration

### Step 1: Create or Configure a Journal

1. Go to Accounting → Configuration → Journals
2. Select your journal (e.g., Customer Invoices) or create a new one
3. Set the `Sequence Override Regex` field:

```regex
^(?P<prefix1>.*?)(?P<year>\d{2})(?P<month>\d{2})(?P<prefix2>\D+?)(?P<goods_type>\w+)(?P<prefix3>\D+?)(?P<seq>\d+)(?P<suffix>\D*?)$
```

**Important**: The system will validate the regex immediately. If it's invalid, you'll see an error:
- "The sequence regex should at least contain the seq grouping keys"

### Step 2: Validate the Configuration

When you save the journal, the system checks:
- ✅ The regex is syntactically correct
- ✅ It contains the required `seq` capture group
- ✅ It can match common sequence patterns

## Usage

### Frontend Usage (Recommended for Users)

For step-by-step instructions with screenshots and examples, see:
- **[FRONTEND_GUIDE.md](FRONTEND_GUIDE.md)** - Complete guide for using the module through Odoo UI

### First Invoice (Set Pattern)

Create your first invoice with the desired sequence format:

1. Create a new invoice
2. Set `Goods Type` field (e.g., "01")
3. Set `Number` field to establish the pattern (e.g., "AD-SI-L-2601-01-0001")
4. Post the invoice

### Subsequent Invoices (Auto-Generate)

For subsequent invoices:

1. Create a new invoice
2. Set `Goods Type` field
3. Post the invoice → Sequence is auto-generated!

## Example

```python
# Invoice 1: Jan 2026, goods_type='01' → AD-SI-L-2601-01-0001
# Invoice 2: Jan 2026, goods_type='01' → AD-SI-L-2601-01-0002
# Invoice 3: Jan 2026, goods_type='02' → AD-SI-L-2601-02-0001 (resets for new type)
# Invoice 4: Feb 2026, goods_type='01' → AD-SI-L-2602-01-0001 (resets for new month)
```

## Documentation

- **[FRONTEND_GUIDE.md](FRONTEND_GUIDE.md)**: Step-by-step guide for using the module through the Odoo UI
- **[ANSWER.md](ANSWER.md)**: Direct answer to the original question
- **[CUSTOM_SEQUENCE_FORMAT.md](CUSTOM_SEQUENCE_FORMAT.md)**: Complete technical documentation
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)**: Implementation details
- **[example_goods_type_sequence.py](example_goods_type_sequence.py)**: Working example script

## Technical Details

### Module Structure

- `models/sequence_mixin.py`: Extends `sequence.mixin` with goods_type support
- `models/account_move.py`: Adds `goods_type` field to invoices
- `models/account_journal.py`: Updates help text for sequence_override_regex
- `views/account_move_views.xml`: Adds UI field for goods_type

### Sequence Reset Logic

The sequence resets when:
- **Month changes**: Different YYMM value
- **Goods type changes**: Different goods_type value

Each combination gets an independent counter.

## Support

For issues or questions, please refer to the documentation files or create an issue in the repository.

## License

LGPL-3

## Credits

- Author: ADI
- Repository: https://github.com/hendrasaputra0501/odoo-18
