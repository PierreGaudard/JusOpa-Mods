"""Publie / met a jour les releases GitHub a partir de mods.json.

Usage:
  python publish.py            -> tous les mods
  python publish.py chained    -> seulement ce(s) mod(s)
"""
import os, sys
from lib_mods import load, tag, jar_path, dl_url, run

d = load()
repo = d['repo']
only = set(a.lower() for a in sys.argv[1:])
mods = [m for m in d['mods'] if not only or m['id'] in only or m['dir'].lower() in only]
if not mods:
    sys.exit('Aucun mod ne correspond a : %s' % ', '.join(only))

for m in mods:
    jar = jar_path(m)
    t = tag(m)
    if not os.path.exists(jar):
        print(f'[SKIP] {m["name"]} : jar introuvable -> {jar}')
        continue

    notes = [m['description'], '', f'**Minecraft `{m["mc"]}`** - Fabric Loader + Fabric API requis.']
    if m.get('short'):
        notes += ['', f'Short : {m["short"]}']
    notes += ['', 'Installation : depose le `.jar` dans ton dossier `mods`.']
    body = '\n'.join(notes)

    code, out, err = run(['gh', 'release', 'view', t, '--repo', repo])
    if code == 0:
        run(['gh', 'release', 'edit', t, '--repo', repo,
             '--title', f'{m["name"]} {m["version"]} (MC {m["mc"]})', '--notes', body])
        c, o, e = run(['gh', 'release', 'upload', t, jar, '--repo', repo, '--clobber'])
        print(f'[MAJ ] {m["name"]} -> {t}' if c == 0 else f'[ERR ] {m["name"]} : {e}')
    else:
        c, o, e = run(['gh', 'release', 'create', t, jar, '--repo', repo,
                       '--title', f'{m["name"]} {m["version"]} (MC {m["mc"]})', '--notes', body])
        print(f'[NEW ] {m["name"]} -> {t}' if c == 0 else f'[ERR ] {m["name"]} : {e}')
    print(f'       {dl_url(repo, m)}')
