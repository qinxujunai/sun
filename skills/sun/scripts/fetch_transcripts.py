#!/usr/bin/env python3
"""Download transcripts from their upstream repository to this local installation."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'sources' / 'podcast-transcripts' / '财富自由革命之路'
UPSTREAM = 'https://github.com/diverHansun/justin-sun-podcast-markdown.git'


def main():
    if TARGET.exists():
        count = len(list(TARGET.glob('*.md'))) if TARGET.is_dir() else 0
        if count:
            print(f'播客目录已存在（{count} 个 Markdown 文件），保留现有资料，不覆盖：{TARGET}')
            return 0
        print(f'目标路径已存在但没有逐字稿，请检查后重试：{TARGET}', file=sys.stderr)
        return 1
    try:
        with tempfile.TemporaryDirectory(prefix='sun-podcast-') as temp:
            checkout = Path(temp) / 'upstream'
            subprocess.run(['git', 'clone', '--depth', '1', '--', UPSTREAM, str(checkout)], check=True)
            source = checkout / '财富自由革命之路'
            files = sorted(source.glob('*.md'))
            if not files or any(p.is_symlink() for p in files):
                raise ValueError('上游逐字稿目录为空或包含符号链接')
            TARGET.parent.mkdir(parents=True, exist_ok=True)
            # Copy only Markdown regular files; do not execute upstream code or copy its .git.
            TARGET.mkdir()
            try:
                for file in files:
                    shutil.copy2(file, TARGET / file.name)
            except Exception:
                shutil.rmtree(TARGET)
                raise
            revision = subprocess.check_output(['git', '-C', str(checkout), 'rev-parse', 'HEAD'], text=True).strip()
            print(f'已从 {UPSTREAM} 导入 {len(files)} 个逐字稿（版本 {revision}）：{TARGET}')
            print('自动转写可能有误；重要引用请对照原音频。')
        return 0
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        print(f'获取播客失败：{exc}。请检查网络，或手动使用 import_transcripts.py 导入。', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
