# language: fr
@UC07 @changeMembership
Fonctionnalité: Contrat initial de changeMembership
  Interface: UpdateHiker; requête: ChangeMembershipQuery.
  Horloge et identité sont contrôlées par le contexte serveur.

  Plan du scénario: Statut administratif
    Étant donné un administrateur connecté et un profil de version actuelle
    Quand il modifie l'adhésion en <statut>
    Alors le nouveau statut est <statut> et l'auteur est audité
    Et les inscriptions et les randonnées existantes ne sont pas annulées automatiquement

    Exemples:
      | statut    |
      | ACTIVE    |
      | EXPIRED   |
      | SUSPENDED |

  Scénario: Tentative d'auto-réactivation
    Étant donné un randonneur connecté à adhésion expirée sans rôle administrateur
    Quand il appelle le changement d'adhésion vers ACTIVE
    Alors l'accès est refusé et l'adhésion reste expirée

  Scénario: Conflit de version
    Étant donné un administrateur avec une version de profil devenue obsolète
    Quand il soumet un changement de statut
    Alors la modification est refusée sans écraser la version actuelle
