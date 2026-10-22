package ca.cairn.carhms.application.usecases

import ca.cairn.carhms.application.dtos.queries.BrowseHikesQuery
import ca.cairn.carhms.application.dtos.HikeSummary

/** Caller roles and server time come from trusted infrastructure, never from the DTO. */
interface BrowseHikes {
    /** UC01; contract: browse-hikes.feature */
    fun browseHikes(query: BrowseHikesQuery): List<HikeSummary>
}
