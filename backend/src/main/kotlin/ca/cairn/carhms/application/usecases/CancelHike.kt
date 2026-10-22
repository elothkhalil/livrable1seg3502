package ca.cairn.carhms.application.usecases

import ca.cairn.carhms.application.dtos.queries.CancelHikeQuery

/** Caller roles and server time come from trusted infrastructure, never from the DTO. */
interface CancelHike {
    /** UC11; contract: cancel-hike.feature */
    fun cancelHike(query: CancelHikeQuery): Unit
}
