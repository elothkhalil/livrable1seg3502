from pathlib import Path
import html, json, re, zipfile
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
R=Path(__file__).resolve().parents[1]
SRC=R/'backend/src/main/kotlin/ca/cairn/carhms'
RES=R/'backend/src/test/resources/contracts'
for p in [SRC/'application/usecases',SRC/'application/dtos/queries',RES,R/'rapport']:p.mkdir(parents=True,exist_ok=True)
def put(p,t):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t.strip()+'\n',encoding='utf-8')
subdomains=[
('planning','Planification des randonnées','Cœur','Définit le produit : choix du sentier, admissibilité du chef, calendrier, capacité et cycle de vie. Ces règles propres au club déterminent les événements proposés.','Randonnée, statut, organisateur référencé, historique de transitions.','Créer, fermer et annuler une randonnée; parcourir les événements.'),
('registration','Inscriptions et liste d’attente','Cœur','L’appariement des membres aux événements, les limites de niveau et la promotion FIFO constituent la différenciation recherchée par le client (§1.2).','Inscription, statut, rang FIFO et attribution des places.','Inscrire, annuler une inscription et promouvoir sans dépasser la capacité.'),
('members','Profils et habilitations','Support','Les profils, l’adhésion constatée et la certification alimentent les décisions du cœur. Le recrutement et la gestion administrative complète des adhésions restent externes.','Randonneur, coordonnées, contact d’urgence, décharge, certification.','Enregistrer un randonneur et mettre à jour son profil, son statut ou sa certification.'),
('trails','Référentiel externe des sentiers','Support','La CCN fait autorité; le club adapte et consulte ses données sans éditer un catalogue indépendant.','Référence CCN, instantané horodaté, difficulté, permission et saison.','Fournir les caractéristiques utiles à la planification et à la consultation.'),
('identity','Identité et contrôle d’accès','Générique','Authentification, sessions et contrôle des rôles sont des capacités réutilisables sans particularité du domaine randonnée.','Compte, rôle et session; secrets hors des objets métier publics.','Authentifier, déconnecter et fournir un contexte d’appel fiable.'),
('notifications','Notifications et intégrations météo','Générique','L’envoi fiable de courriels et l’accès à une prévision sont des capacités techniques réutilisables. Le cœur détermine les événements déclencheurs et les destinataires.','Notification, clé de déduplication, état de livraison, prévision facultative.','Confirmer, notifier les promotions/annulations et envoyer les rappels.'),
('reporting','Rapports d’utilisation','Support','Les statistiques soutiennent le pilotage du club sans définir ses règles de participation.','Projection d’utilisation par sentier et période.','Calculer les événements, les places confirmées et les annulations.')]
for key,name,kind,why,model,scope in subdomains:
 put(SRC/f'domain/{key}/README.md',f'# {name}\n\nClassification : **{kind}**.\n\n{why}\n\n## Responsabilité\n{scope}\n\n## Concepts candidats\n{model}\n\nCe livrable fixe la frontière du sous-domaine; il ne prétend pas fournir une implémentation. Voir le rapport pour les invariants et les dépendances.')
