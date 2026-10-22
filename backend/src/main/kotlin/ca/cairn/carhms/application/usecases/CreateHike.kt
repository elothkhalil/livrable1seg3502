package ca.cairn.carhms.application.usecases

import ca.cairn.carhms.application.dtos.queries.CreateHikeQuery
import java.util.UUID

/** Caller roles and server time come from trusted infrastructure, never from the DTO. */
interface CreateHike {
    /** UC10; contract: create-hike.feature */
    fun createHike(query: CreateHikeQuery): UUID
}
