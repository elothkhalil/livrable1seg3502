package ca.cairn.carhms.application.usecases

import ca.cairn.carhms.application.dtos.queries.SignUpForHikeQuery
import java.util.UUID

/** Caller roles and server time come from trusted infrastructure, never from the DTO. */
interface SignUpForHike {
    /** UC05; contract: sign-up-for-hike.feature */
    fun signUpForHike(query: SignUpForHikeQuery): UUID
}
