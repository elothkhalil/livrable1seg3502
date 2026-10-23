# CAR-HMS - Livrable 1

## Contenu
- `rapport/Livrable1_CAR-HMS.pdf` : rapport final à relire avant remise.
- `rapport/Livrable1_CAR-HMS.md` : texte modifiable du même rapport.
- `rapport/contexte.svg` : diagramme de contexte vectoriel.
- `backend/src/main/kotlin/ca/cairn/carhms/domain/` : 7 sous-domaines documentés.
- `backend/src/main/kotlin/ca/cairn/carhms/application/usecases/` : 9 interfaces, 11 fonctions.
- `backend/src/main/kotlin/ca/cairn/carhms/application/dtos/queries/` : requêtes d'application.
- `backend/src/test/resources/contracts/` : 11 fonctionnalités Cucumber en français.
- `tools/verify.py` : contrôle structurel reproductible, sans dépendance tierce.
- `tools/generate.py` : source de génération du dossier et du PDF (Python + ReportLab).
- `VALIDATION.md` : contrôles effectués et limites.

## Informations de remise
Professeur : Kalenji Kalala. Aucun nom d’équipe distinct. Les identités, numéros étudiants et contributions des deux membres sont intégrés au rapport. Valider les hypothèses avec le client/enseignant.

## Vérification
Depuis ce dossier : `python3 tools/verify.py`.
Pour compiler le squelette si Gradle et JDK 17 sont installés : `cd backend` puis `gradle compileKotlin`. Les dépendances doivent pouvoir être téléchargées. Aucun wrapper Gradle n'est inclus; ne pas annoncer une compilation locale si elle n'a pas été exécutée.

Il s'agit de contrats initiaux : aucune définition de pas Cucumber ni implémentation métier n'est incluse. Les contrats ne sont pas des tests fonctionnels exécutables à ce stade. Le build Gradle sert seulement à compiler les signatures Kotlin.

## Dépôt
Le code est publié sur la branche `main` du dépôt de l'équipe : https://github.com/elothkhalil/livrable1seg3502. Le dossier `backend` contient la structure et les contrats à évaluer; le dossier `rapport` contient le document. Aucun secret ni fichier personnel du workspace n'est inclus.

## Mise à jour du rapport
Modifier `tools/generate.py`, puis exécuter `python3 tools/generate.py` avec ReportLab. Une modification du Markdown seul ne modifie pas automatiquement le PDF. Vérifier ensuite le PDF rendu. Les PDF sources restent dans Downloads et ne sont pas redistribués dans l'archive.
