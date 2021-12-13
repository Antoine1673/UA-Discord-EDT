from datetime import datetime
from dateutil.tz.tz import tzutc
import discord
from discord.ext import commands
from dateutil.relativedelta import relativedelta
from datetimerange import DateTimeRange
import icalevents.icalevents, icalevents.icalparser
import typing
import os
from dotenv import load_dotenv
import requests
import logging
import textEN as text
import json

IcsFileName = "./UA.ICS"
IcsUrl = "http://edt.univ-angers.fr/edt/ics?id=g9F8A5BD6AF4588EDE0530100007FD17D"
IcsCache = []
GroupsFileName = "./GlobalGroups.json"
LastUpdateFileName = "./LastUpdate.txt"

DescReplaceList = {
    "Qualité, Innovation, Fiabilité": "Qualité Innovation Fiabilité",
    "Spécialité Bâtiment : Exploitation, Maintenance et Sécurité": "Spécialité Bâtiment Exploitation Maintenance et Sécurité",
    "ZM2IS1 - M2 Ingénierie des systèmes complexes-Parcours International Ingénierie des Systèmes et Management de Projets": "ZM2IS1 - M2 Ingénierie des systèmes complexes-Parcours International"
}

def getEventGroups(event: icalevents.icalparser.Event) -> typing.List[str]:
    """Returns a list of all groups mentioned in an event."""
    eventDescElements = event.description.split("\n")
    for element in eventDescElements:
        if "Groupe :" in element:
            for oldStr, newStr in DescReplaceList.items():
                if oldStr in element:
                    element = element.replace(oldStr, newStr)
                    event.description.replace(oldStr, newStr)
            eventGroups = element.split(" : ")[1].split(", ")
            return eventGroups

def downloadICS(IcsFileName: str, IcsUrl: str) -> int:
    """Downloads an updated version of an ICS file.
    Returns HTTP code on download error (i.e. HTTP 404), 0 otherwise."""
    global IcsCache
    logging.info("Downloading ICS file...")
    response = requests.get(url=IcsUrl)
    if response.status_code == requests.codes.ok:
        with open(IcsFileName, "wb") as IcsFile:
            IcsFile.write(response.content)
        with open(LastUpdateFileName, "w") as LastUpdateFile:
            LastUpdateFile.write(datetime.isoformat(datetime.now()))
        IcsCache = []
        logging.debug("File download successful")
        return 0
    else:
        logging.error(text.downloadError.format(response.status_code))
        return response.status_code

def cacheIcs() -> None:
    """Load the downloaded ICS file into the global var IcsCache"""
    global IcsCache
    if IcsCache == []:
        IcsCache = icalevents.icalevents.events(file=IcsFileName)

def getIcsGroups(IcsFileName: str) -> typing.List[str]:
    """Fetch all groups from an ICS file."""
    global IcsCache
    logging.info("Scanning whole ICS for groups...")
    with open(IcsFileName, "rt") as IcsFile:
        cacheIcs()
        ics = IcsCache
        groups = []
        for event in ics:
            eventGroups = getEventGroups(event)
            for group in eventGroups:
                group = group.strip()
                if group not in groups:
                    groups.append(group)
    logging.info(f"Found {len(groups)} groups: ")
    logging.info(str(groups))
    return groups

async def verifyRoles(guilds: typing.List[discord.guild.Guild], GroupsFileName: str, channel: discord.TextChannel = None):
    with open(GroupsFileName, "r") as GroupsFile:
        groups = json.load(GroupsFile)
        for guild in guilds:
            for group in groups:
                if group not in [role.name for role in guild.roles]:
                    logging.warning(f"The role \"{group}\" does not exist but is present in the ICS file. It will be created automatically if possible.")
                    try:
                        await guild.create_role(name=group, mentionable=True)
                        if channel is not  None:
                            await channel.send(text.roleCreatedInfo.format(group))
                        logging.info(f"Created role \"{group}\"")
                    except discord.errors.Forbidden:
                        if channel is not  None:
                            await channel.send(text.manageRolesPermError.format(group))
                        logging.error(f"\"Manage roles\" permission missing. The role \"{group}\" could not be created.")

async def refreshRoutine(guilds: typing.List[discord.Guild], channel: discord.ChannelType = None):
    returnVal = downloadICS(IcsFileName, IcsUrl)
    if returnVal != 0:
        if channel is not None:
            await channel.send(text.refreshError)
            return
    with open(GroupsFileName, "w") as GroupsFile:
        json.dump(getIcsGroups(IcsFileName), GroupsFile, indent=4)
    await verifyRoles(guilds, GroupsFileName, channel)
    if channel is not None:
        await channel.send(text.refreshSuccess)

