# language: fr
@UC02 @registerHiker
Fonctionnalité: Contrat initial de registerHiker
  Interface: RegisterHiker; requête: RegisterHikerQuery.
  Horloge et identité sont contrôlées par le contexte serveur.

  Plan du scénario: Décharge conforme à l'âge
    Étant donné une invitation valide non consommée et un courriel unique
    Et un profil complet dont l'âge local est <âge> ans
    Et une décharge versionnée acceptée et <preuve>
    Quand le visiteur soumet son enregistrement
    Alors <résultat>

    Exemples:
      | âge | preuve                                      | résultat                                      |
      | 18  | aucune preuve de tuteur                      | un compte actif est créé et le code consommé   |
      | 17  | un tuteur nommé ayant accepté                | un compte actif est créé et le code consommé   |
      | 17  | aucune preuve de tuteur                      | la demande est refusée sans consommer le code  |

  Plan du scénario: Rejet sans création partielle
    Étant donné une demande d'enregistrement avec <défaut>
    Quand le visiteur soumet son enregistrement
    Alors aucun compte n'est créé
    Et aucune invitation supplémentaire n'est consommée

    Exemples:
      | défaut                       |
      | un code déjà consommé        |
      | un code inconnu              |
      | un code expiré               |
      | un courriel déjà enregistré  |
      | une naissance future         |
      | une décharge non acceptée    |
      | un téléphone manquant        |

  Scénario: Course sur une invitation et reprise du même appel
    Étant donné deux demandes concurrentes pour une même invitation valide
    Quand les deux enregistrements sont soumis puis la demande gagnante est rejouée avec sa clé
    Alors un seul compte est créé et une seule invitation est consommée
    Et le mot de passe n'apparaît dans aucun journal
