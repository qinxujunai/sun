#!/usr/bin/env python3
"""Import an existing local transcript folder into the installed skill."""
import argparse
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source', type=Path, help='Directory containing episode Markdown files')
args = parser.parse_args()
source = args.source.expanduser().resolve()
target = root / 'sources' / 'podcast-transcripts' / '财富自由革命之路'
if not source.is_dir() or not list(source.glob('*.md')):
    parser.error('Source must be a directory containing transcript Markdown files')
if target.exists():
    parser.error(f'Target already exists; no files were overwritten: {target}')
if root in source.parents or source == root:
    parser.error('Source must be outside this skill directory')
target.parent.mkdir(parents=True, exist_ok=True)
shutil.copytree(source, target, symlinks=False)
print(f'Imported {len(list(target.glob("*.md")))} Markdown files to {target}')
