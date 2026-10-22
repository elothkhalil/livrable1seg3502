# language: fr
@UC11 @cancelHike
Fonctionnalité: Contrat initial de cancelHike
  Interface: CancelHike; requête: CancelHikeQuery.
  Horloge et identité sont contrôlées par le contexte serveur.

  Plan du scénario: Annulation autorisée avant le début
    Étant donné une randonnée <état> avec des inscriptions confirmées et en attente
    Et <acteur> connecté avant le début
    Quand il annule la randonnée avec le motif "Fermeture du sentier"
    Alors la randonnée et toutes ses inscriptions actives sont annulées atomiquement
    Et le motif, l'instant et l'auteur sont audités
    Et chaque ancien inscrit actif a une notification d'annulation avec ce motif
    Et aucune promotion ni rappel restant n'est envoyé

    Exemples:
      | état     | acteur                  |
      | ouverte  | son organisateur        |
      | complète | son organisateur        |
      | fermée   | un administrateur       |

  Plan du scénario: Refus d'annulation d'événement
    Étant donné une demande d'annulation avec <défaut>
    Quand l'acteur soumet la commande
    Alors la randonnée et les inscriptions restent inchangées

    Exemples:
      | défaut                                 |
      | un organisateur différent sans rôle administrateur |
      | un motif vide                          |
      | un instant égal au début               |
      | une randonnée terminée                 |

  Scénario: Rejeu malgré panne de messagerie
    Étant donné une annulation réussie dont les courriels sont en attente
    Quand la même annulation est rejouée
    Alors aucune nouvelle transition ni notification logique n'est créée
    Et les notifications initiales peuvent être reprises
