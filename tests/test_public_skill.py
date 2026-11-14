import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class PublicSkillTest(unittest.TestCase):
    def test_missing_then_imported_transcripts_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            skill = base / 'sun'
            shutil.copytree(ROOT / 'skills' / 'sun', skill)
            shutil.rmtree(skill / 'sources' / 'podcast-transcripts', ignore_errors=True)
            query = [sys.executable, str(skill / 'scripts' / 'search_knowledge.py'), '示例原话', '--source', 'podcast']
            before = subprocess.run(query, capture_output=True, text=True, check=True).stdout
            self.assertIn('UNAVAILABLE', before)
            transcripts = base / 'transcripts'
            transcripts.mkdir()
            (transcripts / '001-示例.md').write_text('source: "https://example.org/video"\n## Raw Transcript\n[00:00:01] 示例原话。\n', encoding='utf-8')
            command = [sys.executable, str(skill / 'scripts' / 'import_transcripts.py'), str(transcripts)]
            subprocess.run(command, capture_output=True, text=True, check=True)
            after = subprocess.run(query, capture_output=True, text=True, check=True).stdout
            self.assertIn('[00:00:01]', after)
            self.assertIn('示例原话', after)
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual((skill / 'sources' / 'podcast-transcripts' / '财富自由革命之路' / '001-示例.md').read_text(encoding='utf-8'), (transcripts / '001-示例.md').read_text(encoding='utf-8'))

    def test_guide_works_without_private_podcast(self):
        cmd = [sys.executable, str(ROOT / 'skills' / 'sun' / 'scripts' / 'search_knowledge.py'), '创业', '--source', 'guide', '--limit', '1']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
        self.assertIn('12-创业与做生意.md', result)
        self.assertNotIn('UNAVAILABLE', result)

    def test_framework_works_after_clean_install_from_another_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            skill = Path(temp) / 'sun'
            shutil.copytree(ROOT / 'skills' / 'sun', skill)
            # Git does not store empty directories, so emulate a clean checkout.
            shutil.rmtree(skill / 'sources' / 'cognitive-framework', ignore_errors=True)
            result = subprocess.run(
                [sys.executable, str(skill / 'scripts' / 'search_knowledge.py'), '路径匹配', '--source', 'framework'],
                cwd=temp, capture_output=True, text=True, check=True,
            ).stdout
            self.assertIn('decision-framework.md', result)
            self.assertIn('路径匹配', result)
            self.assertNotIn('UNAVAILABLE', result)
