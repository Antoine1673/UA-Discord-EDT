# UA-Discord-EDT
Discord bot providing the timetable info of Angers University in Discord through ICS calendars.

An ICS file is downloaded every hour from a given URL.
The file is then accessed through the icalevents Python module.

Two commands are implemented for now:
 * `/refresh`: force download the calender, updates the groups list and creates the corresponding roles in all Discord guilds if they are not present yet.
 * `/timetable [time] [groups]`: request a timetable:
   * By default, display all event for the rest of the day for the groups of the user who entered the command.
   * The optional arg `<time>` can either be a week day, "today" or "tomorrow", and will display all events for the according day. It can also be "now", in this case the events occurring for the next 15 minutes will be displayed.
   * The optional arg `<groups>` can be a group or a `, ` separated list of groups, and will display all events these groups attend to. If a group is not recognized, it will simply be ignored.
