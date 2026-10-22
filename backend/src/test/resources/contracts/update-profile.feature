# language: fr
@UC07 @updateProfile
Fonctionnalité: Contrat initial de updateProfile
  Interface: UpdateHiker; requête: UpdateProfileQuery.
  Horloge et identité sont contrôlées par le contexte serveur.

  Scénario: Mise à jour par le propriétaire
    Étant donné un membre connecté et la version actuelle de son profil
    Quand il soumet des coordonnées, une naissance et un niveau valides
    Alors son profil est mis à jour et sa version augmente
    Et son adhésion, ses rôles et sa certification sont inchangés

  Plan du scénario: Validation du profil
    Étant donné une mise à jour du profil avec <défaut>
    Quand le membre soumet la modification
    Alors la modification est refusée et l'ancien profil est conservé

    Exemples:
      | défaut                                |
      | un contact d'urgence sans téléphone   |
      | une date de naissance future          |
      | une version obsolète                  |
      | une nouvelle minorité sans décharge du tuteur |
      | une session absente                   |

  Scénario: Preuve de tuteur lors d'une correction de naissance
    Étant donné un membre dont la naissance corrigée indique 17 ans
    Quand il soumet le profil avec une décharge acceptée par un tuteur nommé
    Alors le profil et la preuve versionnée sont conservés ensemble