assumptions=[
('H01','Inscription initiale publique','L’enregistrement par invitation et la connexion sont des exceptions nécessaires à l’exigence générale d’authentification. Le code est validé contre une source fournie au système, consommé une seule fois et n’est pas émis par CAR-HMS.'),
('H02','Difficulté et admissibilité','On associe débutant/facile=1, intermédiaire/modéré=2, avancé/difficile=3, expert/très difficile=4. Un membre de niveau n peut participer à toute randonnée de niveau d ≤ min(4,n+1), y compris les niveaux inférieurs. Le chef doit avoir un niveau ≥ d.'),
('H03','Complet reste accessible','La recherche par défaut montre les événements ouverts. Un filtre réservé aux utilisateurs connectés permet d’inclure les événements complets encore avant échéance pour rejoindre leur liste d’attente. Les détails par identifiant appliquent la même règle : ouverts publics, complets authentifiés.'),
('H04','Automatismes et audit','Un ordonnanceur interne ferme les inscriptions à l’échéance, envoie les rappels et marque la terminaison au début de la randonnée. Chaque transition consigne l’auteur humain ou SYSTEM, la cause, l’heure et les anciens/nouveaux états.'),
('H05','Bornes temporelles','Les instants sont stockés en UTC et présentés dans America/Toronto. Début futur; durée et capacité entières strictement positives. Création avant l’échéance; début-14 jours ≤ échéance < début. Inscription/annulation personnelle autorisée uniquement tant que maintenant < échéance. À égalité, fermeture prioritaire.'),
('H06','Saison et données CCN','Les dates de saison ne sont pas précisées : une politique de calendrier validée par le club doit convertir les catégories CCN en périodes. Sans politique pour une saison non annuelle, création refusée. Un dernier instantané CCN validé permet le fonctionnement hors ligne; sans donnée utilisable, seule l’opération qui en dépend est refusée.'),
('H07','Validité du chef','La certification inclut le numéro, la délivrance et l’expiration; les dates sont inclusives dans le fuseau du club. Délivrance ≤ date de randonnée ≤ expiration; niveau suffisant et adhésion active du chef exigés. La création ne modifie pas sa certification.'),
('H08','Unicité et concurrence','Le courriel est comparé après retrait des espaces périphériques et neutralisation de la casse. Un seul enregistrement d’inscription existe par couple membre/randonnée. Une réinscription après annulation reprend cet enregistrement avec un nouvel instant FIFO. Les inscriptions et promotions sont atomiques; égalité d’instant départagée par un numéro de séquence croissant.'),
('H09','Promotion FIFO','La liste d’attente n’accepte que des membres admissibles. Au moment de promouvoir, l’admissibilité est revalidée; une entrée devenue inadmissible est annulée, avec motif audité et notification, puis on examine la suivante. Aucune promotion après l’échéance ou sur randonnée annulée.'),
('H10','Décharge et renseignements','L’âge est calculé à la date locale d’enregistrement. Pour un mineur, le nom du tuteur et son acceptation sont obligatoires. Le système conserve la version de la décharge, l’auteur et l’instant d’acceptation. Il ne prétend pas vérifier juridiquement la tutelle.'),
('H11','Rappels et panne externe','Rappel exigible à début moins 24 h. Une randonnée créée après ce seuil reçoit un rappel au prochain passage, avant son début; les nouveaux confirmés après le seuil aussi. Une seule remise logique par inscription et randonnée. Une panne météo supprime seulement l’avertissement; une panne courriel crée un envoi en attente pour reprise.'),
('H12','Rapports et absence de présence','La période inclut ses deux dates et filtre la date locale de début. Nombre de randonnées = tous les événements, annulés inclus. Participants = somme des inscriptions confirmées des événements non annulés : places réservées, jamais présences réelles ni personnes distinctes. Pour un événement terminé, on utilise l’instantané figé au début.'),
('H13','Permissions et confidentialité','Le randonneur modifie uniquement son profil; seul un administrateur change adhésion et certification. Un chef annule uniquement ses événements; un administrateur peut tous les annuler. Les pages publiques ne révèlent que le nom affiché du chef, aucune coordonnée, liste de participants ou donnée d’urgence.'),
('H14','Modification des droits et historique','Un changement d’adhésion/certification n’annule pas rétroactivement les inscriptions ni les randonnées. L’admissibilité est revalidée à chaque nouvelle inscription/promotion; l’administrateur annule les événements touchés au besoin. Ce choix doit être validé par le club.'),
('H15','Reprises et lecture seule','Une clé de requête empêche un même appel rejoué de créer deux comptes, randonnées, inscriptions ou notifications. Les lectures, y compris Parcourir les randonnées, sont incluses dans les contrats applicatifs demandés même si elles ne modifient pas l’état. Un rejet laisse l’état métier intact.')]
# Each use case has detailed nominal flow and explicit failures.
ucs=[
('UC01','Parcourir les randonnées','5','Visiteur ou utilisateur connecté','Aucune authentification requise pour les données publiques.','L’utilisateur ouvre la recherche.',[
'Saisir facultativement un nom de sentier, une date et/ou une difficulté; si connecté, choisir d’inclure les événements complets (H03).',
'Le système valide les filtres et cherche les événements ouverts, ainsi que les complets demandés, dont l’échéance n’est pas atteinte.',
'Trier par début croissant puis identifiant; présenter titre, description, sentier, difficulté, départ, horaire, durée, échéance, capacité, nom affiché du chef et places restantes.',
'Pour un randonneur connecté, marquer les événements compatibles avec son niveau et signaler si son adhésion ne permet pas de s’inscrire.',
'Afficher les résultats sans coordonnées ni informations personnelles des participants.'],[
'Filtres invalides : message précis, aucune recherche exécutée. Filtre des complètes sans session : accès refusé. Aucun résultat : liste vide explicite.',
'CCN indisponible : utiliser les données mémorisées et indiquer leur date de référence. La consultation locale reste disponible.'],
'Résultats affichés; aucune donnée métier modifiée.','État identique en cas d’échec.','BrowseHikes.browseHikes(BrowseHikesQuery)'),
('UC02','Enregistrer un randonneur','6','Visiteur membre du club','Code d’invitation disponible dans la source autorisée; utilisateur non encore enregistré.','Le membre choisit de créer son compte.',[
'Saisir code d’invitation, courriel, mot de passe, nom, téléphone, adresse, naissance, contact d’urgence et niveau.',
'Le système normalise le courriel (espaces retirés et casse neutralisée selon H08 pour l’unicité du compte), vérifie son unicité et les champs obligatoires.',
'Valider le code : existant, non expiré s’il possède une échéance, non consommé; vérifier qu’aucun compte n’a déjà utilisé ce code.',
'Présenter la décharge versionnée; recueillir l’acceptation. Pour moins de 18 ans, recueillir le nom du tuteur et son acceptation.',
'Créer atomiquement le compte et le profil avec adhésion ACTIVE, consommer l’invitation et conserver la preuve d’acceptation; protéger le secret par hachage adapté.',
'Afficher la réussite et inviter à se connecter; aucune adhésion au club ni invitation nouvelle n’est créée.'],[
'Code invalide/consommé, courriel existant, naissance future ou champ invalide : rejet sans compte ni consommation du code.',
'Décharge non acceptée ou tuteur manquant : rejet. Deux créations concurrentes sur le même courriel/code : une seule réussit.'],
'Un randonneur unique actif existe; invitation consommée une seule fois; aucune session automatique supposée.','Aucune création partielle.','RegisterHiker.registerHiker(RegisterHikerQuery)'),
('UC03','Se connecter','10','Utilisateur enregistré','Compte existant; service local d’identité disponible.','L’utilisateur soumet ses identifiants.',[
'Saisir le courriel et le mot de passe sur le formulaire de connexion.',
'Le système retrouve le compte et vérifie le secret sans le journaliser.',
'Émettre une session protégée et charger les rôles; ne pas confondre connexion et admissibilité liée à l’adhésion.',
'Afficher les fonctions autorisées; un compte à adhésion expirée peut consulter son profil mais ne peut pas s’inscrire.'],[
'Identifiants incorrects : message générique, aucune session.',
'Service d’identité indisponible : échec explicite; aucune élévation de privilège.'],
'Session liée au compte et aux permissions actuelles.','Aucune session créée.','Exclu des interfaces et contrats par les consignes du livrable (§2).'),
('UC04','Se déconnecter','11','Utilisateur connecté','Session active.','L’utilisateur choisit la déconnexion.',[
'Demander la déconnexion.',
'Le système invalide la session côté serveur et supprime les éléments locaux d’authentification.',
'Revenir à la consultation publique; toute nouvelle action protégée exige une nouvelle connexion.'],[
'Session déjà expirée : résultat équivalent à une déconnexion réussie.',
'Une requête ultérieure avec l’ancienne session est refusée.'],
'Session inutilisable; données métier préservées.','En cas d’incident, aucun succès d’invalidation distante non vérifié n’est annoncé.','Exclu des interfaces et contrats par les consignes du livrable (§2).'),
('UC05','S’inscrire à une randonnée','3','Randonneur connecté','Adhésion active; randonnée existante ouverte ou complète, non échue; difficulté admissible (H02).','Le randonneur confirme sa participation.',[
'Sélectionner une randonnée à partir de UC01 et confirmer.',
'Le système déduit l’identité depuis la session; revalide adhésion, difficulté, état et échéance.',
'Vérifier l’absence d’inscription active du même membre; réactiver une inscription annulée avec un nouvel ordre FIFO si nécessaire.',
'Dans une transaction, confirmer si une place est libre; si cette place est la dernière, passer la randonnée à COMPLÈTE et auditer la transition.',
'Si la capacité est atteinte, inscrire EN_ATTENTE avec un ordre strict (instant, séquence).',
'Enregistrer l’événement de notification; confirmer à l’écran, puis envoyer le courriel de confirmation ou le rang courant en attente.'],[
'Adhésion inactive, niveau excessif, doublon actif, échéance atteinte, événement fermé/annulé/terminé : rejet.',
'Deux demandes sur la dernière place : une confirmée, l’autre en attente. Une panne courriel ne retire pas l’inscription; reprise différée.'],
'Une inscription active unique existe, statut et capacité cohérents; notification émise ou en attente.','Aucun changement métier sur rejet.','SignUpForHike.signUpForHike(SignUpForHikeQuery)'),
('UC06','Annuler une inscription','4','Randonneur connecté','Inscription propre confirmée ou en attente; maintenant strictement avant l’échéance.','Le membre confirme son retrait.',[
'Sélectionner sa propre inscription et confirmer l’annulation.',
'Le système revalide propriétaire, état de l’inscription et échéance; verrouille l’attribution des places.',
'Passer l’inscription à ANNULÉE en conservant son historique.',
'Si une place confirmée a été libérée, examiner la liste FIFO; annuler les entrées devenues inadmissibles (H09), puis promouvoir le premier membre admissible.',
'Si la capacité reste atteinte, conserver COMPLÈTE; sinon passer à OUVERTE et auditer la transition éventuelle.',
'Consigner la notification de promotion et informer les personnes dont l’attente a été annulée pour inadmissibilité.'],[
'Autre propriétaire, inscription déjà annulée ou échéance atteinte : rejet sans changement.',
'Annulation d’une entrée en attente : aucune place ne se libère, ordre des autres conservé. Panne courriel : reprise différée.'],
'Inscription annulée; au plus une promotion pour une place libérée; aucune surcapacité.','Aucune annulation partielle ou promotion perdue.','CancelSignUp.cancelSignUp(CancelSignUpQuery)'),
('UC07','Mettre à jour un randonneur','7','Randonneur propriétaire ou administrateur','Session autorisée et profil cible existant.','L’utilisateur choisit le type de mise à jour.',[
'Charger les informations autorisées actuelles; choisir modifier le profil, modifier l’adhésion ou enregistrer une certification.',
'Pour le profil personnel, soumettre nom, téléphone, adresse, naissance, urgence et niveau; ne pas permettre de modifier rôles, courriel identifiant ou adhésion par ce formulaire.',
'Pour l’adhésion, un administrateur choisit ACTIVE, EXPIRÉE ou SUSPENDUE. Le processus d’adhésion externe demeure hors portée.',
'Pour la certification, un administrateur saisit numéro, délivrance, expiration et niveau d’organisateur; valider numéro non vide, dates ordonnées et niveau 1 à 4.',
'Valider tous les champs, enregistrer la seule modification autorisée et auditer l’auteur; une certification valide confère l’habilitation d’organisateur.',
'Afficher les données mises à jour; une modification de naissance conserve l’historique de décharge et nécessite une preuve de tuteur si le profil devient mineur.'],[
'Accès à un autre profil ou tentative d’auto-approbation : refus.',
'Champs invalides, nouvelle minorité sans preuve de tuteur, dates incohérentes ou version devenue obsolète : rejet atomique; recharger en cas de conflit.'],
'Profil, statut ou certification modifié selon la commande; autres champs inchangés; H14 appliquée.','Anciennes valeurs conservées sur rejet.','UpdateHiker.updateProfile / changeMembership / recordCertification (3 commandes)'),
('UC08','Fermer une randonnée','2','Ordonnanceur interne (SYSTEM)','Randonnée OUVERTE ou COMPLÈTE; échéance atteinte.','Passage de l’ordonnanceur ou contrôle à l’entrée d’une commande.',[
'Sélectionner une randonnée dont maintenant ≥ échéance.',
'Revalider son état dans une transaction.',
'Passer à FERMÉE; journaliser ancien/nouvel état, instant, cause échéance et auteur SYSTEM.',
'Interdire dès l’échéance toute inscription et annulation personnelle même si l’ordonnanceur a pris du retard.',
'Conserver les inscriptions et la liste d’attente sans promotion ultérieure.'],[
'Appel avant échéance : refus sans changement.',
'Déjà fermée/annulée/terminée : appel sans effet; aucune transition ni notification en double. Appel humain : non autorisé.'],
'Randonnée fermée ou état terminal déjà existant; aucune participation nouvelle.','Aucune fermeture anticipée.','CloseHike.closeHike(CloseHikeQuery)'),
('UC09','Envoyer un rappel de randonnée','9','Ordonnanceur interne; service météo et messagerie secondaires','Événement non annulé et non terminé; début-24 h ≤ maintenant < début; inscriptions confirmées.','Échéance de rappel, confirmation tardive ou reprise après incident.',[
'Charger date, heure, sentier et point de départ; sélectionner uniquement les inscriptions actuellement confirmées sans rappel déjà remis.',
'Demander une prévision pour la date de la randonnée et les coordonnées du point de départ, avec délai d’attente borné.',
'Si pluie ou neige prévue, ajouter un avertissement; si prévision impossible, préparer le rappel sans avertissement.',
'Créer une intention d’envoi par destinataire avec une clé stable (randonnée, inscription, rappel); inclure date, heure, sentier et point de rassemblement.',
'Revalider l’état avant remise à la messagerie; envoyer et consigner le résultat sans exposer les adresses des autres participants.',
'Lors d’une reprise, ne traiter que les rappels non remis et encore pertinents.'],[
'Panne météo : courriel normal sans avertissement; panne messagerie : en attente, reprise avant début.',
'Liste vide, événement annulé, appel trop tôt ou après début : aucun envoi. Une relance ne génère pas un nouveau rappel logique.'],
'Chaque destinataire admissible a un rappel remis ou un envoi en attente; état de randonnée inchangé.','Aucun envoi indu; résultat explicite pour les envois échoués.','SendHikeReminder.sendHikeReminder(SendHikeReminderQuery)'),
('UC10','Créer une randonnée','1','Organisateur connecté et approuvé','Adhésion active; certification enregistrée; données CCN utilisables.','L’organisateur soumet une nouvelle randonnée.',[
'Sélectionner un sentier CCN identifié; consulter permission, difficulté, saison et point de départ.',
'Saisir titre, description, début, durée, date limite et capacité.',
'Valider sentier réel de la région, randonnée permise, date dans la saison et niveau du chef au moins égal à la difficulté.',
'Vérifier la certification à la date de l’événement, le début futur et les bornes temporelles H05; rejeter les champs manquants.',
'Créer une randonnée identifiée de façon unique, liée au chef courant et au sentier CCN, avec l’instantané de référence et le statut OUVERTE.',
'Enregistrer la transition de création et son auteur; rendre la randonnée immédiatement consultable et accessible à l’inscription.'],[
'Certification expirant avant l’événement, niveau insuffisant, saison interdite/inconnue, sentier interdit ou données invalides : rejet explicite.',
'CCN indisponible : utiliser un instantané validé; sans instantané utilisable, rejeter cette création, les autres fonctions restant disponibles.'],
'Une randonnée ouverte unique existe, sans inscription; chef et transition de création tracés.','Aucune randonnée partielle; aucune modification du référentiel CCN.','CreateHike.createHike(CreateHikeQuery)'),
('UC11','Annuler une randonnée','8','Organisateur propriétaire ou administrateur','Randonnée existante OUVERTE, COMPLÈTE ou FERMÉE; maintenant < début.','L’acteur fournit un motif et confirme.',[
'Identifier l’événement et saisir un motif non vide.',
'Le système vérifie que l’acteur est son chef ou un administrateur; revalide l’instant et l’état.',
'Passer atomiquement la randonnée à ANNULÉE et toutes ses inscriptions confirmées/en attente à ANNULÉE; conserver leur historique.',
'Auditer l’auteur, le motif, l’heure et l’ancien état; ne promouvoir personne.',
'Créer un courriel d’annulation avec le motif pour chaque membre dont l’inscription était active; supprimer les rappels non encore remis.',
'Confirmer la réussite; remettre les notifications via la file locale.'],[
'Chef d’un autre événement, motif vide, début atteint ou événement terminé : rejet.',
'Événement déjà annulé : résultat sans effet et sans second courriel. Panne messagerie : annulation maintenue et notification reprise.'],
'Aucune inscription active ne subsiste; motif et auteur conservés; aucune nouvelle inscription permise.','Aucun changement partiel.','CancelHike.cancelHike(CancelHikeQuery)'),
('UC12','Générer un rapport d’utilisation des sentiers','12','Administrateur connecté','Sentier CCN connu; autorisation de rapport.','L’administrateur demande les statistiques.',[
'Sélectionner le sentier, la date de début et la date de fin.',
'Valider début ≤ fin et interpréter les dates dans le fuseau du club, bornes incluses.',
'Sélectionner les événements du sentier selon leur date locale de début.',
'Calculer nombre total d’événements, nombre d’événements annulés et nombre de places confirmées des événements non annulés; appliquer l’instantané historique aux événements terminés (H12).',
'Présenter période, sentier, valeurs et définition des indicateurs, avec la mention « réservations, pas présences réelles ».'],[
'Aucun événement : trois compteurs nuls.',
'Période inversée ou accès non administrateur : refus. CCN indisponible : calculer à partir des références locales.'],
'Rapport affiché sans modifier événements ou inscriptions.','Aucune donnée métier modifiée.','Exclu des interfaces et contrats par les consignes du livrable (§2).')]
# Kotlin DTOs: request identity is never trusted from a client-supplied actor id.
put(SRC/'application/dtos/queries/Queries.kt','''package ca.cairn.carhms.application.dtos.queries

import java.time.Instant
import java.time.LocalDate
import java.util.UUID

/** Transport only. Preconditions and invariants are specified by the contracts. */
enum class SkillLevel { BEGINNER, INTERMEDIATE, ADVANCED, EXPERT }
enum class MembershipStatus { ACTIVE, EXPIRED, SUSPENDED }
enum class TrailDifficulty { EASY, MODERATE, DIFFICULT, VERY_DIFFICULT }
data class EmergencyContactQuery(val name: String, val phone: String)
data class WaiverAcceptanceQuery(
    val version: String,
    val accepted: Boolean,
    val guardianName: String? = null,
    val guardianAccepted: Boolean = false
)
data class ProfileQuery(
    val name: String,
    val phone: String,
    val homeAddress: String,
    val birthDate: LocalDate,
    val emergencyContact: EmergencyContactQuery,
    val skillLevel: SkillLevel
)
data class BrowseHikesQuery(
    val trailName: String? = null,
    val date: LocalDate? = null,
    val difficulty: TrailDifficulty? = null,
    val includeFull: Boolean = false
)
data class RegisterHikerQuery(
    val requestId: UUID,
    val invitationCode: String,
    val email: String,
    val password: String,
    val profile: ProfileQuery,
    val waiver: WaiverAcceptanceQuery
) {
    // Avoid generated data-class toString leaking credentials through logging.
    override fun toString(): String = "RegisterHikerQuery(requestId=$requestId, redacted=true)"
}
data class SignUpForHikeQuery(val requestId: UUID, val hikeId: UUID)
data class CancelSignUpQuery(val requestId: UUID, val registrationId: UUID)
data class UpdateProfileQuery(
    val requestId: UUID,
    val expectedVersion: Long,
    val profile: ProfileQuery,
    val waiver: WaiverAcceptanceQuery? = null
)
data class ChangeMembershipQuery(
    val requestId: UUID,
    val hikerId: UUID,
    val expectedVersion: Long,
    val status: MembershipStatus
)
data class RecordCertificationQuery(
    val requestId: UUID,
    val hikerId: UUID,
    val expectedVersion: Long,
    val certificateNumber: String,
    val issuedOn: LocalDate,
    val expiresOn: LocalDate,
    val organizerLevel: SkillLevel
)
data class CloseHikeQuery(val requestId: UUID, val hikeId: UUID)
data class SendHikeReminderQuery(val requestId: UUID, val hikeId: UUID)
data class CreateHikeQuery(
    val requestId: UUID,
    val trailCcnId: String,
    val title: String,
    val description: String,
    val startsAt: Instant,
    val durationMinutes: Int,
    val registrationDeadline: Instant,
    val capacity: Int
)
data class CancelHikeQuery(val requestId: UUID, val hikeId: UUID, val reason: String)
''')
put(SRC/'application/dtos/HikeSummary.kt','''package ca.cairn.carhms.application.dtos

import ca.cairn.carhms.application.dtos.queries.TrailDifficulty
import java.time.Instant
import java.util.UUID

/** Public projection: no email, phone, address, or participant identity. */
data class HikeSummary(
    val id: UUID,
    val title: String,
    val description: String,
    val trailCcnId: String,
    val trailName: String,
    val difficulty: TrailDifficulty,
    val meetingPoint: String,
    val startsAt: Instant,
    val durationMinutes: Int,
    val registrationDeadline: Instant,
    val capacity: Int,
    val remainingPlaces: Int,
    val organizerDisplayName: String,
    val full: Boolean,
    val levelCompatible: Boolean?,
    val membershipAllowsSignUp: Boolean?,
    val trailDataAsOf: Instant
)
''')
commands=[
('BrowseHikes','browseHikes','BrowseHikesQuery','List<HikeSummary>','UC01','browse-hikes'),
('RegisterHiker','registerHiker','RegisterHikerQuery','UUID','UC02','register-hiker'),
('SignUpForHike','signUpForHike','SignUpForHikeQuery','UUID','UC05','sign-up-for-hike'),
('CancelSignUp','cancelSignUp','CancelSignUpQuery','Unit','UC06','cancel-sign-up'),
('UpdateHiker','updateProfile','UpdateProfileQuery','Unit','UC07','update-profile'),
('UpdateHiker','changeMembership','ChangeMembershipQuery','Unit','UC07','change-membership'),
('UpdateHiker','recordCertification','RecordCertificationQuery','Unit','UC07','record-certification'),
('CloseHike','closeHike','CloseHikeQuery','Unit','UC08','close-hike'),
('SendHikeReminder','sendHikeReminder','SendHikeReminderQuery','Unit','UC09','send-hike-reminder'),
('CreateHike','createHike','CreateHikeQuery','UUID','UC10','create-hike'),
('CancelHike','cancelHike','CancelHikeQuery','Unit','UC11','cancel-hike')]
for interface in dict.fromkeys(c[0] for c in commands):
 cs=[c for c in commands if c[0]==interface]
 imports='\n'.join('import ca.cairn.carhms.application.dtos.queries.'+c[2] for c in cs)
 if any(c[3]=='UUID' for c in cs):imports+='\nimport java.util.UUID'
 if interface=='BrowseHikes':imports+='\nimport ca.cairn.carhms.application.dtos.HikeSummary'
 methods='\n'.join(f'    /** {c[4]}; contract: {c[5]}.feature */\n    fun {c[1]}(query: {c[2]}): {c[3]}' for c in cs)
 put(SRC/f'application/usecases/{interface}.kt',f'''package ca.cairn.carhms.application.usecases

{imports}

/** Caller roles and server time come from trusted infrastructure, never from the DTO. */
interface {interface} {{
{methods}
}}''')
put(R/'backend/settings.gradle.kts','rootProject.name = "car-hms-contracts"')
put(R/'backend/build.gradle.kts','''plugins {
    kotlin("jvm") version "2.0.21"
}
repositories { mavenCentral() }
kotlin { jvmToolchain(17) }
// Initial feature contracts are specifications, not yet bound to step definitions.
// No Cucumber execution task is claimed by this deliverable.
''')
# Gherkin is written in French; each application command has its own feature file.
features={
'browse-hikes':'''  Scénario: Consultation publique filtrée et triée
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
''',
'register-hiker':'''  Plan du scénario: Décharge conforme à l'âge
    Étant donné une invitation valide non consommée et un courriel unique
    Et un profil complet dont l'âge local est <âge> ans
    Et une décharge versionnée acceptée et <preuve>
    Quand le visiteur soumet son enregistrement
    Alors <résultat>

    Exemples:
      | âge | preuve                                      | résultat                                      |
      | 18  | aucune preuve de tuteur                      | un compte actif est créé et le code consommé   |
      | 17  | un tuteur nommé ayant accepté                | un compte actif est créé et le code consommé   |
      | 17  | aucune preuve de tuteur                      | la demande est refusée sans consommer le code  |

  Plan du scénario: Rejet sans création partielle
    Étant donné une demande d'enregistrement avec <défaut>
    Quand le visiteur soumet son enregistrement
    Alors aucun compte n'est créé
    Et aucune invitation supplémentaire n'est consommée

    Exemples:
      | défaut                       |
      | un code déjà consommé        |
      | un code inconnu              |
      | un code expiré               |
      | un courriel déjà enregistré  |
      | une naissance future         |
      | une décharge non acceptée    |
      | un téléphone manquant        |

  Scénario: Course sur une invitation et reprise du même appel
    Étant donné deux demandes concurrentes pour une même invitation valide
    Quand les deux enregistrements sont soumis puis la demande gagnante est rejouée avec sa clé
    Alors un seul compte est créé et une seule invitation est consommée
    Et le mot de passe n'apparaît dans aucun journal
''',
'sign-up-for-hike':'''  Scénario: Dernière place attribuée atomiquement
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
''',
'cancel-sign-up':'''  Scénario: Promotion du premier membre admissible
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
''',
'update-profile':'''  Scénario: Mise à jour par le propriétaire
    Étant donné un membre connecté et la version actuelle de son profil
    Quand il soumet des coordonnées, une naissance et un niveau valides
    Alors son profil est mis à jour et sa version augmente
    Et son adhésion, ses rôles et sa certification sont inchangés

  Plan du scénario: Validation du profil
    Étant donné une mise à jour du profil avec <défaut>
    Quand le membre soumet la modification
    Alors la modification est refusée et l'ancien profil est conservé

    Exemples:
      | défaut                                |
      | un contact d'urgence sans téléphone   |
      | une date de naissance future          |
      | une version obsolète                  |
      | une nouvelle minorité sans décharge du tuteur |
      | une session absente                   |

  Scénario: Preuve de tuteur lors d'une correction de naissance
    Étant donné un membre dont la naissance corrigée indique 17 ans
    Quand il soumet le profil avec une décharge acceptée par un tuteur nommé
    Alors le profil et la preuve versionnée sont conservés ensemble
''',
'change-membership':'''  Plan du scénario: Statut administratif
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
''',
'record-certification':'''  Scénario: Habilitation par un administrateur
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
''',
'close-hike':'''  Plan du scénario: Fermeture à l'échéance
    Étant donné une randonnée <état> d'échéance "2026-11-10T15:00:00Z"
    Et l'horloge serveur indique "2026-11-10T15:00:00Z"
    Quand l'ordonnanceur appelle la fermeture
    Alors la randonnée devient fermée avec auteur SYSTEM et cause échéance
    Et les inscriptions existantes restent inchangées

    Exemples:
      | état     |
      | ouverte  |
      | complète |

  Scénario: Retard d'ordonnanceur
    Étant donné une randonnée ouverte dont l'échéance est passée et non encore traitée
    Quand un membre tente une inscription ou une annulation personnelle
    Alors l'opération est refusée même si le statut persistant n'a pas encore changé

  Scénario: Fermeture anticipée
    Étant donné une randonnée dont l'échéance est future
    Quand l'ordonnanceur appelle la fermeture
    Alors la fermeture est refusée sans transition

  Scénario: Rejeu et état terminal
    Étant donné une randonnée déjà fermée, annulée ou terminée
    Quand l'ordonnanceur appelle deux fois la fermeture
    Alors aucun changement d'état ni événement d'audit supplémentaire n'est créé
''',
'send-hike-reminder':'''  Plan du scénario: Contenu météorologique
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
''',
'create-hike':'''  Scénario: Création valide et certification à sa borne d'expiration
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
''',
'cancel-hike':'''  Plan du scénario: Annulation autorisée avant le début
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
'''}
for iface,fn,dto,ret,uc,slug in commands:
 put(RES/(slug+'.feature'),f'# language: fr\n@{uc} @{fn}\nFonctionnalité: Contrat initial de {fn}\n  Interface: {iface}; requête: {dto}.\n  Horloge et identité sont contrôlées par le contexte serveur.\n\n'+features[slug])
