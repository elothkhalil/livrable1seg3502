# language: fr
@UC08 @closeHike
Fonctionnalité: Contrat initial de closeHike
  Interface: CloseHike; requête: CloseHikeQuery.
  Horloge et identité sont contrôlées par le contexte serveur.

  Plan du scénario: Fermeture à l'échéance
    Étant donné une randonnée <état> d'échéance "2026-11-10T15:00:00Z"
    Et l'horloge serveur indique "2026-11-10T15:00:00Z"
    Quand l'ordonnanceur appelle la fermeture
    Alors la randonnée devient fermée avec auteur SYSTEM et cause échéance
    Et les inscriptions existantes restent inchangées

    Exemples:
      | état     |
      | ouverte  |
      | complète |

  Scénario: Fermeture anticipée
    Étant donné une randonnée dont l'échéance est future
    Quand l'ordonnanceur appelle la fermeture
    Alors la fermeture est refusée sans transition

  Scénario: Rejeu et état terminal
    Étant donné une randonnée déjà fermée, annulée ou terminée
    Quand l'ordonnanceur appelle deux fois la fermeture
    Alors aucun changement d'état ni événement d'audit supplémentaire n'est créé
