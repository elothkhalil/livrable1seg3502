package ca.cairn.carhms.application.usecases

import ca.cairn.carhms.application.dtos.queries.UpdateProfileQuery
import ca.cairn.carhms.application.dtos.queries.ChangeMembershipQuery
import ca.cairn.carhms.application.dtos.queries.RecordCertificationQuery

/** Caller roles and server time come from trusted infrastructure, never from the DTO. */
interface UpdateHiker {
    /** UC07; contract: update-profile.feature */
    fun updateProfile(query: UpdateProfileQuery): Unit
    /** UC07; contract: change-membership.feature */
    fun changeMembership(query: ChangeMembershipQuery): Unit
    /** UC07; contract: record-certification.feature */
    fun recordCertification(query: RecordCertificationQuery): Unit
}
