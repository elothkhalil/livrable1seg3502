# language: fr
@UC09 @sendHikeReminder
Fonctionnalité: Contrat initial de sendHikeReminder
  Interface: SendHikeReminder; requête: SendHikeReminderQuery.
  Horloge et identité sont contrôlées par le contexte serveur.

  Plan du scénario: Contenu météorologique
    Étant donné une randonnée non annulée débutant dans exactement 24 heures
    Et un membre confirmé sans rappel remis
    Et le service météo retourne <prévision>
    Quand l'ordonnanceur demande le rappel
    Alors le membre reçoit date, heure, sentier et point de départ
    Et le courriel <avertissement>

    Exemples:
      | prévision              | avertissement                     |
      | pluie                  | contient un avertissement de pluie|
      | neige                  | contient un avertissement de neige|
      | temps sec              | ne contient aucun avertissement   |
      | indisponibilité        | ne contient aucun avertissement   |

  Scénario: Sélection et déduplication
    Étant donné une randonnée avec un confirmé, un membre en attente et une inscription annulée
    Quand deux passages de rappel sont exécutés à partir du seuil des 24 heures
    Alors seul le confirmé reçoit une intention de rappel unique

  Scénario: Panne de messagerie et reprise
    Étant donné un rappel exigible et une messagerie indisponible
    Quand le rappel est demandé puis repris avant le début après rétablissement
    Alors l'intention reste en attente jusqu'à remise puis est marquée remise
    Et aucune seconde intention logique n'est créée

  Scénario: Confirmation tardive et annulation avant remise
    Étant donné un membre confirmé 10 heures avant le départ
    Quand le rappel est préparé puis la randonnée annulée avant sa remise
    Alors aucun rappel n'est remis
    Et la notification d'annulation est conservée

  Plan du scénario: Aucun rappel hors fenêtre
    Étant donné une randonnée <condition>
    Quand le rappel est demandé
    Alors aucun rappel n'est envoyé

    Exemples:
      | condition                |
      | débutant dans 25 heures   |
      | annulée                  |
      | déjà commencée           |
      | sans membre confirmé     |