put(RES/'README.md','''# Contrats initiaux

Une fonctionnalité par commande (11), couvrant 9 interfaces et 9 cas d’utilisation. UC03, UC04 et UC12 sont exclus du code par les consignes mais analysés dans le rapport. UC07 donne lieu à trois commandes avec permissions différentes.

Les scénarios Gherkin sont des **spécifications initiales**. Aucune définition de pas, infrastructure Spring Boot ou exécution fonctionnelle n’est fournie à cette étape. Les tables « défaut/condition » représentent des fixtures isolées et autrement valides, sauf indication contraire.

Les horloges sont injectées côté serveur. Les instants utilisent UTC; les dates de naissance, saisons et certificats sont évaluées dans America/Toronto. Les identifiants d’acteur et l’heure d’appel ne proviennent jamais du DTO utilisateur. Les clés requestId sont liées à l’acteur et à la commande; rejouer avec une charge différente est rejeté.

Un rejet doit laisser l’état métier intact. Les notifications sont des intentions durables validées avec l’opération métier. La garantie est la déduplication logique locale; une livraison exactement une fois chez un fournisseur externe ne peut pas être garantie sans son concours.

Les interfaces Unit signalent une violation par une erreur applicative typée à définir à l’implémentation; aucun code HTTP n’est imposé par le modèle initial. Les commandes de fermeture et de rappel sont réservées à SYSTEM.
''')
# Report: same content is delivered as PDF and editable Markdown.
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleCAR',fontName='Helvetica-Bold',fontSize=25,leading=30,textColor=colors.HexColor('#163e43'),spaceAfter=18))
styles.add(ParagraphStyle(name='H1CAR',fontName='Helvetica-Bold',fontSize=18,leading=23,textColor=colors.HexColor('#163e43'),spaceAfter=14))
styles.add(ParagraphStyle(name='H2CAR',fontName='Helvetica-Bold',fontSize=11,leading=15,textColor=colors.HexColor('#176c72'),spaceBefore=10,spaceAfter=5))
styles.add(ParagraphStyle(name='BodyCAR',fontName='Helvetica',fontSize=10,leading=14,spaceAfter=7))
styles.add(ParagraphStyle(name='SmallCAR',fontName='Helvetica',fontSize=8.4,leading=11,spaceAfter=5))
styles.add(ParagraphStyle(name='CoverSmall',fontName='Helvetica',fontSize=12,leading=18,spaceAfter=9))
story=[]; md=[]; headings=[]
def P(t,style='BodyCAR'):
 return Paragraph(html.escape(t).replace('\n','<br/>'),styles[style])
