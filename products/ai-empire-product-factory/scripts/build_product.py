#!/usr/bin/env python3
"""
AI Empire Product Factory
Turns a Gold Nugget into a shippable product package.

Usage:
    python3 scripts/build_product.py --input inputs/GOLD_*.md
"""

import argparse
import re
from pathlib import Path
from datetime import datetime


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help='Path to Gold Nugget markdown file')
    parser.add_argument('--out', default='outputs', help='Output directory')
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f'Input not found: {input_path}')
        return 1

    text = input_path.read_text(encoding='utf-8')

    # Extract title from first heading
    title = 'Untitled Product'
    for line in text.split('\n'):
        if line.startswith('# '):
            title = line[2:].strip()
            break

    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    out_dir = Path(args.out) / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    # TODO: run Strategist, Copywriter, Pricing, Web Builder, GTM agents
    # For now, scaffold the package
    (out_dir / 'PRODUCT.md').write_text(f'# {title}\n\n(TODO: generate from factory)\n', encoding='utf-8')
    (out_dir / 'landing-page').mkdir(exist_ok=True)
    (out_dir / 'landing-page/LANDING_PAGE.md').write_text(f'# Landing Page: {title}\n\n(TODO)\n', encoding='utf-8')

    print(f'Factory output: {out_dir}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
