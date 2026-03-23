"""Patch transformers is_gguf_available() to handle version 'N/A'"""
path = '/usr/local/lib/python3.10/dist-packages/transformers/utils/import_utils.py'
with open(path) as f:
    c = f.read()
old = 'return is_available and version.parse(gguf_version) >= version.parse(min_version)'
new = """try:
        return is_available and version.parse(gguf_version) >= version.parse(min_version)
    except Exception:
        return is_available"""
if old in c:
    c = c.replace(old, new)
    with open(path, 'w') as f:
        f.write(c)
    print('Patched is_gguf_available in import_utils.py')
else:
    print('Already patched or pattern not found')