def para(t):story.append(P(t));md.append(t+'\n')
def title(t):
 if story:story.append(PageBreak())
 story.append(P(t,'H1CAR'));md.append('\n# '+t+'\n');headings.append(t)
def h(t):story.append(P(t,'H2CAR'));md.append('\n## '+t+'\n')
def bullets(items,number=False):
 for i,t in enumerate(items,1):
  label=f'{i}.' if number else '•'
  story.append(P(label+' '+t));md.append(f'{i}. {t}' if number else '- '+t)
 md.append('')
def table(headers,rows,widths):
 data=[[P(t,'SmallCAR') for t in headers]]+[[P(str(t),'SmallCAR') for t in row] for row in rows]
 tb=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
 tb.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e2eeee')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#176c72')),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#d4dede')),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]));story.append(tb)
 md.append('| '+' | '.join(headers)+' |\n| '+' | '.join('---' for _ in headers)+' |')
 for row in rows:md.append('| '+' | '.join(str(x).replace('\n',' ') for x in row)+' |')
 md.append('')
# cover
story.append(Spacer(1,54));story.append(P('CAR-HMS','TitleCAR'));story.append(P('Livrable 1\nAnalyse initiale du domaine','TitleCAR'))
md.append('# CAR-HMS - Livrable 1 : Analyse initiale du domaine\n')
for t in ['Système de gestion des événements de randonnée du Club Cairn','SEG 3102 · Automne 2026','Date de préparation : 22 octobre 2026','Professeur : Kalenji Kalala']:
 story.append(P(t,'CoverSmall'));md.append(t+'\n')
