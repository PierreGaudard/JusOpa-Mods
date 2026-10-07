"""Poste les fiches mods dans Discord via webhook.

Un message independant par mod, avec la miniature de son short.
Les mods "listed": false sont ignores : tant que le short n'est pas sorti,
rien ne doit apparaitre, pas meme une annonce.

Les ids des messages postes sont gardes dans messages.json, ce qui permet de
modifier une fiche en place au lieu d'en poster une deuxieme.

Usage:
  python discord.py               -> poste ou met a jour toutes les fiches visibles
  python discord.py chained       -> seulement ce(s) mod(s)
  python discord.py --repost      -> force un nouveau message au lieu de modifier
  python discord.py --supprime X  -> supprime la fiche du mod X
"""
import json, os, sys, urllib.request, urllib.error
from lib_mods import load, dl_url, HUB

WH = os.path.join(HUB, 'webhook.txt')
IDS = os.path.join(HUB, 'messages.json')
if not os.path.exists(WH):
    sys.exit("Cree webhook.txt avec l'URL du webhook Discord dedans.")
url = open(WH, encoding='utf-8').read().strip()

d = load()
repo = d['repo']
COLOR = 0x57F287

ids = json.load(open(IDS, encoding='utf-8')) if os.path.exists(IDS) else {}
def save_ids():
    json.dump(ids, open(IDS, 'w', encoding='utf-8'), indent=2)

def call(method, suffix='', payload=None):
    req = urllib.request.Request(
        url + suffix,
        data=json.dumps(payload).encode('utf-8') if payload is not None else None,
        headers={'Content-Type': 'application/json', 'User-Agent': 'JusOpaModsHub/1.0'},
        method=method)
    with urllib.request.urlopen(req) as r:
        body = r.read().decode('utf-8')
    return json.loads(body) if body else {}

def video_id(short_url):
    """Extrait l'id YouTube d'une URL de short."""
    return short_url.rstrip('/').split('/')[-1].split('?')[0]

def fiche(m):
    fields = [
        {'name': 'Version', 'value': '`{}`'.format(m['version']), 'inline': True},
        {'name': 'Minecraft', 'value': '`{}` sous Fabric'.format(m['mc']), 'inline': True},
    ]
    if m.get('short'):
        fields.append({'name': 'Le short', 'value': '[Regarder]({})'.format(m['short']), 'inline': True})
    fields.append({'name': 'Telechargement',
                   'value': '[{}]({})'.format(m['jar'], dl_url(repo, m))})
    embed = {
        'title': '{} {}'.format(m['emoji'], m['name']),
        'url': m.get('short') or 'https://github.com/{}'.format(repo),
        'description': m['description'],
        'color': COLOR,
        'fields': fields,
        'footer': {'text': 'Fabric Loader + Fabric API requis. Depose le .jar dans ton dossier mods.'},
    }
    if m.get('short'):
        embed['image'] = {'url': 'https://i.ytimg.com/vi/{}/maxresdefault.jpg'.format(video_id(m['short']))}
    return {'embeds': [embed]}

args = sys.argv[1:]
repost = '--repost' in args
args = [a for a in args if a != '--repost']

if '--supprime' in args:
    for key in args[args.index('--supprime') + 1:]:
        mid = ids.pop(key, None)
        if not mid:
            print('[SKIP] aucune fiche connue pour ' + key)
            continue
        try:
            call('DELETE', '/messages/' + mid)
            print('[OK] fiche ' + key + ' supprimee')
        except urllib.error.HTTPError as e:
            print('[OK] fiche ' + key + ' deja absente' if e.code == 404 else '[ERR] ' + key + ' : ' + str(e))
    save_ids()
    sys.exit(0)

only = set(a.lower() for a in args)
if only:
    mods = [m for m in d['mods'] if m['id'] in only or m['dir'].lower() in only]
    inconnus = only - {m['id'] for m in mods} - {m['dir'].lower() for m in mods}
    if inconnus:
        sys.exit('Mod inconnu : ' + ', '.join(sorted(inconnus)))
else:
    mods = [m for m in d['mods'] if m.get('listed', True)]

for m in mods:
    payload = fiche(m)
    mid = None if repost else ids.get(m['id'])
    try:
        msg = call('PATCH', '/messages/' + mid, payload) if mid else call('POST', '?wait=true', payload)
        print('[MAJ ] {}'.format(m['name']) if mid else '[NEW ] {}'.format(m['name']))
    except urllib.error.HTTPError as e:
        if mid and e.code == 404:
            msg = call('POST', '?wait=true', payload)
            print('[NEW ] {} (l ancien message avait ete supprime)'.format(m['name']))
        else:
            raise
    ids[m['id']] = msg['id']
save_ids()
