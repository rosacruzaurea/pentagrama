"""Parse a mysqldump as inert data, reading only editorial tables.

No database service or SQL/PHP execution. Output is private staging data.
"""
import collections
import json
import re
import sys
from pathlib import Path

TABLES = {'wp_posts','wp_postmeta','wp_terms','wp_term_taxonomy','wp_term_relationships'}
META_KEYS = {'_thumbnail_id','_wp_attached_file','_wp_attachment_image_alt',
             '_downloadable_files','_price','_regular_price','_downloadable','_product_url'}


def values(s, pos):
    escapes = {'0':'\0','n':'\n','r':'\r','t':'\t','Z':'\x1a'}
    while pos < len(s):
        while s[pos].isspace() or s[pos] == ',':
            pos += 1
        if s[pos] == ';':
            return
        if s[pos] != '(':
            raise ValueError(f'Expected row at {pos}')
        pos += 1
        row = []
        while True:
            while s[pos].isspace():
                pos += 1
            if s[pos] == "'":
                pos += 1
                parts = []
                start = pos
                while True:
                    if s[pos] == '\\':
                        parts.append(s[start:pos])
                        pos += 1
                        parts.append(escapes.get(s[pos], s[pos]))
                        pos += 1
                        start = pos
                    elif s[pos] == "'":
                        parts.append(s[start:pos])
                        pos += 1
                        if s[pos] == "'":
                            parts.append("'")
                            pos += 1
                            start = pos
                            continue
                        break
                    else:
                        pos += 1
                row.append(''.join(parts))
            else:
                start = pos
                while s[pos] not in ',)':
                    pos += 1
                item = s[start:pos].strip()
                row.append(None if item == 'NULL' else item)
            while s[pos].isspace():
                pos += 1
            if s[pos] == ')':
                pos += 1
                break
            if s[pos] != ',':
                raise ValueError('Invalid delimiter')
            pos += 1
        yield row


def load(path):
    s = path.read_text(encoding='utf-8', errors='strict')
    schemas = {}
    for m in re.finditer(r'^CREATE TABLE(?: IF NOT EXISTS)? `([^`]+)` \((.*?)\) ENGINE',s,re.S|re.M):
        if m[1] in TABLES:
            schemas[m[1]] = re.findall(r'^  `([^`]+)`',m[2],re.M)
    result = {t:[] for t in TABLES}
    counts = collections.Counter()
    for m in re.finditer(r'^INSERT INTO `([^`]+)`(?: \(([^;]*?)\))? VALUES\s*',s,re.M):
        table = m[1]
        if table not in TABLES:
            continue
        columns = re.findall(r'`([^`]+)`',m[2]) if m[2] else schemas[table]
        for row in values(s,m.end()):
            if len(row) != len(columns):
                raise ValueError(f'Column mismatch in {table}')
            obj = dict(zip(columns,row))
            counts[table] += 1
            if table == 'wp_posts':
                if obj['post_type'] not in {'post','page','product','attachment'}:
                    continue
                if obj['post_status'] not in {'publish','inherit'} or obj['post_password']:
                    continue
                obj = {k:obj[k] for k in ['ID','post_date','post_modified','post_content','post_title','post_excerpt','post_name','post_type','post_status','post_parent','guid','menu_order','post_mime_type']}
            if table == 'wp_postmeta' and obj['meta_key'] not in META_KEYS:
                continue
            result[table].append(obj)
    return result, dict(counts)


if __name__ == '__main__':
    result, counts = load(Path(sys.argv[1]))
    Path(sys.argv[2]).write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps({'rows_read':counts,'selected':{k:len(v) for k,v in result.items()},'post_types':dict(collections.Counter(x['post_type'] for x in result['wp_posts']))},ensure_ascii=False))
