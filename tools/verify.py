"""Structural checks only; not business acceptance tests or Kotlin compilation."""
from pathlib import Path
import json, re
r=Path(__file__).resolve().parents[1]
m=json.loads((r/'manifest.json').read_text())
src=r/'backend/src/main/kotlin/ca/cairn/carhms'
contracts=r/'backend/src/test/resources/contracts'
dtos=(src/'application/dtos/queries/Queries.kt').read_text()
checks=0
for key in m['subdomains']:
 p=src/'domain'/key/'README.md'
 assert p.is_file() and len(p.read_text())>100,p
 checks+=1
assert len(list((src/'domain').iterdir()))==7
assert len(list((src/'application/usecases').glob('*.kt')))==9
assert len(list(contracts.glob('*.feature')))==11
scenarios=0; examples=0
for cmd in m['commands']:
 source=(src/'application/usecases'/(cmd['interface']+'.kt')).read_text()
 assert f"fun {cmd['method']}(query: {cmd['dto']})" in source,cmd
 assert re.search(r'\bdata class '+cmd['dto']+r'\(',dtos),cmd
 f=contracts/(cmd['contract']+'.feature');t=f.read_text()
 assert t.startswith('# language: fr\n'),f
 assert '@'+cmd['method'] in t and '@'+cmd['usecase'] in t,f
 assert 'Fonctionnalité:' in t and 'Alors ' in t and 'Quand ' in t,f
 assert t.count('Fonctionnalité:')==1,f
 # Check table widths inside each contiguous block, placeholder substitution below.
 block=[]
 for line in t.splitlines()+['']:
  if line.strip().startswith('|'):block.append(line)
  elif block:
   widths=[len(x.split('|')) for x in block]
   assert len(set(widths))==1,(f,'table widths')
   block=[]
 for outline in re.split(r'  Plan du scénario:',t)[1:]:
  outline=outline.split('  Scénario:')[0]
  assert 'Exemples:' in outline,(f,'missing examples')
  body,rows=outline.split('Exemples:',1)
  header=next(x for x in rows.splitlines() if x.strip().startswith('|'))
  names={x.strip() for x in header.split('|')[1:-1]}
  assert set(re.findall(r'<([^>]+)>',body))<=names,(f,'placeholder')
 scenarios+=len(re.findall(r'^  (?:Scénario|Plan du scénario):',t,re.M))
 examples+=sum(1 for line in t.splitlines() if line.strip().startswith('|'))
 checks+=4
for excluded in ['SignIn','SignOut','GenerateTrailUsageReport']:
 assert not (src/'application/usecases'/(excluded+'.kt')).exists()
report=(r/'rapport/Livrable1_CAR-HMS.md').read_text()
for n in range(1,13):assert f'7. UC{n:02}' in report
for n in range(1,16):assert f'H{n:02}' in report
for n in range(1,6):assert f'B{n:02}' in report
for x in ['300389979','300371110']:assert x in report
print(f'OK: {checks} contrôles de correspondance; 7 sous-domaines, 9 interfaces, 11 commandes/DTO/contrats.')
print(f'OK: {scenarios} scénarios ou plans de scénario; tables et paramètres cohérents.')
print('OK: 12 analyses, 15 hypothèses, 5 observations bonus, 2 identités vérifiées.')
print('LIMITES: contrôle structurel; pas de compilation Kotlin ni de test fonctionnel Cucumber.')
