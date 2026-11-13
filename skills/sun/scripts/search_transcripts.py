#!/usr/bin/env python3
"""Search raw transcript passages by literal keywords; no external dependencies."""
import argparse
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / 'sources' / 'podcast-transcripts' / '财富自由革命之路'

def search(terms, limit=10, episode=None, warnings=None):
    files = sorted(CORPUS.glob('*.md'))
    if not files:
        raise FileNotFoundError(f'No transcripts found: {CORPUS}')
    if episode is not None:
        if not re.fullmatch(r'\d{1,3}', episode):
            raise ValueError('Episode must be a number from 0 to 999')
        files = [p for p in files if p.name.startswith(episode.zfill(3) + '-')]
    terms = list(dict.fromkeys(t.casefold().strip() for t in terms if t.strip()))
    if not terms:
        raise ValueError('At least one nonempty literal keyword is required')
    matches = []
    valid_files = []
    for path in files:
        try:
            lines = path.read_text(encoding='utf-8').splitlines()
        except (UnicodeError, OSError) as exc:
            if warnings is not None: warnings.append(f'{path}: {type(exc).__name__}; file skipped')
            continue
        try:
            start = lines.index('## Raw Transcript') + 1
        except ValueError:
            if warnings is not None: warnings.append(f'{path}: missing Raw Transcript; file skipped')
            continue
        end = next((i for i in range(start, len(lines)) if lines[i].startswith('## ')), len(lines))
        if not any(re.match(r'^\[\d{2}:\d{2}(?::\d{2})?\]', line) for line in lines[start:end]):
            if warnings is not None: warnings.append(f'{path}: no timestamped raw transcript; file skipped')
            continue
        valid_files.append((path, lines))
    for path, lines in valid_files:
        in_raw = False
        url = ''
        for num, line in enumerate(lines, 1):
            if line.startswith('source:') and not url:
                url = line.partition(':')[2].strip().strip('\"\'')
            if line.strip() == '## Raw Transcript':
                in_raw = True
                continue
            if in_raw and line.startswith('## '):
                break
            if not in_raw or not line.strip():
                continue
            text = line.casefold()
            matched = [t for t in terms if t in text]
            if matched:
                score = len(matched) * 100 + sum(min(text.count(t), 3) * len(t) for t in matched)
                matches.append((score, path.name, num, line.strip(), url, matched))
    # ASR slices sometimes split a phrase across adjacent timestamped lines.
    # Normalize punctuation only at the joining boundary for matching; return
    # both original lines unchanged so callers can verify the transcript.
    for path, lines in valid_files:
        url = next((line.partition(':')[2].strip().strip('"\'') for line in lines if line.startswith('source:')), '')
        in_raw = False
        previous = None
        for num, line in enumerate(lines, 1):
            if line.strip() == '## Raw Transcript':
                in_raw = True
                continue
            if in_raw and line.startswith('## '):
                break
            if not in_raw or not re.match(r'^\[\d{2}:\d{2}(?::\d{2})?\]', line):
                previous = None
                continue
            if previous and previous[0] == num - 1:
                prev_num, prev_line = previous
                left = re.sub(r'^\[[^]]+\]\s*', '', prev_line).rstrip(' 。！？；，、,.!?;:：')
                right = re.sub(r'^\[[^]]+\]\s*', '', line).lstrip(' 。！？；，、,.!?;:：')
                joined = (left + right).casefold()
                crossed = [term for term in terms if term in joined and term not in left.casefold() and term not in right.casefold()]
                if crossed:
                    matches.append((100 * len(crossed), path.name, prev_num, prev_line.strip() + '\n' + line.strip(), url, crossed))
            previous = (num, line)
    matches.sort(key=lambda x: (-x[0], x[1], x[2]))
    # First show a spread of episodes, then fill remaining slots with additional
    # passages when only a few episodes contain the requested terms.
    selected, deferred, counts = [], [], {}
    for row in matches:
        name = row[1]
        if counts.get(name, 0) < 2:
            selected.append(row)
            counts[name] = counts.get(name, 0) + 1
        else:
            deferred.append(row)
    return (selected + deferred)[:limit]

def main():
    parser = argparse.ArgumentParser(description='Literal OR search of timestamped raw transcript lines; provide short Chinese or English keywords as separate arguments.')
    parser.add_argument('terms', nargs='+', help='Literal keyword(s), matched case-insensitively')
    parser.add_argument('--limit', type=int, default=10)
    parser.add_argument('--episode', help='Restrict search to one episode number, e.g. 84')
    args = parser.parse_args()
    if not 1 <= args.limit <= 100:
        parser.error('--limit must be between 1 and 100')
    try:
        warnings = []
        rows = search(args.terms, args.limit, args.episode, warnings=warnings)
        for warning in warnings: print('WARNING: ' + warning)
    except (FileNotFoundError, ValueError) as exc:
        print(exc, file=sys.stderr); return 2
    if not rows:
        print('No literal matches. Try synonyms and search the research files separately; no match does not prove absence.')
        return 0
    for score, filename, line, text, url, matched in rows:
        print(f'\n{CORPUS / filename}:{line}\nMatched: {", ".join(matched)} | source: {url}' + (' | cross-line match; original lines below' if '\n' in text else '') + f'\n{text}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
