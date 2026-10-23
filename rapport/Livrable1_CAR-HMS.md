# CAR-HMS - Livrable 1 : Analyse initiale du domaine

Système de gestion des événements de randonnée du Club Cairn

SEG 3102 · Automne 2026

Date de préparation : 22 octobre 2026

Professeur : Kalenji Kalala

| Membre | Numéro étudiant |
| --- | --- |
| Mohamed Khalil EL OTHMANI | 300389979 |
| Mohamed Khalil Mehdaoui | 300371110 |

Analyse initiale du domaine et contrats applicatifs. Les décisions d’analyse sont identifiées comme hypothèses, sans être attribuées au client.


# 2. Sommaire exécutif et équipe


## 2.1 Sommaire exécutif

Ce document s’adresse au client Cairn, à l’équipe de développement et à l’évaluateur du cours; il fixe la portée, les hypothèses et le modèle initial du domaine CAR-HMS. Il décrit les interactions externes, justifie sept sous-domaines, détaille les douze cas d’utilisation et relie neuf interfaces Kotlin et onze contrats Cucumber aux règles métier, puis présente cinq observations de revue des exigences.


## 2.2 Description de l’équipe et des rôles

| Membre | Travail réellement effectué pour ce livrable |
| --- | --- |
| Mohamed Khalil EL OTHMANI 300389979 | Analyse des exigences, hypothèses et revue des contradictions; diagramme de contexte et classification des sous-domaines; rédaction et mise en forme du rapport. |
| Mohamed Khalil Mehdaoui 300371110 | Structure des paquetages du domaine; interfaces Kotlin et DTO; rédaction des contrats Cucumber et vérification de leur correspondance avec les commandes. |

Travail commun aux deux membres : analyse des cas d’utilisation, vérification de la cohérence entre rapport et code et relecture finale. Aucun pourcentage ni nombre d’heures n’est indiqué; ces renseignements sont facultatifs dans les consignes.


## 2.3 Portée et pièces livrées

Inclus : consultation, compte sur invitation, profil et habilitation, planification, inscriptions/attente, notifications et statistiques. Exclus : recrutement, émission des invitations, processus complet d’adhésion, ressources humaines, activités physiques et suivi des présences. Les données CCN demeurent la référence externe.

Le dossier backend contient uniquement le squelette du domaine, les contrats d’application et les fonctionnalités Cucumber demandés. Le produit final utilisera Angular/TypeScript et Kotlin/Spring Boot; aucune interface Web ni implémentation Spring Boot n’est requise pour ce livrable initial [R1, §2.3; R2, §2].


## 2.4 Guide de lecture

Sections 3 à 6 : décisions et modèle de haut niveau. Section 7 : douze fiches de cas d’utilisation. Section 8 : revue bonus distincte des hypothèses. Section 9 : traçabilité et conformité. Section 10 : références et points à confirmer.


# 3. Hypothèses (1/2)


## H01 · Inscription initiale publique

L’enregistrement par invitation et la connexion sont des exceptions nécessaires à l’exigence générale d’authentification. Le code est validé contre une source fournie au système, consommé une seule fois et n’est pas émis par CAR-HMS.


## H02 · Difficulté et admissibilité

On associe débutant/facile=1, intermédiaire/modéré=2, avancé/difficile=3, expert/très difficile=4. Un membre de niveau n peut participer à toute randonnée de niveau d ≤ min(4,n+1), y compris les niveaux inférieurs. Le chef doit avoir un niveau ≥ d.


## H03 · Complet reste accessible

La recherche par défaut montre les événements ouverts. Un filtre réservé aux utilisateurs connectés permet d’inclure les événements complets encore avant échéance pour rejoindre leur liste d’attente. Les détails par identifiant appliquent la même règle : ouverts publics, complets authentifiés.


## H04 · Automatismes et audit

Un ordonnanceur interne ferme les inscriptions à l’échéance, envoie les rappels et marque la terminaison au début de la randonnée. Chaque transition consigne l’auteur humain ou SYSTEM, la cause, l’heure et les anciens/nouveaux états.


## H05 · Bornes temporelles

Les instants sont stockés en UTC et présentés dans America/Toronto. Début futur; durée et capacité entières strictement positives. Création avant l’échéance; début-14 jours ≤ échéance < début. Inscription/annulation personnelle autorisée uniquement tant que maintenant < échéance. À égalité, fermeture prioritaire.


## H06 · Saison et données CCN

Les dates de saison ne sont pas précisées : une politique de calendrier validée par le club doit convertir les catégories CCN en périodes. Sans politique pour une saison non annuelle, création refusée. Un dernier instantané CCN validé permet le fonctionnement hors ligne; sans donnée utilisable, seule l’opération qui en dépend est refusée.


## H07 · Validité du chef

La certification inclut le numéro, la délivrance et l’expiration; les dates sont inclusives dans le fuseau du club. Délivrance ≤ date de randonnée ≤ expiration; niveau suffisant et adhésion active du chef exigés. La création ne modifie pas sa certification.


## H08 · Unicité et concurrence

Le courriel est comparé après retrait des espaces périphériques et neutralisation de la casse. Un seul enregistrement d’inscription existe par couple membre/randonnée. Une réinscription après annulation reprend cet enregistrement avec un nouvel instant FIFO. Les inscriptions et promotions sont atomiques; égalité d’instant départagée par un numéro de séquence croissant.

Statut de ces décisions : propositions de l’équipe à valider avec le client. Elles rendent les contrats déterministes sans ajouter silencieusement des exigences à CAR-Req-01.


