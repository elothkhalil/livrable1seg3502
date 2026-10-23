# Validation effectuée le 22 octobre 2026

## Résultats
- **Structure et traçabilité : succès.** `python3 tools/verify.py` : 51 contrôles de correspondance, 7 sous-domaines avec README, 9 interfaces et 11 fonctions, 11 requêtes racines et 11 fonctionnalités associées.
- **Couverture documentaire : succès.** 12 cas d’utilisation avec préconditions, étapes et postconditions; 15 hypothèses et exactement 5 observations bonus; deux noms et numéros étudiants intégrés.
- **Compilation Kotlin : succès pour les 11 fichiers de signatures.** Les 11 fichiers `.kt` de domaine et d’application ont été compilés directement avec le compilateur Kotlin JVM 2.0.21 disponible dans le cache Gradle local, sous JDK 21.0.2, avec une cible JVM 17. Aucune erreur de compilation. Ce contrôle ne constitue pas une exécution du build Gradle ni du serveur Spring Boot. La classe `CarHmsApplication` et le build Spring Boot ajoutés ensuite n’ont pas encore été compilés : Gradle n’est pas installé sur ce poste.
- **Syntaxe Cucumber : succès.** Parseur officiel `gherkin-official` 42.0.1; les 11 fonctionnalités en français sont analysées puis développées en **101 scénarios** (42 scénarios simples ou plans de scénario avant expansion).
- **PDF : succès.** 25 pages générées avec ReportLab, extraites avec pypdf et rendues avec Poppler. Inspection visuelle des pages : tableaux, diagramme, accents, marges, retours et numéros de page. Aucun débordement constaté.

## Reproduction du contrôle Gherkin
Installer le parseur dans un environnement Python de validation avec `python3 -m pip install gherkin-official==42.0.1`, puis exécuter :

```python
from pathlib import Path
from gherkin.parser import Parser
from gherkin.pickles.compiler import Compiler

count = 0
for path in Path('backend/src/test/resources/contracts').glob('*.feature'):
    document = Parser().parse(path.read_text(encoding='utf-8'))
    document['uri'] = str(path)
    count += len(Compiler().compile(document))
assert count == 101
print('11 fonctionnalités valides, 101 scénarios développés')
```

## Limites et éléments restant à fournir
Les fonctionnalités sont des contrats initiaux, sans définitions de pas ni implémentation métier; les scénarios ne sont donc pas déclarés réussis fonctionnellement. Les interfaces compilent mais n’implémentent pas les comportements.

Couverture et contributions mises à jour : aucun nom d’équipe distinct; professeur Kalenji Kalala; tâches individuelles et travail commun renseignés selon la répartition approuvée par les membres. Le dossier est intégré au dépôt GitHub de l’équipe : https://github.com/elothkhalil/livrable1seg3502. La note finale dépend de l’évaluateur et de la remise complète selon les règles du cours.
