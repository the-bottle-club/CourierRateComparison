#!/usr/bin/env python3
"""
sync_rates.py
=============
Reads courier rate tables from the .md files in the rates/ directory
and regenerates rates/courier-data.js.

Run this from the "Courier Comparison" folder whenever you edit a .md file:

    python sync_rates.py

The HTML dashboard imports courier-data.js and uses its RATE_DATA object,
so all tables, insight cards and the calculator will reflect the new rates
immediately when you reload the page.
"""

import re
import os
from datetime import date

RATES_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rates')
OUTPUT_FILE = os.path.join(RATES_DIR, 'courier-data.js')

BANDS = ['0-2', '2-3', '3-15', '15-20', '20-30']


def norm(text):
    """Normalise unicode dashes and strip £ sign for easier parsing."""
    return (text
            .replace('\u2013', '-')   # en dash
            .replace('\u2014', '-')   # em dash
            .replace('\u2212', '-')   # minus sign
            .replace('\u00a3', ''))   # £


def read_md(filename):
    path = os.path.join(RATES_DIR, filename)
    with open(path, encoding='utf-8') as f:
        return f.read()


# ---------------------------------------------------------------------------
# Section extraction — line-based (avoids f-string/regex curly-brace conflicts)
# ---------------------------------------------------------------------------

def get_section(content, heading_prefix, stop_prefixes=None):
    """
    Return the text under a heading that starts with `heading_prefix`,
    stopping when a line starts with any prefix in `stop_prefixes`.
    The heading line itself is not included in the result.
    """
    if stop_prefixes is None:
        stop_prefixes = ['## ']
    lines = content.split('\n')
    in_section = False
    result = []
    for line in lines:
        stripped = line.strip()
        if not in_section:
            if stripped.startswith(heading_prefix):
                in_section = True
        else:
            if any(stripped.startswith(p) for p in stop_prefixes):
                break
            result.append(line)
    return '\n'.join(result)


def get_subsection(content, heading_prefix):
    """Return text under a ### heading, stopping at the next ## or ### heading."""
    return get_section(content, heading_prefix, stop_prefixes=['## ', '### '])


# ---------------------------------------------------------------------------
# Table parsers
# ---------------------------------------------------------------------------

BAND_MAP = {
    '0-2kg':   '0-2',
    '2-3kg':   '2-3',
    '3-15kg':  '3-15',
    '15-20kg': '15-20',
    '20-30kg': '20-30',
}


def parse_band_table(text):
    """
    Parse a markdown table where rows contain an HTML weight band and a price.

    Accepts tables like:
        | HTML Weight Band | Rate |
        | 0-2kg            | 4.80 |

    Returns dict: { '0-2': 4.80, ... }   Bands with N/A map to None.
    """
    rates = {}
    for line in norm(text).split('\n'):
        if not line.startswith('|'):
            continue
        parts = [p.strip() for p in line.split('|') if p.strip()]
        if not parts or '---' in parts[0]:
            continue
        # Skip header rows
        if 'Weight Band' in parts[0] or 'Service' in parts[0] or 'HTML' in parts[0]:
            continue
        for band_label, band_key in BAND_MAP.items():
            if band_label in norm(parts[0]):
                price = None
                for cell in parts[1:]:
                    cell_n = norm(cell)
                    if re.search(r'\bN/?A\b', cell_n, re.IGNORECASE):
                        price = None
                        break
                    m = re.search(r'(\d+\.\d+|\d+)', cell_n)
                    if m:
                        price = float(m.group(1))
                        break
                rates[band_key] = price
    return rates


# ---------------------------------------------------------------------------
# Per-courier parsers
# ---------------------------------------------------------------------------

def parse_evri():
    content = read_md('evri.md')
    std_section = get_section(content, '## Standard 48 Rates')
    nd_section  = get_section(content, '## Next Day (24hr) Rates')
    return {
        'evri_std': parse_band_table(std_section),
        'evri_nd':  parse_band_table(nd_section),
    }


def parse_dpd():
    content = read_md('dpd.md')
    # The flat rate offer subsection is inside the Next Day Rates section
    section = get_section(content, '## Next Day Rates')
    flat_section = get_subsection(section, '### Revised Flat Rate Offer')
    if not flat_section:
        # Fallback: parse the whole Next Day Rates section
        flat_section = section
    return {
        'dpd_nd': parse_band_table(flat_section),
    }


def parse_dhl():
    content = read_md('dhl.md')
    # Heading starts with '## Standard Rates' — use prefix match
    std_section = get_section(content, '## Standard Rates')
    return {
        'dhl_nd': parse_band_table(std_section),
    }


INPOST_BAND_MAP = {
    'Small':  ['0-2', '2-3'],
    'Medium': ['3-15'],
    'Large':  ['15-20', '20-30'],
}


def parse_inpost_table(text):
    """Parse an InPost-style markdown table (Small/Medium/Large bands, price in last column)."""
    rates = {}
    for line in norm(text).split('\n'):
        if not line.startswith('|'):
            continue
        parts = [p.strip() for p in line.split('|') if p.strip()]
        if not parts or '---' in parts[0] or 'Weight Band' in parts[0]:
            continue
        for size, js_bands in INPOST_BAND_MAP.items():
            if size in parts[0]:
                # Price is always in the last column for InPost tables
                price = None
                last_cell = norm(parts[-1])
                if re.search(r'\bN/?A\b', last_cell, re.IGNORECASE):
                    price = None
                else:
                    m = re.search(r'(\d+\.\d+)', last_cell)  # must have decimal (e.g. 1.93)
                    if m:
                        price = float(m.group(1))
                for b in js_bands:
                    rates[b] = price
    return rates


