# -*- coding: utf-8 -*-
from datetime import date
from odoo import api, fields, models
from odoo.tools import date_utils
import re


class SequenceMixin(models.AbstractModel):
    """Extension of sequence.mixin to support goods_type field in sequences."""
    
    _inherit = 'sequence.mixin'

    # Add goods_type regex pattern
    goods_type = r'(?P<goods_type>\w+)'
    
    # Add new monthly goods_type regex pattern
    _sequence_monthly_goods_type_regex = property(lambda self: 
        fr'^{self.prefix}{self.year}{self.month}(?P<prefix2>\D+?){self.goods_type}(?P<prefix3>\D+?){self.seq}{self.suffix}$'
    )

    def _get_sequence_date_range(self, reset):
        """Override to support month_goods_type reset type."""
        ref_date = fields.Date.to_date(self[self._sequence_date_field])
        if reset in ('year', 'year_range', 'year_range_month'):
            return (date(ref_date.year, 1, 1), date(ref_date.year, 12, 31), None, None)
        if reset in ('month', 'month_goods_type'):
            return date_utils.get_month(ref_date) + (None, None)
        if reset == 'never':
            return (date(1, 1, 1), date(9999, 12, 31), None, None)
        return super()._get_sequence_date_range(reset)

    @api.model
    def _deduce_sequence_number_reset(self, name):
        """Override to recognize month_goods_type pattern."""
        # Check for month_goods_type pattern first (before month pattern)
        for regex, ret_val, requirements in [
            (self._sequence_year_range_monthly_regex, 'year_range_month', ['seq', 'year', 'year_end', 'month']),
            (self._sequence_monthly_goods_type_regex, 'month_goods_type', ['seq', 'month', 'year', 'goods_type']),
            (self._sequence_monthly_regex, 'month', ['seq', 'month', 'year']),
            (self._sequence_year_range_regex, 'year_range', ['seq', 'year', 'year_end']),
            (self._sequence_yearly_regex, 'year', ['seq', 'year']),
            (self._sequence_fixed_regex, 'never', ['seq']),
        ]:
            match = re.match(regex, name or '')
            if match:
                groupdict = match.groupdict()
                if (
                    groupdict.get('year_end') and groupdict.get('year')
                    and (
                        len(groupdict['year']) < len(groupdict['year_end'])
                        or self._truncate_year_to_length((int(groupdict['year']) + 1), len(groupdict['year_end'])) != int(groupdict['year_end'])
                    )
                ):
                    # year and year_end are not compatible for range (the difference is not 1)
                    continue
                if all(groupdict.get(req) is not None for req in requirements):
                    return ret_val
        return super()._deduce_sequence_number_reset(name)

    def _get_sequence_format_param(self, previous):
        """Override to handle goods_type in format parameters."""
        sequence_number_reset = self._deduce_sequence_number_reset(previous)
        regex = self._sequence_fixed_regex
        if sequence_number_reset == 'year':
            regex = self._sequence_yearly_regex
        elif sequence_number_reset == 'year_range':
            regex = self._sequence_year_range_regex
        elif sequence_number_reset == 'month':
            regex = self._sequence_monthly_regex
        elif sequence_number_reset == 'month_goods_type':
            regex = self._sequence_monthly_goods_type_regex
        elif sequence_number_reset == 'year_range_month':
            regex = self._sequence_year_range_monthly_regex
        
        format_values = re.match(regex, previous).groupdict()
        format_values['seq_length'] = len(format_values['seq'])
        format_values['year_length'] = len(format_values.get('year') or '')
        format_values['year_end_length'] = len(format_values.get('year_end') or '')
        
        if not format_values.get('seq') and 'prefix1' in format_values and 'suffix' in format_values:
            format_values['prefix1'] = format_values['suffix']
            format_values['suffix'] = ''
        
        for field in ('seq', 'year', 'month', 'year_end'):
            format_values[field] = int(format_values.get(field) or 0)
        
        # Keep goods_type as string
        if 'goods_type' in format_values and format_values['goods_type'] is not None:
            format_values['goods_type'] = str(format_values['goods_type'])
        else:
            format_values['goods_type'] = ''

        placeholders = re.findall(r'\b(prefix\d|seq|suffix\d?|year|year_end|month|goods_type)\b', regex)
        format = ''.join(
            "{seq:0{seq_length}d}" if s == 'seq' else
            "{month:02d}" if s == 'month' else
            "{year:0{year_length}d}" if s == 'year' else
            "{year_end:0{year_end_length}d}" if s == 'year_end' else
            "{goods_type}" if s == 'goods_type' else
            "{%s}" % s
            for s in placeholders
        )
        return format, format_values

    def _get_next_sequence_format(self):
        """Override to handle goods_type value population."""
        last_sequence = self._get_last_sequence()
        new = not last_sequence
        if new:
            last_sequence = self._get_last_sequence(relaxed=True) or self._get_starting_sequence()

        format_string, format_values = self._get_sequence_format_param(last_sequence)
        
        # Check if goods_type changed - if so, treat as new sequence
        if self._should_reset_sequence_for_goods_type(format_values):
            new = True
        
        if new:
            sequence_number_reset = self._deduce_sequence_number_reset(last_sequence)
            date_start, date_end, forced_year_start, forced_year_end = self._get_sequence_date_range(sequence_number_reset)
            format_values['seq'] = 0
            format_values['year'] = self._truncate_year_to_length(forced_year_start or date_start.year, format_values['year_length'])
            format_values['year_end'] = self._truncate_year_to_length(forced_year_end or date_end.year, format_values['year_end_length'])
            format_values['month'] = self[self._sequence_date_field].month
        
        # Populate goods_type from the record if it has this field and it's in the format
        if 'goods_type' in format_values and hasattr(self, 'goods_type'):
            format_values['goods_type'] = self.goods_type or format_values.get('goods_type', '')
        
        return format_string, format_values

    def _should_reset_sequence_for_goods_type(self, format_values):
        """Check if the sequence should be reset due to goods_type change.
        
        :param format_values: dict of format values extracted from previous sequence
        :return: True if sequence should reset, False otherwise
        """
        if 'goods_type' not in format_values:
            return False
        if not hasattr(self, 'goods_type') or not self.goods_type:
            return False
        previous_goods_type = format_values.get('goods_type')
        return previous_goods_type and previous_goods_type != self.goods_type