# 3. Hypothèses (2/2)


## H09 · Promotion FIFO

La liste d’attente n’accepte que des membres admissibles. Au moment de promouvoir, l’admissibilité est revalidée; une entrée devenue inadmissible est annulée, avec motif audité et notification, puis on examine la suivante. Aucune promotion après l’échéance ou sur randonnée annulée.


## H10 · Décharge et renseignements

L’âge est calculé à la date locale d’enregistrement. Pour un mineur, le nom du tuteur et son acceptation sont obligatoires. Le système conserve la version de la décharge, l’auteur et l’instant d’acceptation. Il ne prétend pas vérifier juridiquement la tutelle.


## H11 · Rappels et panne externe

Rappel exigible à début moins 24 h. Une randonnée créée après ce seuil reçoit un rappel au prochain passage, avant son début; les nouveaux confirmés après le seuil aussi. Une seule remise logique par inscription et randonnée. Une panne météo supprime seulement l’avertissement; une panne courriel crée un envoi en attente pour reprise.


## H12 · Rapports et absence de présence

La période inclut ses deux dates et filtre la date locale de début. Nombre de randonnées = tous les événements, annulés inclus. Participants = somme des inscriptions confirmées des événements non annulés : places réservées, jamais présences réelles ni personnes distinctes. Pour un événement terminé, on utilise l’instantané figé au début.


## H13 · Permissions et confidentialité

Le randonneur modifie uniquement son profil; seul un administrateur change adhésion et certification. Un chef annule uniquement ses événements; un administrateur peut tous les annuler. Les pages publiques ne révèlent que le nom affiché du chef, aucune coordonnée, liste de participants ou donnée d’urgence.


## H14 · Modification des droits et historique

Un changement d’adhésion/certification n’annule pas rétroactivement les inscriptions ni les randonnées. L’admissibilité est revalidée à chaque nouvelle inscription/promotion; l’administrateur annule les événements touchés au besoin. Ce choix doit être validé par le club.


## H15 · Reprises et lecture seule

Une clé de requête empêche un même appel rejoué de créer deux comptes, randonnées, inscriptions ou notifications. Les lectures, y compris Parcourir les randonnées, sont incluses dans les contrats applicatifs demandés même si elles ne modifient pas l’état. Un rejet laisse l’état métier intact.


# 4. Diagramme de contexte du système

La frontière représente l’application Web CAR-HMS et ses composants locaux. Les acteurs et services externes échangent les informations décrites ci-dessous. L’ordonnanceur, le cache et la base de données sont internes; ils ne constituent pas des systèmes clients indépendants.

Diagramme : voir contexte.svg (version vectorielle modifiable).

| Élément externe | Entrées / sorties à la frontière |
| --- | --- |
| Utilisateurs humains | Demandes et confirmations → CAR-HMS; listes, résultats, profils autorisés et rapports ← CAR-HMS. |
| Processus administratif du club | Codes préalables et décisions d’adhésion/certification saisis par les acteurs autorisés. Aucune API externe de membres n’est supposée. |
| CCN | Requête de données → CCN; références de sentiers, géométrie, permissions et caractéristiques ← CCN. Pas d’écriture dans la CCN. |
| Météo | Coordonnées et date → service; prévision facultative ← service. |
| Messagerie | Courriels et destinataires → service; accusés ou erreurs de remise ← service. |

Sécurité : contrôle d’accès à chaque fonction protégée; stockage authentifié et chiffré; minimisation des données publiques. Résilience : données CCN mémorisées, météo facultative et notifications en attente [R1, §1.4, §2.2; H06, H11, H13].


# 5. Sous-domaines (1/2)


## Planification des randonnées · Cœur

Définit le produit : choix du sentier, admissibilité du chef, calendrier, capacité et cycle de vie. Ces règles propres au club déterminent les événements proposés.

Concepts : Randonnée, statut, organisateur référencé, historique de transitions. Responsabilité : Créer, fermer et annuler une randonnée; parcourir les événements. Paquetage : domain.planning.


## Inscriptions et liste d’attente · Cœur

L’appariement des membres aux événements, les limites de niveau et la promotion FIFO constituent la différenciation recherchée par le client (§1.2).

Concepts : Inscription, statut, rang FIFO et attribution des places. Responsabilité : Inscrire, annuler une inscription et promouvoir sans dépasser la capacité. Paquetage : domain.registration.


## Profils et habilitations · Support

Les profils, l’adhésion constatée et la certification alimentent les décisions du cœur. Le recrutement et la gestion administrative complète des adhésions restent externes.

Concepts : Randonneur, coordonnées, contact d’urgence, décharge, certification. Responsabilité : Enregistrer un randonneur et mettre à jour son profil, son statut ou sa certification. Paquetage : domain.members.


## Référentiel externe des sentiers · Support

La CCN fait autorité; le club adapte et consulte ses données sans éditer un catalogue indépendant.

Concepts : Référence CCN, instantané horodaté, difficulté, permission et saison. Responsabilité : Fournir les caractéristiques utiles à la planification et à la consultation. Paquetage : domain.trails.


# 5. Sous-domaines (2/2)


## Identité et contrôle d’accès · Générique

Authentification, sessions et contrôle des rôles sont des capacités réutilisables sans particularité du domaine randonnée.

Concepts : Compte, rôle et session; secrets hors des objets métier publics. Responsabilité : Authentifier, déconnecter et fournir un contexte d’appel fiable. Paquetage : domain.identity.


## Notifications et intégrations météo · Générique

