# Frontend Usage Guide - ADI Account Sequence with Goods Type

This guide provides step-by-step instructions for using the ADI Account Sequence module through the Odoo frontend interface.

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Creating a New Journal](#creating-a-new-journal)
4. [Creating Customer Invoices](#creating-customer-invoices)
5. [Understanding Sequence Behavior](#understanding-sequence-behavior)
6. [Troubleshooting](#troubleshooting)

---

## Overview

The ADI Account Sequence module allows you to create custom invoice sequences that include:
- **Fixed Prefix**: e.g., "AD-SI-L-"
- **Year-Month**: e.g., "2601" for January 2026
- **Goods Type**: e.g., "01" for goods type 1
- **Sequence Number**: e.g., "0001"

**Example Format**: `AD-SI-L-2601-01-0001`

The sequence automatically:
- Resets each month
- Resets for each different goods type
- Increments for the same month and goods type combination

---

## Installation

### Step 1: Install the Module

1. Log in to Odoo as Administrator
2. Go to **Apps** menu
3. Click **Update Apps List**
4. Search for "ADI Account Sequence"
5. Click **Install**

### Step 2: Verify Installation

After installation, you should see:
- A new "Goods Type" field on customer invoices
- Updated help text for journal sequence configuration

---

## Creating a New Journal

### Step 1: Navigate to Journals

1. Go to **Accounting** → **Configuration** → **Journals**
2. Click **Create** button

### Step 2: Configure Basic Journal Information

Fill in the basic information:
- **Journal Name**: e.g., "Customer Invoice - Goods Type"
- **Type**: Select "Sales"
- **Short Code**: e.g., "ADSI"
- **Currency**: Select your currency (if different from company default)

### Step 3: Configure Sequence Override Regex

This is the critical step for custom sequence format.

1. Scroll down to find the **Advanced Settings** tab or **Sequence Override Regex** field
2. In the **Sequence Override Regex** field, enter:

```regex
^(?P<prefix1>.*?)(?P<year>\d{2})(?P<month>\d{2})(?P<prefix2>\D+?)(?P<goods_type>\w+)(?P<prefix3>\D+?)(?P<seq>\d+)(?P<suffix>\D*?)$
```

**Important Notes:**
- This regex pattern MUST include the `(?P<seq>\d+)` capture group (for the sequence number)
- It MUST include `(?P<year>\d{2})` and `(?P<month>\d{2})` for monthly reset
- It includes `(?P<goods_type>\w+)` for goods type support
- The system will validate the regex when you save the journal

### Step 4: Validation

When you save the journal:
- ✅ **Success**: If the regex is valid, the journal will be saved
- ❌ **Error**: If the regex is invalid, you'll see an error message:
  - "The sequence regex should at least contain the seq grouping keys"
  - Fix the regex according to the error message

### Step 5: Save the Journal

Click **Save** to create the journal.

---

## Creating Customer Invoices

Now that you have configured your journal, you can create invoices with the custom sequence.

### Creating the FIRST Invoice (Setting the Pattern)

The first invoice is special because it establishes the sequence pattern.

1. Go to **Accounting** → **Customers** → **Invoices**
2. Click **Create**
3. Fill in the invoice details:
   - **Customer**: Select a customer
   - **Invoice Date**: e.g., January 15, 2026
   - **Journal**: Select your newly created journal (e.g., "Customer Invoice - Goods Type")
   - **Goods Type**: Enter "01" (this is the new field)
   
4. Add invoice lines:
   - Click **Add a line**
   - Select product or enter description
   - Enter quantity and price

5. **IMPORTANT**: Before posting, set the sequence number manually:
   - Find the **Number** field (usually at the top of the form)
   - Enter your desired format: `AD-SI-L-2601-01-0001`
   - This establishes the pattern for all future invoices

6. Click **Confirm** to post the invoice

**Result**: Your first invoice will have the number `AD-SI-L-2601-01-0001`

### Creating SUBSEQUENT Invoices (Auto-Generated Sequences)

After the first invoice, all subsequent invoices will auto-generate their sequence numbers.

#### Example 1: Same Month, Same Goods Type

1. Create a new invoice
2. Set:
   - **Invoice Date**: January 20, 2026 (same month)
   - **Journal**: Same journal
   - **Goods Type**: "01" (same as before)
3. Add invoice lines
4. Click **Confirm**

**Result**: Sequence auto-generated as `AD-SI-L-2601-01-0002` (incremented)

#### Example 2: Same Month, Different Goods Type

1. Create a new invoice
2. Set:
   - **Invoice Date**: January 25, 2026 (same month)
   - **Journal**: Same journal
   - **Goods Type**: "02" (DIFFERENT!)
3. Add invoice lines
4. Click **Confirm**

**Result**: Sequence auto-generated as `AD-SI-L-2601-02-0001` (reset for new goods type)

#### Example 3: Different Month, Same Goods Type

1. Create a new invoice
2. Set:
   - **Invoice Date**: February 10, 2026 (DIFFERENT month)
   - **Journal**: Same journal
   - **Goods Type**: "01"
3. Add invoice lines
4. Click **Confirm**

**Result**: Sequence auto-generated as `AD-SI-L-2602-01-0001` (reset for new month)

---

## Understanding Sequence Behavior

### Sequence Reset Rules

The sequence resets when:
1. **Month Changes**: `2601` → `2602` (January to February)
2. **Goods Type Changes**: `01` → `02`

### Independent Counters

Each combination of **year-month-goods_type** has its own independent counter:
- `2601-01` → 0001, 0002, 0003...
- `2601-02` → 0001, 0002, 0003...
- `2602-01` → 0001, 0002, 0003...

### Complete Example Sequence

| Invoice | Date | Goods Type | Generated Sequence |
|---------|------|------------|--------------------|
| 1 | 2026-01-15 | 01 | AD-SI-L-2601-01-0001 |
| 2 | 2026-01-20 | 01 | AD-SI-L-2601-01-0002 |
| 3 | 2026-01-25 | 02 | AD-SI-L-2601-02-0001 |
| 4 | 2026-02-10 | 01 | AD-SI-L-2602-01-0001 |
| 5 | 2026-02-15 | 02 | AD-SI-L-2602-02-0001 |
| 6 | 2026-01-28 | 01 | AD-SI-L-2601-01-0003 |

Notice in invoice #6: even though it's created later, it continues the `2601-01` sequence because the date falls in January 2026 with goods type 01.

---

## Troubleshooting

### Error: "The sequence regex should at least contain the seq grouping keys"

**Problem**: The regex pattern is invalid or doesn't contain required groups.

**Solution**:
1. Go back to your journal configuration
2. Check the **Sequence Override Regex** field
3. Ensure it contains `(?P<seq>\d+)` at minimum
4. Use the recommended pattern:
```regex
^(?P<prefix1>.*?)(?P<year>\d{2})(?P<month>\d{2})(?P<prefix2>\D+?)(?P<goods_type>\w+)(?P<prefix3>\D+?)(?P<seq>\d+)(?P<suffix>\D*?)$
```

### Error: "The Journal Entry sequence is not conform to the current format"

**Problem**: You're trying to manually change the sequence number to a format that doesn't match the regex.

**Solutions**:
1. Ensure the number you enter matches the pattern defined in the regex
2. Check that all components are present (prefix, year, month, goods type, sequence)
3. Make sure year and month match the invoice date

### Goods Type Field Not Visible

**Problem**: The Goods Type field doesn't appear on the invoice form.

**Solutions**:
1. Verify the module is installed: **Apps** → Search "ADI Account Sequence"
2. Clear browser cache and reload
3. Check that you're creating an invoice (not a journal entry)
4. The field is hidden for journal entries (move_type='entry')

### Sequence Not Auto-Generating

**Problem**: Sequence shows as "/" even after setting goods type.

**Solutions**:
1. Ensure the first invoice was created with an explicit sequence number
2. Check that the journal has the correct **Sequence Override Regex**
3. Verify the goods type is set before posting
4. The sequence only generates when you click **Confirm** (post the invoice)

### Sequence Not Resetting for New Month/Goods Type

**Problem**: Sequence continues incrementing instead of resetting.

**Solutions**:
1. Check the regex pattern includes year and month groups
2. Verify the first invoice of the new period has the correct format
3. Ensure the goods_type field is properly set
4. Check that the invoice date is correct

---

## Advanced Tips

### Customizing the Format

You can customize the sequence format by modifying the regex pattern and the initial sequence.

**Example: 4-digit year instead of 2-digit**
```regex
^(?P<prefix1>.*?)(?P<year>\d{4})(?P<month>\d{2})(?P<prefix2>\D+?)(?P<goods_type>\w+)(?P<prefix3>\D+?)(?P<seq>\d+)(?P<suffix>\D*?)$
```
First invoice: `AD-SI-L-202601-01-0001`

**Example: Different prefix**
First invoice: `SALES-202601-A1-001`

**Example: Alphanumeric goods type**
Goods Type: "A1", "B2", "C3" instead of "01", "02", "03"

### Multiple Journals with Different Patterns

You can create multiple journals, each with its own sequence pattern:
- Sales Journal 1: `AD-SI-L-2601-01-0001`
- Sales Journal 2: `AD-SI-M-2601-01-0001`
- Export Sales: `EXP-2601-01-0001`

Each journal maintains independent sequences.

### Reporting and Filtering

You can search and filter invoices by goods type:
1. Go to **Accounting** → **Customers** → **Invoices**
2. Use **Filters** → **Add Custom Filter**
3. Filter by: `Goods Type` = `01`

---

## Best Practices

1. **Document Your Pattern**: Keep a record of your sequence format and what each component means
2. **Consistent Goods Types**: Establish a standard list of goods types (e.g., 01=Physical Goods, 02=Services)
3. **Test First**: Create test invoices in a test environment before using in production
4. **First Invoice**: Always carefully set the first invoice sequence to establish the pattern
5. **User Training**: Ensure all users understand how to set the goods type field
6. **Backup**: Backup your database before making journal configuration changes

---

## Support

For additional help:
- Check the README.md file in the module
- Review CUSTOM_SEQUENCE_FORMAT.md for technical details
- See example_goods_type_sequence.py for code examples
- Contact your Odoo administrator

---

## Summary

The ADI Account Sequence module provides powerful custom sequence formatting with automatic reset based on period and goods type. The key steps are:

1. **Install** the module
2. **Configure** journal with correct regex pattern
3. **Create** first invoice with explicit sequence number
4. **Set** goods type on each invoice
5. **Post** invoices to generate automatic sequences

The system handles the complexity of sequence generation, resetting, and management automatically once configured properly.
