#!/usr/bin/env python3
"""Check repository-local documentation links and image alt text, offline."""
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []
        self.missing_alt = 0

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag in {'a', 'img', 'source'}:
            target = attrs.get('href' if tag == 'a' else 'src')
            if target:
                self.targets.append(target)
        if tag == 'img' and not attrs.get('alt', '').strip():
            self.missing_alt += 1


def main():
    errors, checked = [], 0
    for path in sorted(ROOT.rglob('*.md')):
        if any(part in {'.git', 'dist', 'work', 'runs', '__pycache__'} for part in path.relative_to(ROOT).parts):
            continue
        text = path.read_text(encoding='utf-8')
        parser = Links()
        parser.feed(text)
        targets = parser.targets + re.findall(r'\]\(([^)\n]+)\)', text)
        if parser.missing_alt:
            errors.append(f'{path.relative_to(ROOT)}: {parser.missing_alt} image(s) without alt text')
        for alt in re.findall(r'!\[([^]]*)\]\(', text):
            if not alt.strip():
                errors.append(f'{path.relative_to(ROOT)}: Markdown image without alt text')
        for target in targets:
            parts = urlsplit(target)
            if parts.scheme or parts.netloc or not parts.path or target.startswith('<'):
                continue
            relative = unquote(parts.path)
            destination = ROOT / relative.lstrip('/') if relative.startswith('/') else path.parent / relative
            if not destination.exists():
                errors.append(f'{path.relative_to(ROOT)}: missing {relative}')
            checked += 1
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'Documentation checks passed: {checked} local links; image alt text present')
    return 0


if __name__ == '__main__':
    sys.exit(main())
