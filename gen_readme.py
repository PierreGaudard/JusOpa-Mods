"""Regenere README.md a partir de mods.json."""
import os
from lib_mods import load, tag, dl_url, HUB

d = load()
repo = d['repo']
mods = [m for m in d['mods'] if m.get('listed', True)]
attente = [m for m in d['mods'] if not m.get('listed', True)]
inv = d.get('discord_invite') or ''

L = []
L.append('# JusOpa Mods')
L.append('')
L.append('Les mods Minecraft des shorts **JusOpa**. Un mod = un short.')
L.append('')
L.append(f'> Tous les mods ci-dessous tournent sur **Minecraft {d["mods"][0]["mc"]}** avec **Fabric**.')
L.append('')
if inv:
    L.append(f'Discord : {inv}')
    L.append('')
L.append('## Les mods')
L.append('')
L.append('| Mod | Ce que ca fait | Version | MC | Short | Telecharger |')
L.append('|---|---|---|---|---|---|')
for m in mods:
    short = f'[voir]({m["short"]})' if m.get('short') else '_a venir_'
    L.append(f'| {m["emoji"]} **{m["name"]}** | {m["tagline"]} | `{m["version"]}` | `{m["mc"]}` | {short} | [.jar]({dl_url(repo, m)}) |')
L.append('')
L.append('## Installation')
L.append('')
L.append('1. Installe **[Fabric Loader](https://fabricmc.net/use/installer/)** pour Minecraft `%s`' % d['mods'][0]['mc'])
L.append('2. Mets **[Fabric API](https://modrinth.com/mod/fabric-api)** dans ton dossier `mods`')
L.append('3. Mets le `.jar` du mod dans le meme dossier `mods`')
L.append('4. Lance Minecraft avec le profil Fabric')
L.append('')
L.append(r'> Dossier `mods` : `%APPDATA%\.minecraft\mods` sur Windows.')
L.append('')
L.append('Tu peux installer plusieurs mods en meme temps. Dans ce cas, prends aussi le **Control Panel** : la touche `F8` te laisse activer ou desactiver chaque mod en direct.')
L.append('')
L.append('## Details')
L.append('')
for m in mods:
    L.append(f'### {m["emoji"]} {m["name"]}')
    L.append('')
    L.append(m['description'])
    L.append('')
    L.append(f'- Version `{m["version"]}` pour Minecraft `{m["mc"]}` (Fabric)')
    if m.get('short'):
        L.append(f'- Short : {m["short"]}')
    L.append(f'- [Telecharger {m["jar"]}]({dl_url(repo, m)})')
    L.append('')
if attente:
    L.append('## Bientot')
    L.append('')
    for m in attente:
        L.append('%s **%s** : %s (short %s)' % (m['emoji'], m['name'], m['tagline'], m.get('eta', 'a venir')))
    L.append('')
L.append('---')
L.append('')
L.append('Mods sous licence MIT. Fais-en ce que tu veux.')
L.append('')

with open(os.path.join(HUB, 'README.md'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(L))
print('README.md regenere : %d mods visibles, %d en attente' % (len(mods), len(attente)))
