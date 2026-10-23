# CAR-HMS - Livrable 1 : domaine initial

SEG 3102 · Automne 2026 · Équipe CAR-HMS

## Contenu
- `rapport/Livrable1_CAR-HMS.pdf` : rapport du livrable.
- `rapport/Livrable1_CAR-HMS.md` : version texte du rapport.
- `rapport/contexte.svg` : diagramme de contexte.
- `backend/src/main/kotlin/ca/cairn/carhms/domain/` : 7 sous-domaines, chacun avec un README.
- `backend/src/main/kotlin/ca/cairn/carhms/application/usecases/` : 9 interfaces, 11 commandes.
- `backend/src/main/kotlin/ca/cairn/carhms/application/dtos/queries/` : DTO de requête.
- `backend/src/test/resources/contracts/` : 11 contrats Cucumber en français.
- `tools/verify.py` : contrôle de cohérence entre commandes, DTO et contrats.

## Vérification
`python3 tools/verify.py`

Compilation (JDK 17 et Gradle) : `cd backend` puis `gradle compileKotlin`.

Les contrats sont des spécifications initiales : aucune définition de pas Cucumber ni logique métier n'est incluse à cette étape.
