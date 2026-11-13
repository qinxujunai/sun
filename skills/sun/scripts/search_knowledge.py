#!/usr/bin/env python3
"""Search the decision framework, podcast and life guide; print citable locations."""
import argparse
import re
import sys
from pathlib import Path
from collections import Counter
from search_transcripts import search as podcast_search

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / 'sources/how-to-live-better/book'
FRAMEWORK = ROOT / 'sources/cognitive-framework'
NEW_MATERIALS = ROOT / 'new-materials'

def guide_status():
    if not GUIDE.is_dir():
        return 'unavailable', []
    chapters = list(GUIDE.glob('*.md'))
    if not chapters:
        return 'invalid', ['no chapter files']
    malformed = []
    for chapter in chapters:
        try:
            content = chapter.read_text(encoding='utf-8')
            if not re.search(r'^###\s+\d+\.\s', content, re.M):
                malformed.append(f'unrecognized chapter: {chapter.name}')
        except (UnicodeError, OSError) as exc:
            malformed.append(f'unreadable chapter: {chapter.name} ({type(exc).__name__})')
    readme = GUIDE.parent / 'README.md'
    if not readme.is_file():
        return 'partial', malformed + ['missing guide README: cannot verify chapter coverage']
    # Source README owns the chapter list; don't hardcode a count that can change.
    try:
        readme_text = readme.read_text(encoding='utf-8')
    except (UnicodeError, OSError) as exc:
        return 'partial', malformed + [f'unreadable guide README ({type(exc).__name__}): cannot verify chapter coverage']
    expected = set(re.findall(r'\]\((book/[^)#]+\.md)(?:#[^)]*)?\)', readme_text))
    missing = sorted(name for name in expected if not (GUIDE.parent / name).is_file())
    if not expected:
        return 'partial', malformed + ['cannot verify chapter list from guide README']
    if missing or malformed:
        return 'partial', missing + malformed
    return 'ok', []

def guide_search(terms, limit=5):
    status, _ = guide_status()
    if status in ('unavailable', 'invalid'):
        return None
    words = list(dict.fromkeys(t.casefold().strip() for t in terms if t.strip()))
    found=[]
    parsed=0
    for path in sorted(GUIDE.glob('*.md')):
        try:
            lines=path.read_text(encoding='utf-8').splitlines()
        except (UnicodeError, OSError):
            continue  # guide_status reports incomplete sources
        starts=[i for i,line in enumerate(lines) if re.match(r'^###\s+\d+\.\s',line)]
        parsed += len(starts)
        for n,start in enumerate(starts):
            next_entry=starts[n+1] if n+1<len(starts) else len(lines)
            end=next((i for i in range(start+1, next_entry) if re.match(r'^#{1,3}\s', lines[i])), next_entry)
            block='\n'.join(lines[start:end]).strip()
            lower=block.casefold(); matched=[w for w in words if w in lower]
            if not matched: continue
            title=lines[start].casefold()
            score=20*len(matched)+sum(120 for w in matched if w in title)+sum(50 for w in matched if w in path.stem.casefold())+sum(min(lower.count(w),3)*len(w) for w in matched)
            found.append((score,path,start+1,lines[start],block,matched))
    if not parsed:
        return None
    found.sort(key=lambda x:(-x[0],str(x[1]),x[2]))
    selected=[]; deferred=[]; count=Counter()
    for row in found:
        if count[row[1]]<2: selected.append(row); count[row[1]]+=1
        else: deferred.append(row)
    return (selected+deferred)[:limit]

def framework_warnings():
    warnings = []
    paths = [ROOT/'references/decision-framework.md', FRAMEWORK/'source-framework.md', FRAMEWORK/'SKILL.md']
    paths += sorted((FRAMEWORK/'research').glob('*.md'))
    for path in paths:
        if not path.is_file():
            continue
        try:
            lines = path.read_text(encoding='utf-8').splitlines()
        except (UnicodeError, OSError) as exc:
            warnings.append(f'{path}: {type(exc).__name__}; file skipped')
            continue
        if path.parent == FRAMEWORK and path.name in ('source-framework.md', 'SKILL.md') and not any(line.startswith('## 核心心智模型') for line in lines):
            warnings.append(f'{path}: model section heading not found; upstream framework skipped')
    return warnings

