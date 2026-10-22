package ca.cairn.carhms.application.usecases

import ca.cairn.carhms.application.dtos.queries.RegisterHikerQuery
import java.util.UUID

/** Caller roles and server time come from trusted infrastructure, never from the DTO. */
interface RegisterHiker {
    /** UC02; contract: register-hiker.feature */
    fun registerHiker(query: RegisterHikerQuery): UUID
}
