# language: fr
@UC10 @createHike
Fonctionnalité: Contrat initial de createHike
  Interface: CreateHike; requête: CreateHikeQuery.
  Horloge et identité sont contrôlées par le contexte serveur.

  Scénario: Création valide et certification à sa borne d'expiration
    Étant donné un chef actif approuvé de niveau "avancé"
    Et sa certification couvre la date locale "2026-11-15" et expire ce jour-là
    Et un sentier CCN autorisé de difficulté "difficile" ouvert toute l'année
    Et une horloge au "2026-10-22T12:00:00Z"
    Quand il crée une randonnée débutant le "2026-11-15T15:00:00Z" de durée 120 minutes et capacité 8
    Et fixe l'échéance au "2026-11-01T15:00:00Z"
    Alors une randonnée ouverte identifiée de façon unique est enregistrée
    Et le chef courant et la référence CCN horodatée sont conservés
    Et la transition de création indique le chef comme auteur

  Plan du scénario: Rejet des invariants
    Étant donné une demande de création avec <défaut>
    Quand un organisateur soumet la demande
    Alors aucune randonnée n'est créée et la cause est indiquée

    Exemples:
      | défaut                                            |
      | un appelant non organisateur                      |
      | une adhésion suspendue du chef                    |
      | un certificat expirant la veille de la randonnée   |
      | un certificat délivré après la randonnée           |
      | un niveau de chef inférieur à la difficulté        |
      | un sentier non CCN                                |
      | un sentier interdisant la randonnée                |
      | une date hors saison                              |
      | une saison non annuelle sans calendrier validé     |
      | une échéance 14 jours et 1 seconde avant le début   |
      | une échéance égale au début                        |
      | une échéance déjà atteinte à la création            |
      | une capacité nulle                                 |
      | une durée négative                                 |
      | un titre vide                                     |

  Plan du scénario: Service CCN indisponible
    Étant donné le service CCN indisponible et <cache>
    Quand un chef soumet une création autrement valide
    Alors <résultat>

    Exemples:
      | cache                             | résultat                                             |
      | un instantané validé utilisable    | la randonnée est créée à partir de cet instantané    |
      | aucun instantané utilisable        | seule la création est refusée sans bloquer la lecture|

  Scénario: Rejeu de requête
    Étant donné une demande de création valide déjà acceptée
    Quand la même clé de requête est rejouée
    Alors le même identifiant est retourné et aucune seconde randonnée n'est créée