story.append(Spacer(1,24))
table(['Membre','Numéro étudiant'],[['Mohamed Khalil EL OTHMANI','300389979'],['Mohamed Khalil Mehdaoui','300371110']],[340,155])
story.append(Spacer(1,25));para('Analyse initiale du domaine et contrats applicatifs. Les décisions d’analyse sont identifiées comme hypothèses, sans être attribuées au client.')
title('2. Sommaire exécutif et équipe')
h('2.1 Sommaire exécutif')
para('Ce document s’adresse au client Cairn, à l’équipe de développement et à l’évaluateur du cours; il fixe la portée, les hypothèses et le modèle initial du domaine CAR-HMS. Il décrit les interactions externes, justifie sept sous-domaines, détaille les douze cas d’utilisation et relie neuf interfaces Kotlin et onze contrats Cucumber aux règles métier, puis présente cinq observations de revue des exigences.')
h('2.2 Description de l’équipe et des rôles')
table(['Membre','Travail réellement effectué pour ce livrable'],[
['Mohamed Khalil EL OTHMANI\n300389979','Analyse des exigences, hypothèses et revue des contradictions; diagramme de contexte et classification des sous-domaines; rédaction et mise en forme du rapport.'],
['Mohamed Khalil Mehdaoui\n300371110','Structure des paquetages du domaine; interfaces Kotlin et DTO; rédaction des contrats Cucumber et vérification de leur correspondance avec les commandes.']],[195,300])
para('Travail commun aux deux membres : analyse des cas d’utilisation, vérification de la cohérence entre rapport et code et relecture finale. Aucun pourcentage ni nombre d’heures n’est indiqué; ces renseignements sont facultatifs dans les consignes.')
h('2.3 Portée et pièces livrées')
para('Inclus : consultation, compte sur invitation, profil et habilitation, planification, inscriptions/attente, notifications et statistiques. Exclus : recrutement, émission des invitations, processus complet d’adhésion, ressources humaines, activités physiques et suivi des présences. Les données CCN demeurent la référence externe.')
para('Le dossier backend contient uniquement le squelette du domaine, les contrats d’application et les fonctionnalités Cucumber demandés. Le produit final utilisera Angular/TypeScript et Kotlin/Spring Boot; aucune interface Web ni implémentation Spring Boot n’est requise pour ce livrable initial [R1, §2.3; R2, §2].')
h('2.4 Guide de lecture')
para('Sections 3 à 6 : décisions et modèle de haut niveau. Section 7 : douze fiches de cas d’utilisation. Section 8 : revue bonus distincte des hypothèses. Section 9 : traçabilité et conformité. Section 10 : références et points à confirmer.')
for first,last,label in [(0,8,'3. Hypothèses (1/2)'),(8,len(assumptions),'3. Hypothèses (2/2)')]:
 title(label)
 for code,name,body in assumptions[first:last]:
  h(code+' · '+name);para(body)
 if first==0:para('Statut de ces décisions : propositions de l’équipe à valider avec le client. Elles rendent les contrats déterministes sans ajouter silencieusement des exigences à CAR-Req-01.')
