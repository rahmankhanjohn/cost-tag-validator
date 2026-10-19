#!/usr/bin/env python3
"""cost-tag-validator: check the 5-key taxonomy before finance asks.

The taxonomy from the cost per customer article:
  tenant_id    cust_88213        direct customer attribution
  environment  prod              split production from everything else
  service      checkout-api      which workload
  cost_center  eng-42            finance rollup
  owner        team-payments     accountability
  tenancy      shared|dedicated  shared resources need a split method

Checks every tagged resource for missing keys, inconsistent casing, and a
missing tenancy key, then reports how much of the estate is attributable.

Usage:
  cost-tag-validator.py [PATH] [--json] [--report]
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

REQUIRED = ['tenant_id', 'environment', 'service', 'cost_center', 'owner']
TENANCY_KEY = 'tenancy'
TENANCY_VALUES = ('shared', 'dedicated')
ENVIRONMENTS = ('prod', 'staging', 'dev')

SKIP_DIRS = {'.git', '.terraform', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build'}
CANDIDATES = ('tags', 'labels', 'commonLabels', 'tags_all', 'metadata.labels')


def _strip_quotes(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in '"\'':
        value = value[1:-1]
    return value


def extract_tag_blocks(text):
    """Pull simple key/value tag blocks out of Terraform, YAML or JSON-ish files."""
    blocks = []
    # JSON style: "tags": { "key": "value", ... }
    for match in re.finditer(r'"(?:tags|labels)"\s*:\s*\{([^{}]*)\}', text):
        pairs = dict(re.findall(r'"([^"]+)"\s*:\s*"([^"]*)"', match.group(1)))
        if pairs:
            blocks.append(pairs)
    # Terraform style: tags = { key = "value" }
    for match in re.finditer(r'tags\s*=\s*\{([^}]*)\}', text):
        pairs = dict(re.findall(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"([^"]*)"', match.group(1)))
        if pairs:
            blocks.append(pairs)
    # YAML style: a tags: block followed by indented key: value pairs
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if stripped.rstrip(':') in CANDIDATES and stripped.endswith(':'):
            indent = len(line) - len(line.lstrip())
            pairs = {}
            cursor = index + 1
            while cursor < len(lines):
                nxt = lines[cursor]
                if not nxt.strip():
                    cursor += 1
                    continue
                nxt_indent = len(nxt) - len(nxt.lstrip())
                if nxt_indent <= indent:
                    break
                if ':' in nxt:
                    key, _, value = nxt.strip().partition(':')
                    pairs[key.strip()] = _strip_quotes(value)
                cursor += 1
            if pairs:
                blocks.append(pairs)
            index = cursor
            continue
        index += 1
    return blocks


def validate_block(pairs):
    problems = []
    present = {k.lower(): v for k, v in pairs.items()}
    for key in REQUIRED:
        if key not in present:
            problems.append(('missing_key', key, 'no %s on this resource' % key))
    if TENANCY_KEY not in present:
        problems.append(('missing_key', TENANCY_KEY,
                         'no %s, shared resources need this to be split' % TENANCY_KEY))
    for key, value in present.items():
        if key == TENANCY_KEY:
            if value.lower() not in TENANCY_VALUES:
                problems.append(('bad_tenancy', key, '%s must be shared or dedicated' % key))
        if key == 'environment' and value.lower() not in ENVIRONMENTS:
            problems.append(('unknown_environment', key, '%s is not a known environment' % key))
        if value.strip() == '':
            problems.append(('empty_value', key, '%s is present but empty' % key))
    return present, problems


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(description='Validate the 5-key cost tagging taxonomy.')
    parser.add_argument('path', nargs='?', default='.', help='directory to scan')
    parser.add_argument('--json', action='store_true', help='machine-readable output')
    parser.add_argument('--report', action='store_true', help='one paste-ready summary line')
    args = parser.parse_args(argv)

    root = Path(args.path).resolve()
    resources = 0
    tagged = 0
    problems = []
    casing = {}

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d.lower() not in SKIP_DIRS]
        for filename in filenames:
            path = Path(dirpath) / filename
            try:
                text = path.read_text(encoding='utf-8', errors='ignore')
            except OSError:
                continue
            rel = str(path.relative_to(root)).replace('\\', '/')
            for pairs in extract_tag_blocks(text):
                resources += 1
                present, issues = validate_block(pairs)
                if issues:
                    problems.append({'file': rel, 'issues': issues})
                else:
                    tagged += 1
                for key, value in present.items():
                    if key in ('owner', 'cost_center', 'service', 'tenant_id'):
                        casing.setdefault(key, {}).setdefault(value.lower(), set()).add(value)

    case_conflicts = []
    for key, variants in casing.items():
        for lower, forms in variants.items():
            if len(forms) > 1:
                case_conflicts.append({'key': key, 'variants': sorted(forms)})

    attributable = 100.0 * tagged / resources if resources else 0.0
    summary = {
        'root': str(root),
        'resources_scanned': resources,
        'resources_fully_tagged': tagged,
        'attributable_percent': round(attributable, 1),
        'problems': problems,
        'case_conflicts': case_conflicts,
    }

    if args.json:
        print(json.dumps(summary, indent=2))
        return 1 if problems or case_conflicts else 0

    if args.report:
        parts = ['Cost tagging: %d of %d tagged resources carry the full 5-key taxonomy (%.0f%% attributable).'
                 % (tagged, resources, attributable)]
        if case_conflicts:
            parts.append('Case conflicts on %d keys, for example %s.'
                         % (len(case_conflicts),
                            ', '.join(c['variants'][0] + ' vs ' + c['variants'][1]
                                      for c in case_conflicts[:2])))
        if problems:
            parts.append('%d resources are missing keys.' % len(problems))
        parts.append('Checked %s.' % time.strftime('%Y-%m-%d'))
        parts.append('Tool: https://github.com/rahmankhanjohn/cost-tag-validator')
        print(' '.join(parts))
        return 1 if problems or case_conflicts else 0

    lines = []
    lines.append('Cost tag validator')
    lines.append('=' * 66)
    lines.append('  Path                    %s' % root)
    lines.append('  Tagged resources found  %d' % resources)
    lines.append('  Fully compliant         %d' % tagged)
    lines.append('  Attributable            %.0f%%' % attributable)
    lines.append('')
    if problems:
        lines.append('  Missing or invalid keys')
        for entry in problems[:25]:
            for kind, key, detail in entry['issues']:
                lines.append('    %s  %-16s %s  (%s)' % (entry['file'], key, detail, kind))
        if len(problems) > 25:
            lines.append('    ... and %d more' % (len(problems) - 25))
        lines.append('')
    if case_conflicts:
        lines.append('  Case conflicts (these split your reports)')
        for conflict in case_conflicts:
            lines.append('    %-12s %s' % (conflict['key'], ' vs '.join(conflict['variants'])))
        lines.append('')
    if not problems and not case_conflicts:
        lines.append('  No problems found. The taxonomy is applied consistently.')
        lines.append('')
    lines.append('  Shared resources need a split method agreed with finance,')
    lines.append('  then written down and applied the same way every month.')
    return 1 if problems or case_conflicts else 0


if __name__ == '__main__':
    sys.exit(main())
