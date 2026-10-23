# language: fr
@UC06 @cancelSignUp
Fonctionnalité: Contrat initial de cancelSignUp
  Interface: CancelSignUp; requête: CancelSignUpQuery.
  Horloge et identité sont contrôlées par le contexte serveur.

  Scénario: Promotion du premier membre admissible
    Étant donné une randonnée complète avec un confirmé "A" et les attentes "B, C, D" dans cet ordre
    Et "B" a désormais une adhésion suspendue tandis que "C" et "D" restent admissibles
    Quand "A" annule avant l'échéance
    Alors les inscriptions de "A" et "B" sont annulées
    Et "C" est confirmé et "D" reste en attente
    Et la randonnée reste complète sans surcapacité
    Et une notification est prévue pour "B" et "C"

  Scénario: Réouverture sans attente
    Étant donné une randonnée complète sans liste d'attente
    Quand un confirmé annule avant l'échéance
    Alors la randonnée devient ouverte et la transition est auditée

  Scénario: Retrait d'une entrée en attente
    Étant donné une randonnée complète avec les attentes "B, C"
    Quand "B" annule avant l'échéance
    Alors "C" reste en attente au rang 1
    Et le nombre de confirmés est inchangé

  Plan du scénario: Refus d'annulation
    Étant donné une annulation demandée avec <condition>
    Quand la commande est appelée
    Alors la demande est refusée sans modifier la liste d'attente

    Exemples:
      | condition                           |
      | une inscription d'un autre membre   |
      | une inscription déjà annulée        |
      | un instant égal à l'échéance         |
      | une randonnée annulée               |

  Scénario: Égalité d'horodatage et annulations concurrentes
    Étant donné deux attentes admissibles au même instant ordonnées par séquence 10 puis 11
    Et une randonnée complète avec deux confirmés
    Quand ces deux confirmés annulent simultanément avant échéance
    Alors les deux attentes sont promues chacune une seule fois selon leur séquence
    Et aucun envoi de promotion n'est dupliqué

  Scénario: Échéance passée avant le passage de l'ordonnanceur
    Étant donné une randonnée ouverte dont l'échéance est passée mais pas encore fermée par l'ordonnanceur
    Et une inscription confirmée du membre à cette randonnée
    Quand le membre demande l'annulation de son inscription
    Alors la demande est refusée et l'inscription reste confirmée