title('4. Diagramme de contexte du système')
para('La frontière représente l’application Web CAR-HMS et ses composants locaux. Les acteurs et services externes échangent les informations décrites ci-dessous. L’ordonnanceur, le cache et la base de données sont internes; ils ne constituent pas des systèmes clients indépendants.')
d=Drawing(495,278)
def box(d,x,y,w,hh,text,fill='#edf5f4'):
 d.add(Rect(x,y,w,hh,rx=6,ry=6,fillColor=colors.HexColor(fill),strokeColor=colors.HexColor('#46767a')))
 for i,line in enumerate(text.split('\n')):d.add(String(x+w/2,y+hh/2+(len(text.split('\n'))-1)*6-i*12,line,fontName='Helvetica',fontSize=9,textAnchor='middle',fillColor=colors.HexColor('#163e43')))
def arrow(d,x1,y1,x2,y2):
 import math
 d.add(Line(x1,y1,x2,y2,strokeColor=colors.HexColor('#46767a'),strokeWidth=1))
 a=math.atan2(y2-y1,x2-x1); sz=5
 d.add(Polygon([x2,y2,x2-sz*__import__('math').cos(a-.5),y2-sz*__import__('math').sin(a-.5),x2-sz*__import__('math').cos(a+.5),y2-sz*__import__('math').sin(a+.5)],fillColor=colors.HexColor('#46767a'),strokeColor=None))
box(d,158,75,179,145,'CAR-HMS\nConsultation et profils\nPlanification et inscriptions\nRapports et notifications\nBase, cache, ordonnanceur','#d6e9e7')
box(d,0,206,130,55,'Visiteur / membre\nOrganisateur / admin')
box(d,0,77,130,58,'Processus du club\nadhésion / invitations')
box(d,365,214,130,48,'Données CCN\nsentiers et permissions')
box(d,365,129,130,48,'Service météo\nprévisions au départ')
box(d,365,33,130,48,'Service courriel\nremise des messages')
arrow(d,130,228,158,194);arrow(d,158,179,130,213)
arrow(d,130,108,158,120)
arrow(d,337,192,365,234);arrow(d,365,223,337,180)
arrow(d,337,150,365,156);arrow(d,365,143,337,138)
arrow(d,337,103,365,63);arrow(d,365,49,337,88)
story.append(d);md.append('Diagramme : voir contexte.svg (version vectorielle modifiable).\n')
table(['Élément externe','Entrées / sorties à la frontière'],[
['Utilisateurs humains','Demandes et confirmations → CAR-HMS; listes, résultats, profils autorisés et rapports ← CAR-HMS.'],
['Processus administratif du club','Codes préalables et décisions d’adhésion/certification saisis par les acteurs autorisés. Aucune API externe de membres n’est supposée.'],
['CCN','Requête de données → CCN; références de sentiers, géométrie, permissions et caractéristiques ← CCN. Pas d’écriture dans la CCN.'],
['Météo','Coordonnées et date → service; prévision facultative ← service.'],
['Messagerie','Courriels et destinataires → service; accusés ou erreurs de remise ← service.']],[130,365])
para('Sécurité : contrôle d’accès à chaque fonction protégée; stockage authentifié et chiffré; minimisation des données publiques. Résilience : données CCN mémorisées, météo facultative et notifications en attente [R1, §1.4, §2.2; H06, H11, H13].')
# export drawing also SVG
from reportlab.graphics import renderSVG
renderSVG.drawToFile(d,str(R/'rapport/contexte.svg'))
for group,label in [(subdomains[:4],'5. Sous-domaines (1/2)'),(subdomains[4:],'5. Sous-domaines (2/2)')]:
 title(label)
 for key,name,kind,why,model,scope in group:
  h(name+' · '+kind)
  para(why);para('Concepts : '+model+' Responsabilité : '+scope+' Paquetage : domain.'+key+'.')
 if group==subdomains[4:]:
  h('Dépendances et frontières')
  para('La planification consulte les profils/habilitations et le référentiel de sentiers. Les inscriptions consultent la planification et les profils. Le cœur produit les événements consommés par les notifications et les projections de rapports. L’identité fournit le contexte d’appel aux services applicatifs; elle n’attribue pas à elle seule l’admissibilité à une randonnée.')
  para('Ces frontières constituent des sous-domaines conceptuels et des paquetages, pas une obligation de microservices ou de bases distinctes. Une transaction locale peut protéger capacité, inscription et intention de notification.')
title('6. Modèle de domaine de haut niveau')
table(['Concept / lien','Contenu et cardinalité'],[
['Randonneur','Identité par courriel unique; coordonnées, naissance, urgence, niveau et statut d’adhésion. Un compte a un profil. Un administrateur est un rôle d’accès, pas une sous-classe métier obligatoire.'],
['Certification','Un randonneur possède 0..1 certification courante; les versions antérieures sont conservées en historique. Numéro, délivrance, expiration, niveau. Organisateur = randonneur habilité.'],
['Décharge','Un randonneur conserve 1..* preuves versionnées; chaque preuve a un acceptant et un instant, ainsi que le tuteur si nécessaire.'],
['Randonnée → organisateur','Chaque randonnée a exactement 1 organisateur; un organisateur dirige 0..* randonnées. Titre, description, début, durée, échéance, capacité et statut.'],
['Randonnée → sentier','Exactement 1 référence CCN et son instantané validé; une référence sert 0..* randonnées. Le départ vient du sentier. La difficulté n’est pas saisie indépendamment.'],
['Inscription','Lie exactement 1 randonneur à exactement 1 randonnée. Chaque côté a 0..* inscriptions; unicité du couple. Statut, instant de demande, séquence et historique.'],
['Historique de transition','Une randonnée possède 1..* transitions, incluant la création : ancien état éventuel, nouvel état, auteur, cause et instant. SYSTEM représente les transitions automatiques.'],
['Notification','Une intention référence son événement métier et son destinataire; statut de remise et clé de déduplication. Pas d’envoi réseau requis dans la transaction métier.'],
['Rapport','Projection calculée, pas entité possédant les événements. Aucune notion de présence réelle n’est introduite.']],[145,350])
h('Cycle de vie de la randonnée')
para('Création → OUVERTE. Dernière place prise : OUVERTE → COMPLÈTE. Place libérée sans remplacement : COMPLÈTE → OUVERTE. Échéance atteinte : OUVERTE ou COMPLÈTE → FERMÉE. Avant le début : OUVERTE, COMPLÈTE ou FERMÉE → ANNULÉE. Au début, sans annulation : FERMÉE → TERMINÉE selon H04. ANNULÉE et TERMINÉE sont terminales.')
para('TERMINÉE est un état métier analytique issu du glossaire, bien que la liste du §2.1 ne le mentionne pas. Il signifie événement prévu passé, sans assertion sur sa réalisation physique. Un traitement en retard ferme puis termine dans cet ordre en conservant les instants de prise d’effet et de traitement.')
title('6.1 Invariants et décisions transversales')
bullets([
'I01 · Autorisation : compte authentifié pour toute action protégée; inscription initiale et connexion publiques par H01. SYSTEM seul déclenche fermeture et rappels.',
'I02 · Capacité : 0 ≤ inscriptions confirmées ≤ capacité; COMPLÈTE si capacité atteinte avant échéance; aucune attente prioritaire contournée lors d’une place libérée.',
'I03 · Admissibilité : adhésion active et d ≤ min(4,n+1) à l’inscription/promotion; niveau du chef ≥ d et certification couvrant l’événement à la création.',
'I04 · Temps : maintenant < échéance pour participer ou se retirer; début-14 jours ≤ échéance < début; annulation globale permise jusqu’à maintenant < début.',
'I05 · Référence : CCN est autorité pour sentier, permission, difficulté, saison et départ. Un instantané local n’est pas un catalogue éditable par le club.',
'I06 · Atomicité : places, inscription, transitions et intentions de notification sont cohérentes dans une même transaction logique; les appels externes sont hors de cette transaction.',
'I07 · Historique : aucune suppression physique d’un événement ou d’une inscription n’efface son auteur, son ordre, son motif ou les valeurs nécessaires aux rapports.',
'I08 · Confidentialité : un visiteur n’obtient jamais coordonnées, urgence, naissance, courriel ni liste nominative des participants. Les requêtes d’enregistrement ne sont jamais journalisées en clair.',
'I09 · Répétition : requestId est unique par acteur et commande; un rejeu identique renvoie le résultat initial sans nouveau changement, une charge différente est refusée.',
'I10 · Rapport : les compteurs distinguent événements, annulations et places réservées; aucune estimation de fréquentation réelle n’est présentée comme une observation.'
])
h('Conventions pour les fiches et les contrats')
para('Les préconditions décrivent l’état requis; elles sont revalidées côté serveur. Les branches d’erreur décrivent les appels qui ne les respectent pas. Les étapes nominales sont ordonnées; les postconditions distinguent réussite et rejet. Les notifications sont considérées acceptées lorsque l’intention durable est créée; leur remise peut être différée.')
para('La correspondance lexicale est : OUVERTE/OPEN, COMPLÈTE/FULL, FERMÉE/CLOSED, ANNULÉE/CANCELLED, TERMINÉE/FINISHED; CONFIRMÉE/CONFIRMED, EN_ATTENTE/WAITLISTED, ANNULÉE/CANCELLED. Les enums de transport Kotlin utilisent les termes anglais; le rapport et Gherkin utilisent le français.')
for code,name,priority,actor,pre,trigger,steps,alts,post,fail,api in ucs:
 title('7. '+code+' · '+name)
 para('Priorité source : '+priority+' [R1, §3.2]. Acteur principal : '+actor+'.')
 h('Préconditions');para(pre)
 h('Déclencheur');para(trigger)
 h('Scénario nominal');bullets(steps,True)
 h('Variantes et erreurs');bullets(alts)
 h('Postconditions');para('Réussite : '+post);para('Rejet : '+fail)
 h('Contrat applicatif');para(api)
