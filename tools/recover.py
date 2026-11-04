"""Read legacy caches as data only. Never invoke PHP or instantiate serialized classes.

Usage: python3 tools/recover.py /path/to/private/extracted/var/www/pentagrama /path/to/private/output.json
The intermediate output is private and MUST NOT be committed. Public data is selected separately.
"""
import json
import sys
from pathlib import Path


class PHPData:
    def __init__(self, data):
        self.b = data
        self.i = 0

    def take(self, n):
        out = self.b[self.i:self.i+n]
        self.i += n
        if len(out) != n:
            raise ValueError('Truncated serialization')
        return out

    def expect(self, text):
        if self.take(len(text)) != text:
            raise ValueError(f'Invalid serialization at {self.i}')

    def until(self, char):
        end = self.b.index(char, self.i)
        out = self.b[self.i:end]
        self.i = end+1
        return out

    def read(self, depth=0):
        if depth > 30:
            raise ValueError('Serialization too deep')
        kind = self.take(1)
        if kind == b'N':
            self.expect(b';')
            return None
        self.expect(b':')
        if kind in (b'i', b'd', b'b'):
            value = self.until(b';')
            return float(value) if kind == b'd' else int(value)
        if kind == b's':
            n = int(self.until(b':'))
            self.expect(b'"')
            value = self.take(n).decode('utf-8', errors='replace')
            self.expect(b'";')
            return value
        if kind == b'O':
            n = int(self.until(b':'))
            self.expect(b'"')
            cls = self.take(n)
            self.expect(b'":')
            if cls != b'stdClass':
                raise ValueError('Non-data class refused')
        if kind in (b'a', b'O'):
            count = int(self.until(b':'))
            if count > 100000:
                raise ValueError('Array too large')
            self.expect(b'{')
            result = {}
            for _ in range(count):
                key = self.read(depth+1)
                value = self.read(depth+1)
                result[key] = value
            self.expect(b'}')
            return result
        raise ValueError(f'Unsupported serialization kind {kind}')


def walk(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from walk(item)


if __name__ == '__main__':
    root, output = map(Path, sys.argv[1:3])
    posts, failures, other = {}, [], []
    for path in (root/'wp-content/cache/db').rglob('*.php'):
        data = path.read_bytes()
        marker = data.find(b'?>')
        if marker < 0:
            continue
        try:
            result = PHPData(data[marker+2:]).read()
            for obj in walk(result.get('last_result', {})):
                if 'post_content' in obj and 'post_title' in obj and 'ID' in obj:
                    prev = posts.get(str(obj['ID']))
                    if not prev or obj.get('post_modified','') >= prev.get('post_modified',''):
                        posts[str(obj['ID'])] = obj
                elif any(k in obj for k in ['meta_key','taxonomy','term_id']):
                    other.append(obj)
        except (ValueError, IndexError, KeyError) as error:
            failures.append({'file':path.name,'reason':str(error)})
    output.write_text(json.dumps({'posts':list(posts.values()),'metadata':other,'failures':failures},ensure_ascii=False,indent=2))
    print(json.dumps({'posts':len(posts),'metadata':len(other),'failures':failures},ensure_ascii=False))
