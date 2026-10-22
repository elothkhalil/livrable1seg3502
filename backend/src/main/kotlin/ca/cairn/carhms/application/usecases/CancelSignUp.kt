package ca.cairn.carhms.application.usecases

import ca.cairn.carhms.application.dtos.queries.CancelSignUpQuery

/** Caller roles and server time come from trusted infrastructure, never from the DTO. */
interface CancelSignUp {
    /** UC06; contract: cancel-sign-up.feature */
    fun cancelSignUp(query: CancelSignUpQuery): Unit
}