bonus=[
('B01','Authentification et création du premier compte',
'« Tout accès aux fonctionnalités du CAR-HMS autre que la consultation des randonnées ouvertes doit exiger une authentification et une autorisation. » [R1, §2.2, p. 3]',
'UC Enregistrer un randonneur permet pourtant à un visiteur de créer son premier compte [R1, p. 7]; Se connecter précède nécessairement une session. Une application littérale rendrait l’amorçage impossible.',
'H01 : exceptions limitées à l’enregistrement par invitation et à la connexion; consultation publique maintenue.',
'Frontière identité/profils : RegisterHiker accepte un contexte anonyme, mais impose code valide, unicité et décharge. Les autres écritures conservent leur contrôle de rôle.',
'register-hiker.feature : enregistrement du visiteur, code invalide et course sur une invitation. Se connecter reste exclu des interfaces selon R2.'),
('B02','Deux formulations incompatibles des niveaux',
'« Un randonneur ne peut s’inscrire qu’aux randonnées cotées à son niveau d’habileté ou à un niveau au-dessus, lorsque son adhésion est active. » [R1, §1.5, p. 2]',
'Le résumé d’inscription parle d’une difficulté « au plus d’un niveau supérieure » [R1, p. 7], ce qui inclut les niveaux inférieurs. De plus, les deux échelles n’utilisent pas les mêmes mots.',
'H02 : ordre explicite sur quatre niveaux; d ≤ min(4,n+1), sans borne inférieure. Cette interprétation privilégie le résumé de UC et l’accessibilité des sorties faciles aux experts.',
'La règle d’admissibilité du sous-domaine registration utilise un rang normalisé; le niveau du chef obéit à une comparaison distincte chef ≥ difficulté.',
'sign-up-for-hike.feature : débutant/modéré accepté, débutant/difficile refusé, avancé/facile accepté et expert/très difficile accepté.'),
('B03','État complet et accès à la liste d’attente',
'« Le CAR-HMS doit permettre aux randonneurs de s’inscrire aux randonnées ouvertes et doit tenir une liste d’attente lorsqu’une randonnée est complète. » [R1, §2.1, p. 3]',
'Le parcours public de UC Parcourir les randonnées ne liste que les randonnées ouvertes [R1, p. 7]. Sans accès aux complètes, la liste d’attente exigée devient inaccessible par le parcours normal.',
'H03 : ajouter un filtre authentifié incluant les complètes avant l’échéance; accepter l’inscription vers attente pour l’état COMPLÈTE. La consultation publique reste limitée aux ouvertes.',
'BrowseHikesQuery.includeFull et garde de SignUpForHike autorisent COMPLÈTE avant échéance; capacité et places restantes restent cohérentes.',
'browse-hikes.feature : une complète apparaît à 0 place; sign-up-for-hike.feature : la demande suivante rejoint l’attente au rang 1.'),
('B04','Déclencheurs automatiques et auteur du cycle',
'« Le CAR-HMS doit enregistrer l’utilisateur qui a effectué chaque étape du cycle de vie d’une randonnée. » [R1, §2.1, p. 3]',
'Le diagramme rattache Fermer une randonnée et Envoyer un rappel à un randonneur [R1, fig. 1, p. 5], tandis que les résumés les déclenchent par échéance et par début moins un jour [R1, p. 7-8]. Une action planifiée n’a pas forcément d’utilisateur humain.',
'H04 : ordonnanceur interne, principal SYSTEM et cause conservée; les règles temporelles s’appliquent même si son passage tarde. TERMINÉE conserve la même convention d’audit.',
'planning conserve un auteur humain ou système pour chaque transition; CloseHike et SendHikeReminder exigent un appel interne autorisé.',
'close-hike.feature : égalité à l’échéance, retard et rejeu sans double audit; send-hike-reminder.feature : déclenchement aux 24 heures.'),
('B05','Participants statistiques et absence de présence',
'« Le rapport présente des statistiques sur les randonnées de ce sentier pendant la période indiquée (nombre de randonnées, nombre de participants, nombre de randonnées annulées). » [R1, §3.2, p. 8]',
'Le terme participants n’est pas défini; or « Ce qui se passe le jour de la randonnée n’est pas suivi par le système » [R1, §1.5, p. 3]. Les présences réelles et les personnes distinctes ne se déduisent pas du nombre d’inscriptions.',
'H12 : dates incluses selon le début local; somme des réservations confirmées sur événements non annulés, instantané figé pour les terminés; compteur total incluant annulées.',
'reporting conserve une projection historique de réservations et expose la définition de l’indicateur. Aucun concept de présence n’est inventé.',
'UC12 : période vide donne (0,0,0). Exemple de vérification : deux événements, un non annulé avec 3 confirmés et un annulé avec 2 anciens confirmés donnent (2,3,1). UC12 est exclu des contrats Cucumber par R2.')]
for group,label in [(bonus[:3],'8. Bonus · revue des exigences (1/2)'),(bonus[3:],'8. Bonus · revue des exigences (2/2)')]:
 title(label)
 for code,name,quote,issue,resolution,impact,evidence in group:
  h(code+' · '+name);para(quote);para('Lacune : '+issue);para('Résolution : '+resolution);para('Effet sur le modèle/contrat : '+impact);para('Vérification : '+evidence)
 if group==bonus[3:]:para('Ces cinq observations expliquent l’origine de décisions; elles ne remplacent pas la liste complète des hypothèses de la section 3. Les autres points à confirmer ne sont pas présentés comme des observations bonus supplémentaires.')
