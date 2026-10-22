# language: fr
@UC07 @recordCertification
Fonctionnalité: Contrat initial de recordCertification
  Interface: UpdateHiker; requête: RecordCertificationQuery.
  Horloge et identité sont contrôlées par le contexte serveur.

  Scénario: Habilitation par un administrateur
    Étant donné un administrateur connecté et un randonneur existant de version actuelle
    Quand il enregistre le certificat "C-100" délivré le "2026-01-01" expirant le "2026-12-31" au niveau "avancé"
    Alors la certification et le niveau sont conservés et l'auteur est audité
    Et le randonneur est habilité comme organisateur dans les limites de cette certification

  Plan du scénario: Certification refusée
    Étant donné une demande de certification avec <défaut>
    Quand la commande est appelée
    Alors aucune certification ni habilitation n'est modifiée

    Exemples:
      | défaut                                  |
      | un appel par un simple randonneur        |
      | un numéro vide                          |
      | une expiration antérieure à la délivrance|
      | un niveau hors de 1 à 4                  |
      | une version obsolète                    |