L’envoi fiable de courriels et l’accès à une prévision sont des capacités techniques réutilisables. Le cœur détermine les événements déclencheurs et les destinataires.

Concepts : Notification, clé de déduplication, état de livraison, prévision facultative. Responsabilité : Confirmer, notifier les promotions/annulations et envoyer les rappels. Paquetage : domain.notifications.


## Rapports d’utilisation · Support

Les statistiques soutiennent le pilotage du club sans définir ses règles de participation.

Concepts : Projection d’utilisation par sentier et période. Responsabilité : Calculer les événements, les places confirmées et les annulations. Paquetage : domain.reporting.


## Dépendances et frontières

La planification consulte les profils/habilitations et le référentiel de sentiers. Les inscriptions consultent la planification et les profils. Le cœur produit les événements consommés par les notifications et les projections de rapports. L’identité fournit le contexte d’appel aux services applicatifs; elle n’attribue pas à elle seule l’admissibilité à une randonnée.

Ces frontières constituent des sous-domaines conceptuels et des paquetages, pas une obligation de microservices ou de bases distinctes. Une transaction locale peut protéger capacité, inscription et intention de notification.


# 6. Modèle de domaine de haut niveau

| Concept / lien | Contenu et cardinalité |
| --- | --- |
| Randonneur | Identité par courriel unique; coordonnées, naissance, urgence, niveau et statut d’adhésion. Un compte a un profil. Un administrateur est un rôle d’accès, pas une sous-classe métier obligatoire. |
| Certification | Un randonneur possède 0..1 certification courante; les versions antérieures sont conservées en historique. Numéro, délivrance, expiration, niveau. Organisateur = randonneur habilité. |
| Décharge | Un randonneur conserve 1..* preuves versionnées; chaque preuve a un acceptant et un instant, ainsi que le tuteur si nécessaire. |
| Randonnée → organisateur | Chaque randonnée a exactement 1 organisateur; un organisateur dirige 0..* randonnées. Titre, description, début, durée, échéance, capacité et statut. |
| Randonnée → sentier | Exactement 1 référence CCN et son instantané validé; une référence sert 0..* randonnées. Le départ vient du sentier. La difficulté n’est pas saisie indépendamment. |
| Inscription | Lie exactement 1 randonneur à exactement 1 randonnée. Chaque côté a 0..* inscriptions; unicité du couple. Statut, instant de demande, séquence et historique. |
| Historique de transition | Une randonnée possède 1..* transitions, incluant la création : ancien état éventuel, nouvel état, auteur, cause et instant. SYSTEM représente les transitions automatiques. |
| Notification | Une intention référence son événement métier et son destinataire; statut de remise et clé de déduplication. Pas d’envoi réseau requis dans la transaction métier. |
| Rapport | Projection calculée, pas entité possédant les événements. Aucune notion de présence réelle n’est introduite. |


## Cycle de vie de la randonnée

Création → OUVERTE. Dernière place prise : OUVERTE → COMPLÈTE. Place libérée sans remplacement : COMPLÈTE → OUVERTE. Échéance atteinte : OUVERTE ou COMPLÈTE → FERMÉE. Avant le début : OUVERTE, COMPLÈTE ou FERMÉE → ANNULÉE. Au début, sans annulation : FERMÉE → TERMINÉE selon H04. ANNULÉE et TERMINÉE sont terminales.

TERMINÉE est un état métier analytique issu du glossaire, bien que la liste du §2.1 ne le mentionne pas. Il signifie événement prévu passé, sans assertion sur sa réalisation physique. Un traitement en retard ferme puis termine dans cet ordre en conservant les instants de prise d’effet et de traitement.


# 6.1 Invariants et décisions transversales

- I01 · Autorisation : compte authentifié pour toute action protégée; inscription initiale et connexion publiques par H01. SYSTEM seul déclenche fermeture et rappels.
- I02 · Capacité : 0 ≤ inscriptions confirmées ≤ capacité; COMPLÈTE si capacité atteinte avant échéance; aucune attente prioritaire contournée lors d’une place libérée.
- I03 · Admissibilité : adhésion active et d ≤ min(4,n+1) à l’inscription/promotion; niveau du chef ≥ d et certification couvrant l’événement à la création.
- I04 · Temps : maintenant < échéance pour participer ou se retirer; début-14 jours ≤ échéance < début; annulation globale permise jusqu’à maintenant < début.
- I05 · Référence : CCN est autorité pour sentier, permission, difficulté, saison et départ. Un instantané local n’est pas un catalogue éditable par le club.
- I06 · Atomicité : places, inscription, transitions et intentions de notification sont cohérentes dans une même transaction logique; les appels externes sont hors de cette transaction.
- I07 · Historique : aucune suppression physique d’un événement ou d’une inscription n’efface son auteur, son ordre, son motif ou les valeurs nécessaires aux rapports.
- I08 · Confidentialité : un visiteur n’obtient jamais coordonnées, urgence, naissance, courriel ni liste nominative des participants. Les requêtes d’enregistrement ne sont jamais journalisées en clair.
- I09 · Répétition : requestId est unique par acteur et commande; un rejeu identique renvoie le résultat initial sans nouveau changement, une charge différente est refusée.
- I10 · Rapport : les compteurs distinguent événements, annulations et places réservées; aucune estimation de fréquentation réelle n’est présentée comme une observation.


## Conventions pour les fiches et les contrats

Les préconditions décrivent l’état requis; elles sont revalidées côté serveur. Les branches d’erreur décrivent les appels qui ne les respectent pas. Les étapes nominales sont ordonnées; les postconditions distinguent réussite et rejet. Les notifications sont considérées acceptées lorsque l’intention durable est créée; leur remise peut être différée.

