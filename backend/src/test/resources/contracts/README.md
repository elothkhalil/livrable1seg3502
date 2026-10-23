# Contrats initiaux

Une fonctionnalité par commande (11), couvrant 9 interfaces et 9 cas d’utilisation. UC03, UC04 et UC12 sont exclus du code par les consignes mais analysés dans le rapport. UC07 donne lieu à trois commandes avec permissions différentes.

Les scénarios Gherkin sont des **spécifications initiales**. Aucune définition de pas ni exécution fonctionnelle n’est fournie à cette étape; le projet contient seulement la classe d’application Spring Boot et les dépendances Cucumber prévues. Les tables « défaut/condition » représentent des fixtures isolées et autrement valides, sauf indication contraire.

Les horloges sont injectées côté serveur. Les instants utilisent UTC; les dates de naissance, saisons et certificats sont évaluées dans America/Toronto. Les identifiants d’acteur et l’heure d’appel ne proviennent jamais du DTO utilisateur. Les clés requestId sont liées à l’acteur et à la commande; rejouer avec une charge différente est rejeté.

Un rejet doit laisser l’état métier intact. Les notifications sont des intentions durables validées avec l’opération métier. La garantie est la déduplication logique locale; une livraison exactement une fois chez un fournisseur externe ne peut pas être garantie sans son concours.

Les interfaces Unit signalent une violation par une erreur applicative typée à définir à l’implémentation; aucun code HTTP n’est imposé par le modèle initial. Les commandes de fermeture et de rappel sont réservées à SYSTEM.
