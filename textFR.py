import calendar

refreshCommandName = "refresh"
requestCommandName = "edt"

now = "rn"
relativeDays = [
    "today",
    "demain"
]
weekDays = {
    "lundi": calendar.MONDAY,
    "mardi": calendar.TUESDAY,
    "mercredi": calendar.WEDNESDAY,
    "jeudi": calendar.THURSDAY,
    "vendredi": calendar.FRIDAY,
    "samedi": calendar.SATURDAY,
    "dimanche": calendar.SUNDAY
}

refreshSuccess = "Emploi du temps mis à jour."
timetableEmbedTitle = "Emploi du temps de {} :"
timetableEmbedTitleGroups = "Emploi du temps du groupe {}:"
timetableEmbedRoom = "Salle :"
timetableEmbedTeacher = "Prof :"
timetableEmbedUpdate = "Mise à jour :"
timetableEmbedGroups = "Groupes :"
timetableEmbedDetails = "Details :"

roleCreatedInfo = "Le rôle *{}* a été automatiquement créé."

downloadError = "Erreur HTTP {} pendant le téléchargement de l'emploi du temps. Planning non mis à jour."
refreshError = "Erreur pendant la mise à jour de l'emploi du temps. Le site de l'université est peut-être cassé."
manageRolesPermError = "Je n'ai pas la permission `Gérer les rôles`, imposible de créer le rôle *{}* présent dans l'emploi du temps."
argumentError = "Argument `{}` incorrect : \"{}\"."
noDataError = "<erreur>"
noEventError = "Pas d'évènements"

refreshCommandBrief = "Force la mise à jour de l'emploi du temps."
requestCommandBrief = "Renvoie tous les évènements restants dans ta journée."

refreshCommandHelp = """Force la mise à jour de l'emploi du temps, et créée automatiquement des rôles pour les groupes qui n'existent pas encore si besoin.
        L'emploi du temps se met à jour automatiquement toutes les heures, pas besoin de spammer."""
requestCommandHelp = """Renvoie tous les évènements ayant lieu dans la période donnnée pour le(s) groupe(s) donné(s).
        Par défaut, renvoie les évènements restants dans la journée pour les groupes de l'utilisateur."""