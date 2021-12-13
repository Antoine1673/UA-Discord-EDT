import calendar

refreshCommandName = "refresh"
requestCommandName = "timetable"

now = "now"
relativeDays = [
    "today",
    "tomorrow"
]
weekDays = {
    "monday": calendar.MONDAY,
    "tuesday": calendar.TUESDAY,
    "wednesday": calendar.WEDNESDAY,
    "thursday": calendar.THURSDAY,
    "friday": calendar.FRIDAY,
    "saturday": calendar.SATURDAY,
    "sunday": calendar.SUNDAY
}

refreshSuccess = "The timetable was updated successfully."
timetableEmbedTitleUser = "Timetable of {}:"
timetableEmbedTitleGroups = "Timetable of group {}:"
timetableEmbedRoom = "Room:"
timetableEmbedTeacher = "Teacher:"
timetableEmbedUpdate = "Update:"
timetableEmbedGroups = "Groups:"
timetableEmbedDetails = "Details:"

roleCreatedInfo = "The role *{}* was automatically created."

downloadError = "HTTP error code {} while downloading ICS. Events not updated."
refreshError = "Error while refreshing timetable. The university's website might be broken."
manageRolesPermError = "I don't have the permission `Manage Roles`, I cannot create the role *{}* according to the timetable groups."
argumentError = "incorrect `{}` argument : \"{}\"."
noDataError = "<error>"

refreshCommandBrief = "Refresh the timetable."
requestCommandBrief = "Give all the events for the rest of your day"

refreshCommandHelp = """Force the update of the timetable, and automatically create roles for the groups that do not exist yet, if necessary.
        The timetable is automatically updated every hour, no need to spam."""
requestCommandHelp = """Request all events happening in the given time period for the given groups.
        Defaults to the rest of the day and for all the groups the user belongs to."""