La correspondance lexicale est : OUVERTE/OPEN, COMPLÈTE/FULL, FERMÉE/CLOSED, ANNULÉE/CANCELLED, TERMINÉE/FINISHED; CONFIRMÉE/CONFIRMED, EN_ATTENTE/WAITLISTED, ANNULÉE/CANCELLED. Les enums de transport Kotlin utilisent les termes anglais; le rapport et Gherkin utilisent le français.


# 7. UC01 · Parcourir les randonnées

Priorité source : 5 [R1, §3.2]. Acteur principal : Visiteur ou utilisateur connecté.


## Préconditions

Aucune authentification requise pour les données publiques.


## Déclencheur

L’utilisateur ouvre la recherche.


## Scénario nominal

1. Saisir facultativement un nom de sentier, une date et/ou une difficulté; si connecté, choisir d’inclure les événements complets (H03).
2. Le système valide les filtres et cherche les événements ouverts, ainsi que les complets demandés, dont l’échéance n’est pas atteinte.
3. Trier par début croissant puis identifiant; présenter titre, description, sentier, difficulté, départ, horaire, durée, échéance, capacité, nom affiché du chef et places restantes.
4. Pour un randonneur connecté, marquer les événements compatibles avec son niveau et signaler si son adhésion ne permet pas de s’inscrire.
5. Afficher les résultats sans coordonnées ni informations personnelles des participants.


## Variantes et erreurs

- Filtres invalides : message précis, aucune recherche exécutée. Filtre des complètes sans session : accès refusé. Aucun résultat : liste vide explicite.
- CCN indisponible : utiliser les données mémorisées et indiquer leur date de référence. La consultation locale reste disponible.


## Postconditions

Réussite : Résultats affichés; aucune donnée métier modifiée.

Rejet : État identique en cas d’échec.


## Contrat applicatif

BrowseHikes.browseHikes(BrowseHikesQuery)


# 7. UC02 · Enregistrer un randonneur

Priorité source : 6 [R1, §3.2]. Acteur principal : Visiteur membre du club.


## Préconditions

Code d’invitation disponible dans la source autorisée; utilisateur non encore enregistré.


## Déclencheur

Le membre choisit de créer son compte.


## Scénario nominal

1. Saisir code d’invitation, courriel, mot de passe, nom, téléphone, adresse, naissance, contact d’urgence et niveau.
2. Le système normalise le courriel (espaces retirés et casse neutralisée selon H08 pour l’unicité du compte), vérifie son unicité et les champs obligatoires.
3. Valider le code : existant, non expiré s’il possède une échéance, non consommé; vérifier qu’aucun compte n’a déjà utilisé ce code.
4. Présenter la décharge versionnée; recueillir l’acceptation. Pour moins de 18 ans, recueillir le nom du tuteur et son acceptation.
5. Créer atomiquement le compte et le profil avec adhésion ACTIVE, consommer l’invitation et conserver la preuve d’acceptation; protéger le secret par hachage adapté.
6. Afficher la réussite et inviter à se connecter; aucune adhésion au club ni invitation nouvelle n’est créée.


## Variantes et erreurs

- Code invalide/consommé, courriel existant, naissance future ou champ invalide : rejet sans compte ni consommation du code.
- Décharge non acceptée ou tuteur manquant : rejet. Deux créations concurrentes sur le même courriel/code : une seule réussit.


## Postconditions

Réussite : Un randonneur unique actif existe; invitation consommée une seule fois; aucune session automatique supposée.

Rejet : Aucune création partielle.


## Contrat applicatif

RegisterHiker.registerHiker(RegisterHikerQuery)


# 7. UC03 · Se connecter

Priorité source : 10 [R1, §3.2]. Acteur principal : Utilisateur enregistré.


## Préconditions

Compte existant; service local d’identité disponible.


## Déclencheur

L’utilisateur soumet ses identifiants.


## Scénario nominal

1. Saisir le courriel et le mot de passe sur le formulaire de connexion.
2. Le système retrouve le compte et vérifie le secret sans le journaliser.
3. Émettre une session protégée et charger les rôles; ne pas confondre connexion et admissibilité liée à l’adhésion.
4. Afficher les fonctions autorisées; un compte à adhésion expirée peut consulter son profil mais ne peut pas s’inscrire.


## Variantes et erreurs

- Identifiants incorrects : message générique, aucune session.
- Service d’identité indisponible : échec explicite; aucune élévation de privilège.


## Postconditions

Réussite : Session liée au compte et aux permissions actuelles.

Rejet : Aucune session créée.


## Contrat applicatif

Exclu des interfaces et contrats par les consignes du livrable (§2).


# 7. UC04 · Se déconnecter

Priorité source : 11 [R1, §3.2]. Acteur principal : Utilisateur connecté.


## Préconditions

Session active.


## Déclencheur

L’utilisateur choisit la déconnexion.


## Scénario nominal

1. Demander la déconnexion.
2. Le système invalide la session côté serveur et supprime les éléments locaux d’authentification.
3. Revenir à la consultation publique; toute nouvelle action protégée exige une nouvelle connexion.


## Variantes et erreurs

- Session déjà expirée : résultat équivalent à une déconnexion réussie.
- Une requête ultérieure avec l’ancienne session est refusée.


## Postconditions

Réussite : Session inutilisable; données métier préservées.

Rejet : En cas d’incident, aucun succès d’invalidation distante non vérifié n’est annoncé.


## Contrat applicatif

