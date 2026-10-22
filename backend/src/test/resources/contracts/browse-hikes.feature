# language: fr
@UC01 @browseHikes
Fonctionnalité: Contrat initial de browseHikes
  Interface: BrowseHikes; requête: BrowseHikesQuery.
  Horloge et identité sont contrôlées par le contexte serveur.

  Scénario: Consultation publique filtrée et triée
    Étant donné une randonnée ouverte "A" le "2026-11-10" sur "Sentier A" de difficulté "facile"
    Et une randonnée ouverte "B" le "2026-11-09" sur "Sentier A" de difficulté "facile"
    Et une randonnée annulée "C" sur "Sentier A"
    Quand un visiteur recherche "Sentier A" sans inclure les randonnées complètes
    Alors les résultats sont "B, A" dans cet ordre
    Et chaque résultat indique le départ et le nombre de places restantes
    Et aucun résultat ne contient de courriel ou de liste de participants
    Et aucune donnée métier n'est modifiée

  Scénario: Accès à une randonnée complète pour rejoindre sa liste d'attente
    Étant donné une randonnée complète avant son échéance
    Quand un membre connecté recherche en incluant les randonnées complètes
    Alors cette randonnée apparaît avec 0 place restante

  Scénario: Refus de consultation publique des complètes
    Étant donné un visiteur sans session
    Quand il recherche en incluant les randonnées complètes
    Alors la demande est refusée sans révéler les randonnées complètes

  Scénario: Personnalisation du niveau sans modifier l'accès public
    Étant donné un membre connecté de niveau "intermédiaire" et d'adhésion "expirée"
    Et une randonnée ouverte de difficulté "difficile"
    Quand ce membre consulte les randonnées
    Alors cette randonnée est marquée compatible avec son niveau
    Mais l'inscription est signalée indisponible à cause de son adhésion

  Scénario: Aucun résultat et CCN indisponible
    Étant donné un instantané local CCN et un service CCN indisponible
    Quand un visiteur cherche un nom de sentier absent
    Alors une liste vide est retournée avec la date des données locales
