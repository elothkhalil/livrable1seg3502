package ca.cairn.carhms.application.usecases

import ca.cairn.carhms.application.dtos.queries.SendHikeReminderQuery

/** Caller roles and server time come from trusted infrastructure, never from the DTO. */
interface SendHikeReminder {
    /** UC09; contract: send-hike-reminder.feature */
    fun sendHikeReminder(query: SendHikeReminderQuery): Unit
}