Exclu des interfaces et contrats par les consignes du livrable (§2).


# 7. UC05 · S’inscrire à une randonnée

Priorité source : 3 [R1, §3.2]. Acteur principal : Randonneur connecté.


## Préconditions

Adhésion active; randonnée existante ouverte ou complète, non échue; difficulté admissible (H02).


## Déclencheur

Le randonneur confirme sa participation.


## Scénario nominal

1. Sélectionner une randonnée à partir de UC01 et confirmer.
2. Le système déduit l’identité depuis la session; revalide adhésion, difficulté, état et échéance.
3. Vérifier l’absence d’inscription active du même membre; réactiver une inscription annulée avec un nouvel ordre FIFO si nécessaire.
4. Dans une transaction, confirmer si une place est libre; si cette place est la dernière, passer la randonnée à COMPLÈTE et auditer la transition.
5. Si la capacité est atteinte, inscrire EN_ATTENTE avec un ordre strict (instant, séquence).
6. Enregistrer l’événement de notification; confirmer à l’écran, puis envoyer le courriel de confirmation ou le rang courant en attente.


## Variantes et erreurs

- Adhésion inactive, niveau excessif, doublon actif, échéance atteinte, événement fermé/annulé/terminé : rejet.
- Deux demandes sur la dernière place : une confirmée, l’autre en attente. Une panne courriel ne retire pas l’inscription; reprise différée.


## Postconditions

Réussite : Une inscription active unique existe, statut et capacité cohérents; notification émise ou en attente.

Rejet : Aucun changement métier sur rejet.


## Contrat applicatif

SignUpForHike.signUpForHike(SignUpForHikeQuery)


# 7. UC06 · Annuler une inscription

Priorité source : 4 [R1, §3.2]. Acteur principal : Randonneur connecté.


## Préconditions

Inscription propre confirmée ou en attente; maintenant strictement avant l’échéance.


## Déclencheur

Le membre confirme son retrait.


## Scénario nominal

1. Sélectionner sa propre inscription et confirmer l’annulation.
2. Le système revalide propriétaire, état de l’inscription et échéance; verrouille l’attribution des places.
3. Passer l’inscription à ANNULÉE en conservant son historique.
4. Si une place confirmée a été libérée, examiner la liste FIFO; annuler les entrées devenues inadmissibles (H09), puis promouvoir le premier membre admissible.
5. Si la capacité reste atteinte, conserver COMPLÈTE; sinon passer à OUVERTE et auditer la transition éventuelle.
6. Consigner la notification de promotion et informer les personnes dont l’attente a été annulée pour inadmissibilité.


## Variantes et erreurs

- Autre propriétaire, inscription déjà annulée ou échéance atteinte : rejet sans changement.
- Annulation d’une entrée en attente : aucune place ne se libère, ordre des autres conservé. Panne courriel : reprise différée.


## Postconditions

Réussite : Inscription annulée; au plus une promotion pour une place libérée; aucune surcapacité.

Rejet : Aucune annulation partielle ou promotion perdue.


## Contrat applicatif

CancelSignUp.cancelSignUp(CancelSignUpQuery)


# 7. UC07 · Mettre à jour un randonneur

Priorité source : 7 [R1, §3.2]. Acteur principal : Randonneur propriétaire ou administrateur.


## Préconditions

Session autorisée et profil cible existant.


## Déclencheur

L’utilisateur choisit le type de mise à jour.


## Scénario nominal

1. Charger les informations autorisées actuelles; choisir modifier le profil, modifier l’adhésion ou enregistrer une certification.
2. Pour le profil personnel, soumettre nom, téléphone, adresse, naissance, urgence et niveau; ne pas permettre de modifier rôles, courriel identifiant ou adhésion par ce formulaire.
3. Pour l’adhésion, un administrateur choisit ACTIVE, EXPIRÉE ou SUSPENDUE. Le processus d’adhésion externe demeure hors portée.
4. Pour la certification, un administrateur saisit numéro, délivrance, expiration et niveau d’organisateur; valider numéro non vide, dates ordonnées et niveau 1 à 4.
5. Valider tous les champs, enregistrer la seule modification autorisée et auditer l’auteur; une certification valide confère l’habilitation d’organisateur.
6. Afficher les données mises à jour; une modification de naissance conserve l’historique de décharge et nécessite une preuve de tuteur si le profil devient mineur.


## Variantes et erreurs

- Accès à un autre profil ou tentative d’auto-approbation : refus.
- Champs invalides, nouvelle minorité sans preuve de tuteur, dates incohérentes ou version devenue obsolète : rejet atomique; recharger en cas de conflit.


## Postconditions

Réussite : Profil, statut ou certification modifié selon la commande; autres champs inchangés; H14 appliquée.

Rejet : Anciennes valeurs conservées sur rejet.


## Contrat applicatif

UpdateHiker.updateProfile / changeMembership / recordCertification (3 commandes)


# 7. UC08 · Fermer une randonnée

Priorité source : 2 [R1, §3.2]. Acteur principal : Ordonnanceur interne (SYSTEM).


## Préconditions

Randonnée OUVERTE ou COMPLÈTE; échéance atteinte.


## Déclencheur

Passage de l’ordonnanceur ou contrôle à l’entrée d’une commande.


## Scénario nominal

1. Sélectionner une randonnée dont maintenant ≥ échéance.
2. Revalider son état dans une transaction.
3. Passer à FERMÉE; journaliser ancien/nouvel état, instant, cause échéance et auteur SYSTEM.
4. Interdire dès l’échéance toute inscription et annulation personnelle même si l’ordonnanceur a pris du retard.
5. Conserver les inscriptions et la liste d’attente sans promotion ultérieure.


