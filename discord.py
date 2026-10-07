"""Poste les fiches mods dans Discord via webhook.

Le webhook est lu dans webhook.txt (jamais commite).
Usage:
  python discord.py              -> poste tous les mods
  python discord.py chained      -> poste seulement ce(s) mod(s)
  python discord.py --index      -> poste le message d'index (liste de tout)
"""
import json, os, sys, urllib.request
from lib_mods import load, dl_url, HUB

WH = os.path.join(HUB, 'webhook.txt')
if not os.path.exists(WH):
    sys.exit('Cree webhook.txt avec l\'URL du webhook Discord dedans.')
url = open(WH, encoding='utf-8').read().strip()

d = load()
repo = d['repo']
COLOR = 0x57F287

def post(payload):
    req = urllib.request.Request(
        url + '?wait=true',
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json', 'User-Agent': 'JusOpaModsHub/1.0'})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode('utf-8'))

args = [a for a in sys.argv[1:]]

if '--index' in args:
    lines = []
    for m in d['mods']:
        s = f' - [le short]({m["short"]})' if m.get('short') else ''
        lines.append(f'{m["emoji"]} **{m["name"]}** - {m["tagline"]}\n[Telecharger]({dl_url(repo, m)}){s}')
    post({'embeds': [{
        'title': 'Tous les mods JusOpa',
        'description': '\n\n'.join(lines),
        'color': COLOR,
        'footer': {'text': f'Minecraft {d["mods"][0]["mc"]} - Fabric | Toutes les versions : github.com/{repo}/releases'}}]})
    print('[OK] index poste')
    sys.exit(0)

only = set(a.lower() for a in args)
mods = [m for m in d['mods'] if not only or m['id'] in only or m['dir'].lower() in only]
for m in mods:
    fields = [
        {'name': 'Version', 'value': f'`{m["version"]}`', 'inline': True},
        {'name': 'Minecraft', 'value': f'`{m["mc"]}` (Fabric)', 'inline': True},
    ]
    if m.get('short'):
        fields.append({'name': 'Le short', 'value': f'[Regarder]({m["short"]})', 'inline': True})
    post({'embeds': [{
        'title': f'{m["emoji"]} {m["name"]}',
        'url': m.get('short') or f'https://github.com/{repo}',
        'description': m['description'],
        'color': COLOR,
        'fields': fields + [{'name': 'Telechargement', 'value': f'[{m["jar"]}]({dl_url(repo, m)})'}],
        'footer': {'text': 'Fabric Loader + Fabric API requis - depose le .jar dans ton dossier mods'}}]})
    print(f'[OK] {m["name"]} poste')
