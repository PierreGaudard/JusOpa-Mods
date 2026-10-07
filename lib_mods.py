import json, os, subprocess, sys

HUB = os.path.dirname(os.path.abspath(__file__))
MCDEV = os.path.dirname(HUB)

def load():
    with open(os.path.join(HUB, 'mods.json'), encoding='utf-8') as f:
        return json.load(f)

def save(d):
    with open(os.path.join(HUB, 'mods.json'), 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
        f.write('\n')

def tag(m):
    return f"{m['id']}-v{m['version']}"

def jar_path(m):
    return os.path.join(MCDEV, m['dir'], 'build', 'libs', m['jar'])

def dl_url(repo, m):
    return f"https://github.com/{repo}/releases/download/{tag(m)}/{m['jar']}"

def run(args, **kw):
    r = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace', **kw)
    return r.returncode, (r.stdout or '').strip(), (r.stderr or '').strip()
