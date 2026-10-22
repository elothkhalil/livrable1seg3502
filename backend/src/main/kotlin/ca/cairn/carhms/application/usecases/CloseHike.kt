package ca.cairn.carhms.application.usecases

import ca.cairn.carhms.application.dtos.queries.CloseHikeQuery

/** Caller roles and server time come from trusted infrastructure, never from the DTO. */
interface CloseHike {
    /** UC08; contract: close-hike.feature */
    fun closeHike(query: CloseHikeQuery): Unit
}
