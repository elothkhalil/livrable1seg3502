# language: fr
@UC05 @signUpForHike
Fonctionnalité: Contrat initial de signUpForHike
  Interface: SignUpForHike; requête: SignUpForHikeQuery.
  Horloge et identité sont contrôlées par le contexte serveur.

  Scénario: Dernière place attribuée atomiquement
    Étant donné une randonnée ouverte de capacité 2 avec 1 inscription confirmée
    Et deux membres actifs admissibles sans inscription à cette randonnée
    Quand ces membres s'inscrivent simultanément avant l'échéance
    Alors un membre est confirmé et l'autre est en attente au rang 1
    Et la randonnée devient complète avec exactement 2 confirmés
    Et la transition enregistre l'auteur de la dernière place
    Et chaque membre reçoit une intention de courriel correspondant à son statut

  Plan du scénario: Admissibilité selon le niveau
    Étant donné un membre actif de niveau <niveau>
    Et une randonnée ouverte de difficulté <difficulté> avant l'échéance
    Quand le membre confirme son inscription
    Alors l'inscription est <résultat>

    Exemples:
      | niveau        | difficulté    | résultat  |
      | débutant      | modéré        | confirmée |
      | débutant      | difficile     | refusée   |
      | avancé        | facile        | confirmée |
      | expert        | très difficile| confirmée |

  Plan du scénario: Refus de participation
    Étant donné une demande d'inscription avec <condition>
    Quand la commande d'inscription est appelée
    Alors la demande est refusée sans modifier les inscriptions

    Exemples:
      | condition                                 |
      | aucune session                            |
      | une adhésion expirée                      |
      | une adhésion suspendue                    |
      | une inscription déjà confirmée            |
      | une inscription déjà en attente           |
      | un instant égal à l'échéance               |
      | une randonnée fermée                      |
      | une randonnée annulée                     |
      | une randonnée terminée                    |

  Scénario: Réinscription et reprise après panne courriel
    Étant donné une inscription annulée et une randonnée complète avant échéance
    Et un membre toujours admissible et une messagerie indisponible
    Quand il se réinscrit puis rejoue la même clé de requête
    Alors une seule inscription en attente existe avec un nouvel ordre FIFO en queue
    Et une seule notification logique reste en attente de remise