## Variantes et erreurs

- Appel avant échéance : refus sans changement.
- Déjà fermée/annulée/terminée : appel sans effet; aucune transition ni notification en double. Appel humain : non autorisé.


## Postconditions

Réussite : Randonnée fermée ou état terminal déjà existant; aucune participation nouvelle.

Rejet : Aucune fermeture anticipée.


## Contrat applicatif

CloseHike.closeHike(CloseHikeQuery)


# 7. UC09 · Envoyer un rappel de randonnée

Priorité source : 9 [R1, §3.2]. Acteur principal : Ordonnanceur interne; service météo et messagerie secondaires.


## Préconditions

Événement non annulé et non terminé; début-24 h ≤ maintenant < début; inscriptions confirmées.


## Déclencheur

Échéance de rappel, confirmation tardive ou reprise après incident.


## Scénario nominal

1. Charger date, heure, sentier et point de départ; sélectionner uniquement les inscriptions actuellement confirmées sans rappel déjà remis.
2. Demander une prévision pour la date de la randonnée et les coordonnées du point de départ, avec délai d’attente borné.
3. Si pluie ou neige prévue, ajouter un avertissement; si prévision impossible, préparer le rappel sans avertissement.
4. Créer une intention d’envoi par destinataire avec une clé stable (randonnée, inscription, rappel); inclure date, heure, sentier et point de rassemblement.
5. Revalider l’état avant remise à la messagerie; envoyer et consigner le résultat sans exposer les adresses des autres participants.
6. Lors d’une reprise, ne traiter que les rappels non remis et encore pertinents.


## Variantes et erreurs

- Panne météo : courriel normal sans avertissement; panne messagerie : en attente, reprise avant début.
- Liste vide, événement annulé, appel trop tôt ou après début : aucun envoi. Une relance ne génère pas un nouveau rappel logique.


## Postconditions

Réussite : Chaque destinataire admissible a un rappel remis ou un envoi en attente; état de randonnée inchangé.

Rejet : Aucun envoi indu; résultat explicite pour les envois échoués.


## Contrat applicatif

SendHikeReminder.sendHikeReminder(SendHikeReminderQuery)


# 7. UC10 · Créer une randonnée

Priorité source : 1 [R1, §3.2]. Acteur principal : Organisateur connecté et approuvé.


## Préconditions

Adhésion active; certification enregistrée; données CCN utilisables.


## Déclencheur

L’organisateur soumet une nouvelle randonnée.


## Scénario nominal

1. Sélectionner un sentier CCN identifié; consulter permission, difficulté, saison et point de départ.
2. Saisir titre, description, début, durée, date limite et capacité.
3. Valider sentier réel de la région, randonnée permise, date dans la saison et niveau du chef au moins égal à la difficulté.
4. Vérifier la certification à la date de l’événement, le début futur et les bornes temporelles H05; rejeter les champs manquants.
5. Créer une randonnée identifiée de façon unique, liée au chef courant et au sentier CCN, avec l’instantané de référence et le statut OUVERTE.
6. Enregistrer la transition de création et son auteur; rendre la randonnée immédiatement consultable et accessible à l’inscription.


## Variantes et erreurs

- Certification expirant avant l’événement, niveau insuffisant, saison interdite/inconnue, sentier interdit ou données invalides : rejet explicite.
- CCN indisponible : utiliser un instantané validé; sans instantané utilisable, rejeter cette création, les autres fonctions restant disponibles.


## Postconditions

Réussite : Une randonnée ouverte unique existe, sans inscription; chef et transition de création tracés.

Rejet : Aucune randonnée partielle; aucune modification du référentiel CCN.


## Contrat applicatif

CreateHike.createHike(CreateHikeQuery)


# 7. UC11 · Annuler une randonnée

Priorité source : 8 [R1, §3.2]. Acteur principal : Organisateur propriétaire ou administrateur.


## Préconditions

Randonnée existante OUVERTE, COMPLÈTE ou FERMÉE; maintenant < début.


## Déclencheur

L’acteur fournit un motif et confirme.


## Scénario nominal

1. Identifier l’événement et saisir un motif non vide.
2. Le système vérifie que l’acteur est son chef ou un administrateur; revalide l’instant et l’état.
3. Passer atomiquement la randonnée à ANNULÉE et toutes ses inscriptions confirmées/en attente à ANNULÉE; conserver leur historique.
4. Auditer l’auteur, le motif, l’heure et l’ancien état; ne promouvoir personne.
5. Créer un courriel d’annulation avec le motif pour chaque membre dont l’inscription était active; supprimer les rappels non encore remis.
6. Confirmer la réussite; remettre les notifications via la file locale.


## Variantes et erreurs

- Chef d’un autre événement, motif vide, début atteint ou événement terminé : rejet.
- Événement déjà annulé : résultat sans effet et sans second courriel. Panne messagerie : annulation maintenue et notification reprise.


## Postconditions

Réussite : Aucune inscription active ne subsiste; motif et auteur conservés; aucune nouvelle inscription permise.

Rejet : Aucun changement partiel.


## Contrat applicatif

CancelHike.cancelHike(CancelHikeQuery)


# 7. UC12 · Générer un rapport d’utilisation des sentiers

Priorité source : 12 [R1, §3.2]. Acteur principal : Administrateur connecté.


## Préconditions

Sentier CCN connu; autorisation de rapport.


## Déclencheur

L’administrateur demande les statistiques.


