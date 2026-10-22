package ca.cairn.carhms.application.dtos.queries

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
