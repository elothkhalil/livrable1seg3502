package ca.cairn.carhms.application.dtos

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
