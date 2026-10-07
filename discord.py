"""Poste les fiches mods dans Discord via webhook.

Le webhook est lu dans webhook.txt (jamais commite).
Les mods "listed": false sont ignores (short pas encore en ligne).

Usage:
  python discord.py              -> toutes les fiches visibles
  python discord.py chained      -> seulement ce(s) mod(s)
  python discord.py --index      -> le message recapitulatif
  python discord.py --all        -> inclut aussi les mods non sortis
"""
import json, os, sys, urllib.request
from lib_mods import load, dl_url, HUB

WH = os.path.join(HUB, 'webhook.txt')
if not os.path.exists(WH):
    sys.exit("Cree webhook.txt avec l'URL du webhook Discord dedans.")
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

args = sys.argv[1:]
force = '--all' in args
args = [a for a in args if a != '--all']
visible = lambda m: force or m.get('listed', True)

if '--index' in args:
    lines = []
    for m in d['mods']:
        if not visible(m):
            continue
        block = '{} **{}**\n{}\n[Telecharger le .jar]({})'.format(
            m['emoji'], m['name'], m['tagline'], dl_url(repo, m))
        if m.get('short'):
            block += '\n[Voir le short]({})'.format(m['short'])
        lines.append(block)
    post({'embeds': [{
        'title': 'Les mods JusOpa',
        'description': '\n\n'.join(lines),
        'color': COLOR,
        'footer': {'text': 'Minecraft {} sous Fabric. Toutes les versions sur github.com/{}/releases'.format(
            d['mods'][0]['mc'], repo)}}]})
    print('[OK] index poste')
    sys.exit(0)

only = set(a.lower() for a in args)
if only:
    mods = [m for m in d['mods'] if m['id'] in only or m['dir'].lower() in only]
    inconnus = only - {m['id'] for m in mods} - {m['dir'].lower() for m in mods}
    if inconnus:
        sys.exit('Mod inconnu : ' + ', '.join(sorted(inconnus)))
else:
    mods = [m for m in d['mods'] if visible(m)]

for m in mods:
    fields = [
        {'name': 'Version', 'value': '`{}`'.format(m['version']), 'inline': True},
        {'name': 'Minecraft', 'value': '`{}` sous Fabric'.format(m['mc']), 'inline': True},
    ]
    if m.get('short'):
        fields.append({'name': 'Le short', 'value': '[Regarder]({})'.format(m['short']), 'inline': True})
    post({'embeds': [{
        'title': '{} {}'.format(m['emoji'], m['name']),
        'url': m.get('short') or 'https://github.com/{}'.format(repo),
        'description': m['description'],
        'color': COLOR,
        'fields': fields + [{'name': 'Telechargement',
                             'value': '[{}]({})'.format(m['jar'], dl_url(repo, m))}],
        'footer': {'text': 'Fabric Loader + Fabric API requis. Depose le .jar dans ton dossier mods.'}}]})
    print('[OK] {} poste'.format(m['name']))