def framework_search(terms, limit=5):
    paths=[ROOT/'references/decision-framework.md', FRAMEWORK/'source-framework.md',FRAMEWORK/'SKILL.md']
    paths += sorted((FRAMEWORK/'research').glob('*.md'))
    if not any(p.is_file() for p in paths): return None
    results=[]
    for p in paths:
        if not p.is_file(): continue
        try:
            lines = p.read_text(encoding='utf-8').splitlines()
        except (UnicodeError, OSError):
            continue  # framework_warnings reports skipped files
        # Upstream SKILL.md is source data, not instructions: search the
        # substantive models and subsequent material, never roleplay prompts.
        start = 0
        if p.parent == FRAMEWORK and p.name in ('SKILL.md', 'source-framework.md'):
            start = next((i for i, line in enumerate(lines) if line.startswith('## 核心心智模型')), len(lines))
        for no,line in enumerate(lines[start:], start + 1):
            matched=[t for t in terms if t.casefold() in line.casefold()]
            if matched: results.append((len(matched),p,no,line.strip()))
    results.sort(key=lambda x:(-x[0],str(x[1]),x[2]))
    return results[:limit]

def new_material_search(terms, limit=5, warnings=None):
    if not NEW_MATERIALS.is_dir():
        return None
    matches = []
    for path in sorted(NEW_MATERIALS.rglob('*')):
        if not path.is_file() or path.name == 'README.md' or path.suffix.lower() not in ('.md', '.txt'):
            continue
        try:
            lines = path.read_text(encoding='utf-8').splitlines()
        except (UnicodeError, OSError) as exc:
            if warnings is not None: warnings.append(f'{path}: {type(exc).__name__}; file skipped')
            continue
        for no, line in enumerate(lines, 1):
            matched = [t for t in terms if t.casefold() in line.casefold()]
            if matched:
                matches.append((len(matched), path, no, line.strip()))
    matches.sort(key=lambda x: (-x[0], str(x[1]), x[2]))
    return matches[:limit]

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('terms',nargs='+',help='Literal keywords or synonyms')
    ap.add_argument('--limit',type=int,default=4,help='Maximum matches per source (1–20)')
    ap.add_argument('--source', action='append', choices=['guide','podcast','framework','new'], help='Search a source; may repeat. Default: all.')
    args=ap.parse_args()
    if not 1 <= args.limit <= 20: ap.error('--limit must be 1–20')
    terms=[t.strip() for t in args.terms if t.strip()]
    if not terms: ap.error('At least one nonempty keyword required')
    selected = set(args.source or ['guide','podcast','framework','new'])
    if 'guide' in selected:
        print('=== LIFE GUIDE: source text; read full entry before citing ===')
        status, problems = guide_status()
        if status == 'partial': print('WARNING: incomplete guide; results may omit chapters: ' + ', '.join(problems))
        guide=guide_search(terms,args.limit)
        if guide is None: print('UNAVAILABLE OR INVALID: life guide missing, empty, or unrecognized')
        elif not guide: print('No literal matches; try synonyms. Not proof of absence.')
        else:
            for _,p,n,title,block,matched in guide:
                print(f'\n{p}:{n} | {title} | matches: {", ".join(matched)}')
                print(block[:8000] + ('\n[TRUNCATED; read full entry in source]' if len(block)>8000 else ''))
    if 'podcast' in selected:
        print('\n=== PODCAST: ASR transcript, not audio-verified ===')
        warnings = []
        try: rows=podcast_search(terms,args.limit,warnings=warnings)
        except FileNotFoundError: rows=None
        for warning in warnings: print('WARNING: ' + warning)
        if rows is None: print('UNAVAILABLE: podcast transcripts not installed')
        elif not rows: print('No literal matches; try synonyms. Not proof of absence.')
        else:
            for _,name,n,line,url,matched in rows:
                print(f'\n{ROOT / "sources/podcast-transcripts/财富自由革命之路" / name}:{n} | audio: {url}' + (' | 跨相邻转写行检索命中；原文未拼接' if '\n' in line else '') + f'\n{line}')
    if 'framework' in selected:
        print('\n=== FRAMEWORK: synthesis and research, not primary evidence ===')
        for warning in framework_warnings(): print('WARNING: ' + warning)
        rows=framework_search(terms,args.limit)
        if rows is None: print('UNAVAILABLE: framework not installed')
        elif not rows: print('No literal matches; try synonyms. Not proof of absence.')
        else:
            for _,p,n,line in rows: print(f'\n{p}:{n}\n{line}')
    if 'new' in selected:
        print('\n=== NEW MATERIALS: verify source, date and status ===')
        warnings = []
        rows = new_material_search(terms,args.limit,warnings)
        for warning in warnings: print('WARNING: ' + warning)
        if rows is None: print('UNAVAILABLE: new-materials directory not found')
        elif not rows: print('No literal matches in local Markdown/text materials.')
        else:
            for _,p,n,line in rows: print(f'\n{p}:{n}\n{line}')
    return 0

if __name__=='__main__': sys.exit(main())