## Scénario nominal

1. Sélectionner le sentier, la date de début et la date de fin.
2. Valider début ≤ fin et interpréter les dates dans le fuseau du club, bornes incluses.
3. Sélectionner les événements du sentier selon leur date locale de début.
4. Calculer nombre total d’événements, nombre d’événements annulés et nombre de places confirmées des événements non annulés; appliquer l’instantané historique aux événements terminés (H12).
5. Présenter période, sentier, valeurs et définition des indicateurs, avec la mention « réservations, pas présences réelles ».


## Variantes et erreurs

- Aucun événement : trois compteurs nuls.
- Période inversée ou accès non administrateur : refus. CCN indisponible : calculer à partir des références locales.


## Postconditions

Réussite : Rapport affiché sans modifier événements ou inscriptions.

Rejet : Aucune donnée métier modifiée.


## Contrat applicatif

Exclu des interfaces et contrats par les consignes du livrable (§2).


# 8. Bonus · revue des exigences (1/2)


## B01 · Authentification et création du premier compte

« Tout accès aux fonctionnalités du CAR-HMS autre que la consultation des randonnées ouvertes doit exiger une authentification et une autorisation. » [R1, §2.2, p. 3]

Lacune : UC Enregistrer un randonneur permet pourtant à un visiteur de créer son premier compte [R1, p. 7]; Se connecter précède nécessairement une session. Une application littérale rendrait l’amorçage impossible.

Résolution : H01 : exceptions limitées à l’enregistrement par invitation et à la connexion; consultation publique maintenue.

Effet sur le modèle/contrat : Frontière identité/profils : RegisterHiker accepte un contexte anonyme, mais impose code valide, unicité et décharge. Les autres écritures conservent leur contrôle de rôle.

Vérification : register-hiker.feature : enregistrement du visiteur, code invalide et course sur une invitation. Se connecter reste exclu des interfaces selon R2.


## B02 · Deux formulations incompatibles des niveaux

« Un randonneur ne peut s’inscrire qu’aux randonnées cotées à son niveau d’habileté ou à un niveau au-dessus, lorsque son adhésion est active. » [R1, §1.5, p. 2]

Lacune : Le résumé d’inscription parle d’une difficulté « au plus d’un niveau supérieure » [R1, p. 7], ce qui inclut les niveaux inférieurs. De plus, les deux échelles n’utilisent pas les mêmes mots.

Résolution : H02 : ordre explicite sur quatre niveaux; d ≤ min(4,n+1), sans borne inférieure. Cette interprétation privilégie le résumé de UC et l’accessibilité des sorties faciles aux experts.

Effet sur le modèle/contrat : La règle d’admissibilité du sous-domaine registration utilise un rang normalisé; le niveau du chef obéit à une comparaison distincte chef ≥ difficulté.

Vérification : sign-up-for-hike.feature : débutant/modéré accepté, débutant/difficile refusé, avancé/facile accepté et expert/très difficile accepté.


## B03 · État complet et accès à la liste d’attente

« Le CAR-HMS doit permettre aux randonneurs de s’inscrire aux randonnées ouvertes et doit tenir une liste d’attente lorsqu’une randonnée est complète. » [R1, §2.1, p. 3]

Lacune : Le parcours public de UC Parcourir les randonnées ne liste que les randonnées ouvertes [R1, p. 7]. Sans accès aux complètes, la liste d’attente exigée devient inaccessible par le parcours normal.

Résolution : H03 : ajouter un filtre authentifié incluant les complètes avant l’échéance; accepter l’inscription vers attente pour l’état COMPLÈTE. La consultation publique reste limitée aux ouvertes.

Effet sur le modèle/contrat : BrowseHikesQuery.includeFull et garde de SignUpForHike autorisent COMPLÈTE avant échéance; capacité et places restantes restent cohérentes.

Vérification : browse-hikes.feature : une complète apparaît à 0 place; sign-up-for-hike.feature : la demande suivante rejoint l’attente au rang 1.


# 8. Bonus · revue des exigences (2/2)


## B04 · Déclencheurs automatiques et auteur du cycle

« Le CAR-HMS doit enregistrer l’utilisateur qui a effectué chaque étape du cycle de vie d’une randonnée. » [R1, §2.1, p. 3]

Lacune : Le diagramme rattache Fermer une randonnée et Envoyer un rappel à un randonneur [R1, fig. 1, p. 5], tandis que les résumés les déclenchent par échéance et par début moins un jour [R1, p. 7-8]. Une action planifiée n’a pas forcément d’utilisateur humain.

Résolution : H04 : ordonnanceur interne, principal SYSTEM et cause conservée; les règles temporelles s’appliquent même si son passage tarde. TERMINÉE conserve la même convention d’audit.

Effet sur le modèle/contrat : planning conserve un auteur humain ou système pour chaque transition; CloseHike et SendHikeReminder exigent un appel interne autorisé.

Vérification : close-hike.feature : égalité à l’échéance, retard et rejeu sans double audit; send-hike-reminder.feature : déclenchement aux 24 heures.


## B05 · Participants statistiques et absence de présence

« Le rapport présente des statistiques sur les randonnées de ce sentier pendant la période indiquée (nombre de randonnées, nombre de participants, nombre de randonnées annulées). » [R1, §3.2, p. 8]

Lacune : Le terme participants n’est pas défini; or « Ce qui se passe le jour de la randonnée n’est pas suivi par le système » [R1, §1.5, p. 3]. Les présences réelles et les personnes distinctes ne se déduisent pas du nombre d’inscriptions.