def parse_inpost():
    content = read_md('inpost.md')
    # Standard rates
    inject_section  = get_subsection(content, '### Injected')
    collect_section = get_subsection(content, '### Collection')

    # Next day rates — base prices are in "### Base Prices" under "## Next Day Rates"
    nd_base_section = get_subsection(content, '### Base Prices')
    nd_inject = parse_inpost_table(nd_base_section)
    # Collection adds £0.24 per parcel on top of the inject base price
    nd_collect = {
        k: round(v + 0.24, 2) if v is not None else None
        for k, v in nd_inject.items()
    }

    return {
        'inpost_inject':    parse_inpost_table(inject_section),
        'inpost_collect':   parse_inpost_table(collect_section),
        'inpost_nd_inject': nd_inject,
        'inpost_nd_collect': nd_collect,
    }


def parse_royal_mail():
    content = read_md('royal-mail.md')
    proposed_section = get_section(content, '## Proposed Rates')

    t48, t24 = {}, {}
    for line in norm(proposed_section).split('\n'):
        if not line.startswith('|'):
            continue
        parts = [p.strip() for p in line.split('|') if p.strip()]
        if len(parts) < 3 or '---' in parts[0] or 'Service' in parts[0]:
            continue
        service   = parts[0]
        band_raw  = norm(parts[1])
        rate_cell = norm(parts[2])

        band_key = BAND_MAP.get(band_raw)
        if not band_key:
            continue

        if re.search(r'\bN/?A\b', rate_cell, re.IGNORECASE):
            price = None
        else:
            m = re.search(r'(\d+\.\d+|\d+)', rate_cell)
            price = float(m.group(1)) if m else None

        if 'Tracked 48' in service:
            t48[band_key] = price
        elif 'Tracked 24' in service:
            t24[band_key] = price

    return {'rm_t48': t48, 'rm_t24': t24}


# ---------------------------------------------------------------------------
# Generate courier-data.js
# ---------------------------------------------------------------------------

def fmt_rate(v):
    if v is None:
        return 'null'
    return f'{v:.2f}'


def build_js(all_rates):
    today = date.today().isoformat()
    source_comments = {
        'inpost_inject':     '// -- InPost -- source: rates/inpost.md',
        'inpost_collect':    None,
        'inpost_nd_inject':  '// -- InPost Next Day (indicative) -- source: rates/inpost.md',
        'inpost_nd_collect': None,
        'evri_std':          '// -- Evri (via MHI) -- source: rates/evri.md',
        'evri_nd':           None,
        'rm_t48':            '// -- Royal Mail -- source: rates/royal-mail.md',
        'rm_t24':            None,
        'dpd_nd':            '// -- DPD -- source: rates/dpd.md',
        'dhl_nd':            '// -- DHL eCommerce -- source: rates/dhl.md',
    }
    keys_order = ['inpost_inject', 'inpost_collect',
                  'inpost_nd_inject', 'inpost_nd_collect',
                  'evri_std', 'evri_nd',
                  'rm_t48', 'rm_t24', 'dpd_nd', 'dhl_nd']

    lines = [
        '// ============================================================',
        '//  COURIER RATE DATA',
        '//  AUTO-GENERATED by sync_rates.py -- do not edit by hand.',
        '//',
        '//  To update: edit a .md file in this folder, then run:',
        '//      python sync_rates.py',
        '//  from the "Courier Comparison" directory.',
        '//',
        '//  Source files:',
        '//    rates/inpost.md',
        '//    rates/royal-mail.md',
        '//    rates/evri.md',
        '//    rates/dpd.md',
        '//    rates/dhl.md',
        '//',
        f'//  Last synced: {today}',
        '// ============================================================',
        '',
        'const RATE_DATA = {',
        '',
    ]

    for key in keys_order:
        comment = source_comments.get(key)
        if comment:
            lines.append(f'  {comment}')
        rates = all_rates.get(key, {})
        band_entries = ', '.join(
            "'" + b + "': " + fmt_rate(rates.get(b)) for b in BANDS
        )
        lines.append(f'  {key}: {{ {band_entries} }},')
        lines.append('')

    lines.append('};')
    lines.append('')
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print('sync_rates.py -- syncing MD files to courier-data.js\n')

    all_rates = {}
    ok = True

    parsers = [
        ('InPost',     parse_inpost),
        ('Royal Mail', parse_royal_mail),
        ('Evri',       parse_evri),
        ('DPD',        parse_dpd),
        ('DHL',        parse_dhl),
    ]

    for name, parser in parsers:
        try:
            result = parser()
            for key, rates in result.items():
                if not rates:
                    print(f'  WARNING  {name} ({key}): no rates parsed -- check MD file structure')
                    ok = False
                else:
                    vals = {k: v for k, v in rates.items()}
                    print(f'  OK       {name} ({key}): {vals}')
            all_rates.update(result)
        except FileNotFoundError as e:
            print(f'  ERROR    {name}: file not found -- {e}')
            ok = False
        except Exception as e:
            import traceback
            print(f'  ERROR    {name}: {e}')
            traceback.print_exc()
            ok = False

    print()
    if not ok:
        print('Completed with warnings -- review the output above.')
    else:
        print('All couriers parsed successfully.')

    js = build_js(all_rates)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(js)

    print(f'Written: {OUTPUT_FILE}')
    print('Reload the HTML dashboard in your browser to see the updated rates.')


if __name__ == '__main__':
    main()