title('9. Traçabilité des artefacts et conformité')
table(['Cas','Interface et commande','Contrat .feature'],[[c[4],c[0]+'.'+c[1],c[5]] for c in commands],[52,210,233])
para('Les onze DTO racines sont dans application.dtos.queries.Queries.kt; ProfileQuery, EmergencyContactQuery et WaiverAcceptanceQuery composent les requêtes. HikeSummary est une projection de sortie dans application.dtos. Le paquetage usecases contient neuf interfaces; UpdateHiker possède trois fonctions pour séparer les permissions.')
h('Couverture des consignes')
table(['Exigence de remise [R2]','Emplacement / preuve'],[
['Couverture et contributions','Sections 1 et 2; professeur, identités et tâches des deux membres renseignés.'],
['Hypothèses, contexte, sous-domaines','Sections 3 à 6; 7 sous-paquetages domain avec README.'],
['12 analyses de cas d’utilisation','Section 7 : préconditions, étapes, variantes et postconditions.'],
['Commandes / DTO / contrats','9 interfaces, 11 fonctions, 11 DTO racines, 11 fonctionnalités.'],
['Exceptions au code','UC03, UC04 et UC12 décrits dans le rapport; aucune interface ni fonctionnalité correspondante.'],
['Bonus jusqu’à 5 éléments','Section 8 : 5 observations avec citation, résolution et effet.'],
['Dépôt GitHub','Dossier backend prêt à intégrer; publication et URL du dépôt à fournir par l’équipe.']],[175,320])
title('10. Références et préparation de la remise')
h('10.1 Documents de référence')
para('[R1] Kalonji Kalala. Système de gestion des événements de randonnée du Cairn (CAR-HMS), document des exigences initiales, CAR-Req-01. SEG 3102, Université d’Ottawa, automne 2026. Fichier fourni : Exigences Initiales-CAR-HMS_exigences_initiales_FR1.pdf, 8 pages. Références pertinentes : contexte/portée p. 1-2; glossaire p. 2-3; exigences p. 3-4; diagramme p. 5-6; cas d’utilisation p. 7-8.')
para('[R2] Boqi Chen. SEG 3102, Projet, Livrable 1 : domaine initial. Université d’Ottawa, automne 2026. Fichier fourni : SEG3102_Livrable1_FR1.pdf, 3 pages. Plan du rapport p. 1; structure de code et exceptions p. 2; critères du bonus p. 2-3.')
para('Les liens vers la CCN présents dans R1 désignent de futures sources opérationnelles; aucune consultation du catalogue en direct ni validation d’un fournisseur météo n’est prétendue ici. Les règles de ce livrable sont tirées des deux PDF et des hypothèses explicites.')
h('10.2 Points à confirmer avant dépôt')
bullets(['Vérifier les informations de couverture et le tableau des contributions; aucun nom d’équipe distinct n’est utilisé, conformément au choix des membres.',
'Valider les hypothèses avec le client/enseignant, en priorité l’admissibilité aux niveaux inférieurs, le calendrier saisonnier CCN, la revalidation des attentes et le sens de « participants ».',
'Intégrer backend dans le dépôt GitHub de l’équipe et vérifier l’arborescence et les droits d’accès de l’évaluateur. Les consignes ne rendent pas explicitement obligatoire une branche appelée contracts : ce nom apparaît dans l’exemple.',
'La compilation directe des fichiers Kotlin a réussi (compilateur 2.0.21, JDK 21, cible JVM 17). Le parseur Gherkin officiel accepte 11 fonctionnalités et 100 scénarios développés. L’exécution métier nécessitera les définitions de pas et une implémentation ultérieure.',
'Relire le rapport, vérifier les champs administratifs, puis remettre selon la procédure et la date annoncées dans le cours. Les PDF fournis n’indiquent pas la date limite.'])
h('10.3 Limite de validation')
para('La grille détaillée de correction n’est pas fournie. Ce dossier vise l’ensemble des exigences explicites et le bonus, sans garantir une note. Les contrôles automatiques locaux portent sur la structure, la correspondance entre commandes/DTO/contrats, la compilation des signatures Kotlin, la syntaxe Gherkin et le rendu du PDF; ils ne prouvent pas l’implémentation du produit.')
put(R/'rapport/Livrable1_CAR-HMS.md','\n'.join(md))
def footer(c,doc):
 c.setStrokeColor(colors.HexColor('#b7cece'));c.line(50,43,545,43)
 c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#536a6c'))
 c.drawString(50,30,'CAR-HMS · SEG 3102 · Livrable 1 · 22 octobre 2026');c.drawRightString(545,30,str(doc.page))
doc=SimpleDocTemplate(str(R/'rapport/Livrable1_CAR-HMS.pdf'),pagesize=(595.28,841.89),leftMargin=50,rightMargin=50,topMargin=48,bottomMargin=58,title='CAR-HMS - Livrable 1 : domaine initial',author='Mohamed Khalil EL OTHMANI et Mohamed Khalil Mehdaoui')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
put(R/'README.md','''# CAR-HMS - Livrable 1

## Contenu
- `rapport/Livrable1_CAR-HMS.pdf` : rapport final à relire avant remise.
- `rapport/Livrable1_CAR-HMS.md` : texte modifiable du même rapport.
- `rapport/contexte.svg` : diagramme de contexte vectoriel.
- `backend/src/main/kotlin/ca/cairn/carhms/domain/` : 7 sous-domaines documentés.
- `backend/src/main/kotlin/ca/cairn/carhms/application/usecases/` : 9 interfaces, 11 fonctions.
- `backend/src/main/kotlin/ca/cairn/carhms/application/dtos/queries/` : requêtes d'application.
- `backend/src/test/resources/contracts/` : 11 fonctionnalités Cucumber en français.
- `tools/verify.py` : contrôle structurel reproductible, sans dépendance tierce.
- `tools/generate.py` : source de génération du dossier et du PDF (Python + ReportLab).
- `VALIDATION.md` : contrôles effectués et limites.

## Informations de remise
Professeur : Kalenji Kalala. Aucun nom d’équipe distinct. Les identités, numéros étudiants et contributions des deux membres sont intégrés au rapport. Valider les hypothèses avec le client/enseignant.

## Vérification
Depuis ce dossier : `python3 tools/verify.py`.
Pour compiler le squelette si Gradle et JDK 17 sont installés : `cd backend` puis `gradle compileKotlin`. Les dépendances doivent pouvoir être téléchargées. Aucun wrapper Gradle n'est inclus; ne pas annoncer une compilation locale si elle n'a pas été exécutée.

Il s'agit de contrats initiaux : aucune définition de pas Cucumber ni implémentation métier n'est incluse. Les contrats ne sont pas des tests fonctionnels exécutables à ce stade. Le build Gradle sert seulement à compiler les signatures Kotlin.

## Dépôt
Le code est publié sur la branche `main` du dépôt de l'équipe : https://github.com/elothkhalil/livrable1seg3502. Le dossier `backend` contient la structure et les contrats à évaluer; le dossier `rapport` contient le document. Aucun secret ni fichier personnel du workspace n'est inclus.

## Mise à jour du rapport
Modifier `tools/generate.py`, puis exécuter `python3 tools/generate.py` avec ReportLab. Une modification du Markdown seul ne modifie pas automatiquement le PDF. Vérifier ensuite le PDF rendu. Les PDF sources restent dans Downloads et ne sont pas redistribués dans l'archive.
''')
put(R/'manifest.json',json.dumps({'subdomains':[s[0] for s in subdomains],'commands':[{'interface':i,'method':m,'dto':q,'usecase':u,'contract':f} for i,m,q,ret,u,f in commands]},ensure_ascii=False,indent=2))
print('Generated report and source at',R)