Résolution : H12 : dates incluses selon le début local; somme des réservations confirmées sur événements non annulés, instantané figé pour les terminés; compteur total incluant annulées.

Effet sur le modèle/contrat : reporting conserve une projection historique de réservations et expose la définition de l’indicateur. Aucun concept de présence n’est inventé.

Vérification : UC12 : période vide donne (0,0,0). Exemple de vérification : deux événements, un non annulé avec 3 confirmés et un annulé avec 2 anciens confirmés donnent (2,3,1). UC12 est exclu des contrats Cucumber par R2.

Ces cinq observations expliquent l’origine de décisions; elles ne remplacent pas la liste complète des hypothèses de la section 3. Les autres points à confirmer ne sont pas présentés comme des observations bonus supplémentaires.


# 9. Traçabilité des artefacts et conformité

| Cas | Interface et commande | Contrat .feature |
| --- | --- | --- |
| UC01 | BrowseHikes.browseHikes | browse-hikes |
| UC02 | RegisterHiker.registerHiker | register-hiker |
| UC05 | SignUpForHike.signUpForHike | sign-up-for-hike |
| UC06 | CancelSignUp.cancelSignUp | cancel-sign-up |
| UC07 | UpdateHiker.updateProfile | update-profile |
| UC07 | UpdateHiker.changeMembership | change-membership |
| UC07 | UpdateHiker.recordCertification | record-certification |
| UC08 | CloseHike.closeHike | close-hike |
| UC09 | SendHikeReminder.sendHikeReminder | send-hike-reminder |
| UC10 | CreateHike.createHike | create-hike |
| UC11 | CancelHike.cancelHike | cancel-hike |

Les onze DTO racines sont dans application.dtos.queries.Queries.kt; ProfileQuery, EmergencyContactQuery et WaiverAcceptanceQuery composent les requêtes. HikeSummary est une projection de sortie dans application.dtos. Le paquetage usecases contient neuf interfaces; UpdateHiker possède trois fonctions pour séparer les permissions.


## Couverture des consignes

| Exigence de remise [R2] | Emplacement / preuve |
| --- | --- |
| Couverture et contributions | Sections 1 et 2; professeur, identités et tâches des deux membres renseignés. |
| Hypothèses, contexte, sous-domaines | Sections 3 à 6; 7 sous-paquetages domain avec README. |
| 12 analyses de cas d’utilisation | Section 7 : préconditions, étapes, variantes et postconditions. |
| Commandes / DTO / contrats | 9 interfaces, 11 fonctions, 11 DTO racines, 11 fonctionnalités. |
| Exceptions au code | UC03, UC04 et UC12 décrits dans le rapport; aucune interface ni fonctionnalité correspondante. |
| Bonus jusqu’à 5 éléments | Section 8 : 5 observations avec citation, résolution et effet. |
| Dépôt GitHub | Dossier backend prêt à intégrer; publication et URL du dépôt à fournir par l’équipe. |


# 10. Références et préparation de la remise


## 10.1 Documents de référence

[R1] Kalonji Kalala. Système de gestion des événements de randonnée du Cairn (CAR-HMS), document des exigences initiales, CAR-Req-01. SEG 3102, Université d’Ottawa, automne 2026. Fichier fourni : Exigences Initiales-CAR-HMS_exigences_initiales_FR1.pdf, 8 pages. Références pertinentes : contexte/portée p. 1-2; glossaire p. 2-3; exigences p. 3-4; diagramme p. 5-6; cas d’utilisation p. 7-8.

[R2] Boqi Chen. SEG 3102, Projet, Livrable 1 : domaine initial. Université d’Ottawa, automne 2026. Fichier fourni : SEG3102_Livrable1_FR1.pdf, 3 pages. Plan du rapport p. 1; structure de code et exceptions p. 2; critères du bonus p. 2-3.

Les liens vers la CCN présents dans R1 désignent de futures sources opérationnelles; aucune consultation du catalogue en direct ni validation d’un fournisseur météo n’est prétendue ici. Les règles de ce livrable sont tirées des deux PDF et des hypothèses explicites.


## 10.2 Points à confirmer avant dépôt

- Vérifier les informations de couverture et le tableau des contributions; aucun nom d’équipe distinct n’est utilisé, conformément au choix des membres.
- Valider les hypothèses avec le client/enseignant, en priorité l’admissibilité aux niveaux inférieurs, le calendrier saisonnier CCN, la revalidation des attentes et le sens de « participants ».
- Intégrer backend dans le dépôt GitHub de l’équipe et vérifier l’arborescence et les droits d’accès de l’évaluateur. Les consignes ne rendent pas explicitement obligatoire une branche appelée contracts : ce nom apparaît dans l’exemple.
- La compilation directe des fichiers Kotlin a réussi (compilateur 2.0.21, JDK 21, cible JVM 17). Le parseur Gherkin officiel accepte 11 fonctionnalités et 100 scénarios développés. L’exécution métier nécessitera les définitions de pas et une implémentation ultérieure.
- Relire le rapport, vérifier les champs administratifs, puis remettre selon la procédure et la date annoncées dans le cours. Les PDF fournis n’indiquent pas la date limite.


## 10.3 Limite de validation

La grille détaillée de correction n’est pas fournie. Ce dossier vise l’ensemble des exigences explicites et le bonus, sans garantir une note. Les contrôles automatiques locaux portent sur la structure, la correspondance entre commandes/DTO/contrats, la compilation des signatures Kotlin, la syntaxe Gherkin et le rendu du PDF; ils ne prouvent pas l’implémentation du produit.
