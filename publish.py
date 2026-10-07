"""Publie / met a jour les releases GitHub a partir de mods.json.

Un mod "listed": false part en brouillon : la release existe, le jar est
dedans, mais rien n'est visible publiquement tant que le short n'est pas sorti.

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
    sys.exit('Aucun mod ne correspond a : ' + ', '.join(only))

for m in mods:
    jar, t = jar_path(m), tag(m)
    listed = m.get('listed', True)
    if not os.path.exists(jar):
        print('[SKIP] {} : jar introuvable -> {}'.format(m['name'], jar))
        continue

    notes = [m['description'], '',
             '**Minecraft `{}`** sous Fabric. Fabric Loader + Fabric API requis.'.format(m['mc'])]
    if m.get('short'):
        notes += ['', 'Le short : ' + m['short']]
    notes += ['', 'Installation : depose le `.jar` dans ton dossier `mods`.']
    body = '\n'.join(notes)
    title = '{} {} (MC {})'.format(m['name'], m['version'], m['mc'])
    draft = ['--draft=true'] if not listed else ['--draft=false']

    if run(['gh', 'release', 'view', t, '--repo', repo])[0] == 0:
        c, _, e = run(['gh', 'release', 'edit', t, '--repo', repo,
                       '--title', title, '--notes', body] + draft)
        if c == 0:
            c, _, e = run(['gh', 'release', 'upload', t, jar, '--repo', repo, '--clobber'])
        verbe = 'MAJ '
    else:
        c, _, e = run(['gh', 'release', 'create', t, jar, '--repo', repo,
                       '--title', title, '--notes', body] + (['--draft'] if not listed else []))
        verbe = 'NEW '

    if c != 0:
        print('[ERR ] {} : {}'.format(m['name'], e))
        continue
    print('[{}] {} -> {}{}'.format(verbe, m['name'], t, '' if listed else '  (BROUILLON)'))
    if listed:
        print('       ' + dl_url(repo, m))