def main():
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    bot = commands.Bot(command_prefix="/")
    logging.basicConfig(filename="UA-Discord-EDT.log", level=logging.INFO)

    @bot.event
    async def on_ready():
        logging.info(f"{bot.user}: Connection established.")

    @bot.command(name=text.refreshCommandName)
    async def refreshCommand(ctx: commands.Context):
        """Refresh the timetable, and create new roles if necessary"""
        async with ctx.typing():
            await refreshRoutine(bot.guilds, ctx.channel)
    
    @bot.command(name=text.requestCommandName, help=text.requestCommandHelp)
    async def requestCommand(
        ctx: commands.Context,
        time: typing.Union[str, int, None] = text.relativeDays[0],
        *groups: typing.Union[str, None]
    ):
        """Request all events happening in the given time period for the given groups.
        Defaults to the rest of the day and for all the groups the user belongs to."""
        async with ctx.typing():
            logging.info(f"Request command: time={time}, groups={groups}.")

            # calculation of begin and end from the time parameters
            requestTimeRange = DateTimeRange()
            if time in text.relativeDays:
                requestTimeRange.set_start_datetime(datetime.now(tz=tzutc()) + relativedelta(days=+text.relativeDays.index(time), hour=0))
                requestTimeRange.set_end_datetime(requestTimeRange.start_datetime + relativedelta(hour=23))
            elif time in text.weekDays.keys():
                requestTimeRange.set_start_datetime(datetime.now(tz=tzutc()) + relativedelta(days=+1, weekday=text.weekDays[time], hour=0))
                requestTimeRange.set_end_datetime(requestTimeRange.start_datetime + relativedelta(hour=23))
            elif time == text.now:  
                requestTimeRange.set_start_datetime(datetime.now(tz=tzutc()))
                requestTimeRange.set_end_datetime(requestTimeRange.start_datetime + relativedelta(minutes=15))
            else:
                try:
                    time = int(time)
                    if time < 0 or time > 40:
                        raise ValueError
                except ValueError:
                    await ctx.send(text.argumentError.format("time", time))
                    logging.info(f"incorrect input for \"time\" parameter: \"{time}\".")
                    return
                requestTimeRange.set_start_datetime(datetime.now(tz=tzutc()))
                requestTimeRange.set_end_datetime(requestTimeRange.start_datetime + relativedelta(hours=time))
            logging.debug("Done calculating begin and end datetimes of timetable.")

            # cleaning of the group parameters
            with open(GroupsFileName, "r") as GroupsFile:
                globalGroupsList = json.load(GroupsFile)
                if groups is None or len(groups) == 0:
                    # if no group parameter is given
                    groupParamGiven = False
                    groups = []
                    for role in ctx.author.roles:
                        if role.name in globalGroupsList:
                            groups.append(role.name)
                else:
                    # if a group parameter is given
                    groupParamGiven = True
                    groups = list(groups)
                    groups = " ".join(groups)
                    groups = groups.split(", ")
                    for group in groups.copy():
                        if group not in globalGroupsList:
                            await ctx.send(text.argumentError.format("group", group))
                            logging.info(f"incorrect input for \"group\" parameter: \"{group}\".")
                            groups.remove(group)
                            if len(groups) == 0:
                                logging.info("No group left in group list.")
                                return
            logging.debug("Done treating the groups.")
            #TODO: implement "exclusive" groups (i.e. for GES)

            # creation, filtering and sorting of the event list
            cacheIcs()
            events = IcsCache
            for event in events.copy():
                eventTimeRange = DateTimeRange(start_datetime=event.start.replace(tzinfo=tzutc()), end_datetime=event.end.replace(tzinfo=tzutc()))
                if not eventTimeRange.is_intersection(requestTimeRange):
                    events.remove(event)
                    continue
                eventGroups = getEventGroups(event)
                if not any([group in eventGroups for group in groups]):
                    events.remove(event)
            events.sort(key=lambda event: event.start.timestamp())

            # Discord embed assembling
            embed = discord.Embed()
            if not groupParamGiven:
                embed.title = text.timetableEmbedTitleUser.format(ctx.author.name)
            else:
                embed.title = text.timetableEmbedTitleGroups.format(", ".join(groups))
            with open(LastUpdateFileName, "r") as LastUpdateFile:
                lastUpdate = datetime.fromisoformat(LastUpdateFile.readline())
                embed.set_footer(text=f"""\
                    {text.timetableEmbedUpdate} {lastUpdate.strftime("%a %d/%m %Hh%M")}\n{text.timetableEmbedGroups} {", ".join(groups)}""")
            for index, event in enumerate(events):
                category = room = subject = teacher = text.noDataError
                details = ""
                eventDescElements = event.description.split("\n")
                for element in eventDescElements:
                    if "Catégorie :" in element:
                        category = element.split(" : ")[1]
                    elif "Salle :" in element:
                        room = element.split(" : ")[1]
                    elif "Matière :" in element:
                        subject = element.split(" : ")[1]
                    elif "Personnel :" in element:
                        teacher = element.split(" : ")[1]
                    elif "Remarques :" in element:
                        details = element.split(" : ")[1]
                    elif "Groupe :" in element:
                        pass
                    else:
                        logging.info(f"Unknown field in event description: \"{element}\"")
                    embedFieldValue = f"""\
                        {event.start.strftime("%Hh%M")} - {event.end.strftime("%Hh%M")}
                        {text.timetableEmbedRoom} {room}\n\
                        {text.timetableEmbedTeacher} {teacher}"""
                    if details != "":
                        embedFieldValue += f"\n{text.timetableEmbedDetails} {details}"
                embed.add_field(
                    name=f"{category} - {subject}",
                    value=embedFieldValue,
                    inline=False
                )
                if index > 0:
                    timeRangeCurrentEvent = DateTimeRange(event.start, event.end)
                    timeRangeLastEvent = DateTimeRange(events[index - 1].start, events[index - 1].end)
                    if timeRangeCurrentEvent.is_intersection(timeRangeLastEvent):
                        embed.set_field_at(index=index - 1, inline=True, name=embed.fields[index].name, value=embed.fields[index].value)
                        embed.set_field_at(index=index, inline=True, name=embed.fields[index].name, value=embed.fields[index].value)
                   #TODO: find a way to manage inline tag to better represent overlapping events
            await ctx.send(embed=embed)
            logging.info(f"send timetable for groups: {groups} between {requestTimeRange.get_start_time_str()} and {requestTimeRange.get_end_time_str()}")
    bot.run(TOKEN)

if __name__ == '__main__':
    main()