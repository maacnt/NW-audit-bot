from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import requests
import json
import disnake
import traceback
from disnake.ext import commands

print("main rhein bot version")

intents = disnake.Intents.all()

command_sync_flags = commands.CommandSyncFlags.default()
command_sync_flags.sync_commands_debug = False
bot = commands.Bot(
    command_prefix='>', 
    intents=intents,
    command_sync_flags=command_sync_flags
                   )
bot.remove_command("help")

#opens files

def refresh_whitelisted_users():
    with open('./usersid.json', 'r') as f:
        data = json.load(f)
    highrank_users = data['highrank_users']
    whitelisted_users = data['whitelisted_users']
    return whitelisted_users, highrank_users

os.chdir(os.path.dirname(os.path.abspath(__file__)))

token = open("./token.json", "r")
whitelisted_users_file = open("./usersid.json", "r")


#settings and service account token

credentials = service_account.Credentials.from_service_account_file('./excelapi-388705-bb8fd497f3d5.json')
service = build('sheets', 'v4', credentials=credentials)

spreadsheet_id = 'put id here'
spreadsheet_name = 'put spreadsheet name here'
sheet_gid = "put sheet gid" #CAN'T BE 0 OR NONE

search_row_username = "row for usernames"
search_row_rank = "row for ranks"
search_row_attended = "row for numbers"

search_range_start = 15
search_range_end = 330


#checks and stuff


# Custom check to verify if the user is allowed to interact with the bot
async def check_if_user_is_whitelisted(ctx):
    whitelisted_users = refresh_whitelisted_users()[0]
    if ctx.author.id in whitelisted_users:
        return True
    else:
        embed = disnake.Embed(title="Non-authorized user", description="You are not permitted to use this command", color=0x780000)
        embed.set_author(name="ERROR 99")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/697168778844176466/1131618178196328638/f7a110f49ce179e263d5d0f13674b548.png?width=676&height=676")
        embed.add_field(name="To get whitelisted, contact Maciek, username: macnt", value="", inline=True)
        embed.set_footer(text="by Maciek (macnt)")
        await ctx.send(embed=embed)
        return False
    
async def highrank(ctx):
    highrank_users = refresh_whitelisted_users()[1]
    if ctx.author.id in highrank_users:
        return True
    else:
        embed = disnake.Embed(title="Non-high rank user", description="You are not permitted to use this command", color=0x780000)
        embed.set_author(name="ERROR 98")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/697168778844176466/1131618178196328638/f7a110f49ce179e263d5d0f13674b548.png?width=676&height=676")
        embed.add_field(name="Only the Developer has access to this command", value="", inline=True)
        embed.set_footer(text="by Maciek (macnt)")
        await ctx.send(embed=embed)
        return False
        

        
def returnerror(error):
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(error)
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!")

#conditions to crash/output an error (funny)
conditions = { 
    search_range_start <= 0 or search_range_end <= 0: "Search range start or end is less than 0",
    search_range_start > search_range_end: "Search range start is greater than search range end",
    sheet_gid == "": "Sheet gid is empty",
    spreadsheet_id == "": "Spreadsheet id is empty",
    spreadsheet_name == "": "Spreadsheet name is empty",
    search_row_username == "": "Search row username is empty",
    search_row_rank == "": "Search row rank is empty",
    search_row_attended == "": "Search row attended is empty",
} 

for condition, error_message in conditions.items():
    if condition:
        returnerror(error_message)
        
        
#commands

#help command
@bot.slash_command(description="Shows the commands of the bot!")
async def help(inter):
    embed=disnake.Embed(title="Commands to use withn the bot", description="NOTE: you need to get whitelisted to the spreadsheet commands", color=0x000000)
    embed.set_author(name="Accessible commands")
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/697168778844176466/1131618178196328638/f7a110f49ce179e263d5d0f13674b548.png?width=676&height=676")
    embed.add_field(name="Utility commands ", value="```cpp\n#ping\n#hello\n#what_rank_am_i```", inline=True)
    embed.add_field(name="Spreadsheet commands ", value="```cpp\nfetch(audit log)\n#run\n#auditclear\n#print_value\n#show_settings```", inline=True)
    embed.add_field(name="Developer Commands ", value="```cpp\nwhitelist_user(user id)\nunwhitelist_user(user id)\n#show_whitelisted_users\nchange_setting(variable, value)```", inline=True)
    embed.set_footer(text="by Maciek (macnt)")
    await inter.send(embed=embed)
    
@bot.slash_command(description="Whitelists user with the given id")
@commands.check(highrank)
async def whitelist_user(inter, user_id: str):
    try:
        user_id = int(user_id)
    except ValueError:
        await inter.send("Invalid user ID. Please provide a valid user ID.")
        return
    
    # Load the current whitelisted users
    with open('usersid.json', 'r') as f:
        data = json.load(f)
    whitelisted_users = data['whitelisted_users']

    # Add the new user ID
    whitelisted_users.append(user_id)

    # Save the updated list back to the file
    data['whitelisted_users'] = whitelisted_users
    with open('usersid.json', 'w') as f:
        json.dump(data, f)

    await inter.send(f"User {user_id} has been whitelisted.")
    
@bot.slash_command(description="Unwhitelists user with the given id")
@commands.check(highrank)
async def unwhitelist_user(inter, user_id: str):
    try:
        user_id = int(user_id)
    except ValueError:
        await inter.send("Invalid user ID. Please provide a valid user ID.")
        return
    
    # Load the current whitelisted users
    with open('usersid.json', 'r') as f:
        data = json.load(f)
    whitelisted_users = data['whitelisted_users']

    # Remove the user ID
    whitelisted_users.remove(user_id)

    # Save the updated list back to the file
    data['whitelisted_users'] = whitelisted_users
    with open('usersid.json', 'w') as f:
        json.dump(data, f)

    await inter.send(f"User {user_id} has been unwhitelisted.")
    
    
@bot.slash_command(description="Shows the whitelisted users")
@commands.check(highrank)
async def show_whitelisted_users(inter):
    # Load the current whitelisted users
    with open('usersid.json', 'r') as f:
        data = json.load(f)
    whitelisted_users = data['whitelisted_users']

    # Send the list of whitelisted users
    await inter.send(f"Whitelisted users: {whitelisted_users}")


@bot.slash_command(description="Test command")
@commands.check(check_if_user_is_whitelisted)
async def test(inter):
    await inter.send("test")

@bot.slash_command(description="Shows ping of the bot")
async def ping(inter):
    await inter.send(f"Pong! {round(bot.latency * 1000)}ms")

@bot.slash_command(description="Responds with 'World'")
async def hello(inter):
    await inter.response.send_message("World")

@bot.slash_command(description="Paste the audit log here")
@commands.check(check_if_user_is_whitelisted)
async def fetch(inter, data: str):
    
    data = data.split()  # Split the data into individual words
    global given_values
    given_values = [data[i:i+2] for i in range(0, len(data), 2)]  # Group the words into pairs
    if len(given_values) > 1900:
        embed = disnake.Embed(title="Audit log too large", description="Audit log invalid! Please make sure that the audit log is correct\n\nPlease paste the audit log in smaller chunks", color=0x780000)
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/697168778844176466/1131618178196328638/f7a110f49ce179e263d5d0f13674b548.png?width=676&height=676")
        embed.set_author(name="Error 102")
        await inter.send(embed=embed)
        return
    
    # Roles to exclude
    excluded_roles = ["Sergeant", "Oberlieutenant", "Unterlieutenant", "Major", "Brigade-General", "Hauptmann", "Feldwebel", "Adjutant", "Oberst", "Fürstprimas", "Division-General", "Oberstlieutenant"]
    
    #check roles for audit errors
    all_roles = ["Landwehr","Soldat","Gefreiter","Obergefreiter","Korporal","Koporal","Sergeant", "Oberlieutenant", "Unterlieutenant", "Major", "Brigade-General", "Hauptmann", "Feldwebel", "Adjutant", "Oberst", "Fürstprimas"]
    
    # Remove entries with excluded roles from the given_values array
    given_values = [entry for entry in given_values if entry[1] not in excluded_roles]
    
    # Update "Koporal" rank to "Korporal Fourrier"
    for entry in given_values:
        if entry[1] == "Koporal":
            entry[1] = "Korporal Fourrier"
    
    # Output an error when a name is a rank (to prevent fuck-ups)
    for entry in given_values:
        if entry[0] in all_roles:
            embed = disnake.Embed(title="Invalid Role", description=f"Audit log invalid! Please make sure that the audit log is correct\n\nInvalid role detected: {entry[0]} in {entry[1]}", color=0x780000)
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/697168778844176466/1131618178196328638/f7a110f49ce179e263d5d0f13674b548.png?width=676&height=676")
            embed.set_author(name="Error 103")
            embed.set_footer(text="by Maciek (macnt)")
            await inter.send(embed=embed)
            return  # Exit the command if an invalid role is found
        
    #check if even amount of entries
    for line in given_values:
        if len(line) % 2 != 0:
            embed = disnake.Embed(title="Uneven amount of information", description="Audit log invalid! Please make sure that the audit log is correct\n\nSomeone might be missing a rank or there might be a missing username", color=0x780000)
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/697168778844176466/1131618178196328638/f7a110f49ce179e263d5d0f13674b548.png?width=676&height=676")
            embed.set_author(name="Error 104")
            await inter.send(embed=embed)
            return  # Exit the command if uneven data is found

    count_dict = {}
    for item in given_values:
        key = item[0]
        value = item[1]
        
        if key in count_dict:
            # Duplicate found, update the second value
            count_dict[key][1] = value
            count_dict[key][2] += 1
        else:
            # New entry
            count_dict[key] = [key, value, 1]
    given_values = list(count_dict.values())

    embed = disnake.Embed(title="Audit log has been saved", description="You can use the run command now", color=0x000000)
    embed.set_author(name="Information saved")
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/697168778844176466/1131618178196328638/f7a110f49ce179e263d5d0f13674b548.png?width=676&height=676")
    embed.set_footer(text="by Maciek (macnt)")
    await inter.send(embed=embed)
    


@bot.slash_command(description="clears the audit log")
@commands.check(check_if_user_is_whitelisted)
async def auditclear(inter):
    global given_values
    
    #check if audit is not clear
    if not given_values:
        await inter.send("given_values is empty!")
    
    if not given_values.clear():
        await inter.send("Audit cleared!")
    else:
        await inter.send("Failed to clear audit")
  
@bot.slash_command(description="Prints the audit log")
@commands.check(check_if_user_is_whitelisted)
async def print_value(inter):
    
    if given_values == []:
        await inter.send("given_values is empty!")
    else:
        await inter.send(given_values)

@bot.slash_command(description="Shows the bot settings")
@commands.check(check_if_user_is_whitelisted)
async def show_settings(inter):
    embed=disnake.Embed(title="Bot settings", description="Shows the current settings of the bot", color=0x000000)
    embed.set_author(name="Settings")
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/697168778844176466/1131618178196328638/f7a110f49ce179e263d5d0f13674b548.png?width=676&height=676")
    embed.add_field(name="Spreadsheet settings", value=f"Spreadsheet ID: {spreadsheet_id}\nSpreadsheet name: {spreadsheet_name}\nSheet gid: {sheet_gid}\nSearch row username: {search_row_username}\nSearch row rank: {search_row_rank}\nSearch row attended: {search_row_attended}\nSearch range start: {search_range_start}\nSearch range end: {search_range_end}", inline=True)
    embed.set_footer(text="by Maciek (macnt)")
    await inter.send(embed=embed)
    
@bot.slash_command(description="Forcefully changes a global variable within the bot (WARNING: Use with caution)")
@commands.check(highrank)
async def change_setting(inter, setting: str, value: str):
    # Check if the setting exists in the global variables
    if setting in globals():
        # Change the value of the global variable
        globals()[setting] = value
        await inter.send(f"Setting {setting} has been changed to {value}")
    else:
        await inter.send(f"Setting {setting} does not exist")
  
@bot.slash_command(description="Shows the rank of the user")
async def what_rank_am_i(inter):
    whitelisted_user = refresh_whitelisted_users()[0]
    highrank_user = refresh_whitelisted_users()[1]
    
    if inter.author.id in whitelisted_user and inter.author.id in highrank_user:
        embed=disnake.Embed(title="Shows your permission", description="May god have mercy with your soul, as the wrath of this power is something to fear", color=0x000000)
        embed.set_author(name="Whitelist Status")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/697168778844176466/1131618178196328638/f7a110f49ce179e263d5d0f13674b548.png?width=676&height=676")
        embed.add_field(name="```Whitelisted User```", value="", inline=False)
        embed.add_field(name="```Highrank user```", value="", inline=False)
        embed.set_footer(text="by Maciek (macnt)")
        await inter.send(embed=embed)
    elif inter.author.id in whitelisted_user:
        embed=disnake.Embed(title="Shows your permission")
        embed.set_author(name="Whitelist Status")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/697168778844176466/1131618178196328638/f7a110f49ce179e263d5d0f13674b548.png?width=676&height=676")
        embed.add_field(name="```Whitelisted User```", value="", inline=False)
        embed.set_footer(text="by Maciek (macnt)")
        await inter.send(embed=embed)
    elif inter.author.id in highrank_user:
        embed=disnake.Embed(title="Shows your permission")
        embed.set_author(name="Whitelist Status")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/697168778844176466/1131618178196328638/f7a110f49ce179e263d5d0f13674b548.png?width=676&height=676")
        embed.add_field(name="```Highrank user```", value="", inline=False)
        embed.set_footer(text="by Maciek (macnt)")
        await inter.send(embed=embed)
    else:
        embed=disnake.Embed(title="Shows your permission")
        embed.set_author(name="Whitelist Status")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/697168778844176466/1131618178196328638/f7a110f49ce179e263d5d0f13674b548.png?width=676&height=676")
        embed.add_field(name="```Non-Whitelisted User```", value="", inline=False)
        embed.set_footer(text="by Maciek (macnt)")
        await inter.send(embed=embed)
  
  
  
#defs for run command
def getrank(attended_times):
    try:
        if attended_times == 1:
            old_rank = "Landwehr"
        elif 2 <= attended_times <= 6:
            old_rank = "Soldat"
        elif 6 < attended_times <= 12:
            old_rank = "Gefreiter"
        elif 12 < attended_times <= 18:
            old_rank = "Obergefreiter"
        elif 18 < attended_times <= 25:
            old_rank = "Korporal"
        elif 25 <= attended_times:
            old_rank = "Korporal Fourrier"
        
        return old_rank
    except Exception as e:
        returnerror(e)

def column_to_number(column):
    index = 0
    for char in column:
        index = index * 26 + (ord(char.upper()) - ord('A')) + 1
    return index - 1

def update_cell_background_color(spreadsheet_row, search_row_username):
    
    request = {
        "updateCells": {
            "rows": [
                {
                    "values": [
                        {
                            "userEnteredFormat": {
                                "backgroundColorStyle": {
                                    "rgbColor": {
                                        "red": 1,
                                        "green": 0,
                                        "blue": 1,
                                    }
                                }
                            }
                        }
                    ]
                }
            ],
            "fields": "userEnteredFormat(backgroundColorStyle)",
            "start": {
                "sheetId": sheet_gid,
                "rowIndex": spreadsheet_row,
                "columnIndex": search_row_username,
            }
        }
    }
    try:
        service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": [request]}).execute()
    except Exception as e:
        returnerror("An error occurred while updating cell background color:", e)
        
is_running = False
        
#run command
@bot.slash_command(description="Runs the audit log")
@commands.check(check_if_user_is_whitelisted)
async def run(inter):
    global is_running
    if is_running == False:
        is_running = True
        
        embed=disnake.Embed(title="Starting", description="this might take a moment...", color=0x000000)
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/697168778844176466/1131618178196328638/f7a110f49ce179e263d5d0f13674b548.png?width=676&height=676")
        embed.set_footer(text="by Maciek (macnt)")
        await inter.send(embed=embed)
        try:
            range_name = f'{spreadsheet_name}!{search_row_username}{search_range_start}:{search_row_username}{search_range_end}' 
            result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
            values = result.get('values', []) #gets the username array



            attended_range_name = f'{spreadsheet_name}!{search_row_attended}{search_range_start}:{search_row_attended}{search_range_end}' 
            attended_number_raw = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=attended_range_name).execute()
            attended_number = attended_number_raw.get('values', []) #gets the attended array
        except Exception as e:
            returnerror(e)

        global results

        results = []
        for i, row in enumerate(values, start=search_range_start):
            results.append((i, row)) #turns this into a usable array
            raw_results = results

        attended_results = []
        for i, row in enumerate(attended_number, start=search_range_start):
            attended_results.append((i, row)) # turns this into a usable array
        
        try:
            if given_values == [] or given_values == None:
                returnerror("Audit log is empty")

            given_values_content = given_values
            audit_log_entries = len(given_values_content)
            usernames = [info[0] for info in given_values_content]
            results = [entry for entry in results if entry[1][0] in usernames] # makes the results array

            attended_rows_raw = [i[0] for i in attended_results]
            spreadsheet_rows = [i[0] for i in results]
            attended_rows = [i for i in attended_rows_raw if i in spreadsheet_rows] #makes the attended rows array

            promotion_list = []
            not_in_sheet_array = []



            for entry in range(audit_log_entries):
                ranker_information = given_values_content[entry]
                username = ranker_information[0] # gets the username
                rank = ranker_information[1] # gets the rank
                attended = ranker_information[2] # gets the attended

                for spreadsheet_entry in range(len(results)): 
                
                    results_content = results[spreadsheet_entry]  
                    spreadsheet_username = results_content[1][0] # gets the username from the spreadsheet

                    if username == spreadsheet_username: # if the username matches
                        spreadsheet_row = results[spreadsheet_entry][0]  # gets the row number

                        for i in attended_rows: # for every row in the attended rows
                        
                            if i == spreadsheet_row: # if the row matches
                                attended_times = int(attended_results[i-search_range_start][1][0]) # gets the attended times

                                #determine what rank is the ranker currently
                                old_rank = getrank(attended_times)

                                attended_times = int(attended_times) + attended # adds the attended times
                                #print(attended_times) 

                                #determine what rank is the ranker after the update
                                new_rank = getrank(attended_times)

                                #if the rank is different, add it to promotion array
                                if old_rank != new_rank:
                                    promotion_list_content = (f"{username} **{old_rank} ---> {new_rank}**")
                                    promotion_list.append(promotion_list_content)

                                    try:
                                        update_cell_background_color(spreadsheet_row-1, column_to_number(search_row_username))
                                    except Exception as e:
                                        await inter.send("An error occurred while updating the spreadsheet with error: " + str(e))
                                        returnerror(e)

                                range_name = f"{spreadsheet_name}!{search_row_attended}{i}:{search_row_attended}{i}" # gets the range
                                values = [[attended_times]] # gets the values

                                body = {'values': values}
                                try:
                                    result = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_name,valueInputOption='USER_ENTERED', body=body).execute()# updates the spreadsheet
                                except Exception as e:
                                    await inter.send("An error occurred while updating the spreadsheet with error: " + str(e))
                                    returnerror({"failed to update attendance with error: "} + e)
                                break
                        ranker = username, rank, attended
                        if ranker in results:
                            results.remove(ranker)

                        break
                else:
                
                    ranker = username, rank, attended
                    not_in_sheet_array.append(ranker) # adds the ranker to the not in sheet array

            print(not_in_sheet_array)
            
            
            raw_spreadsheet_rows = [i[0] for i in raw_results]# gets the raw spreadsheet rows
            if raw_spreadsheet_rows:  # Check if the list is not empty
                highest_row = max(raw_spreadsheet_rows)  # gets the highest row
                highest_free_row = highest_row + 1 # gets the highest free row 
            else:
                highest_row = None  # or some other value that makes sense in your context

            data = []

            for i in not_in_sheet_array:
                #print(highest_free_row)

                username = i[0] # gets the username
                rank = i[1] # gets the rank
                attended = i[2] # gets the attended

                username_range_name = f"{spreadsheet_name}!{search_row_username}{highest_free_row}:{search_row_username}{highest_free_row}" # gets the username range
                rank_range_name = f"{spreadsheet_name}!{search_row_rank}{highest_free_row}:{search_row_rank}{highest_free_row}" # gets the rank range
                attended_range_name = f"{spreadsheet_name}!{search_row_attended}{highest_free_row}:{search_row_attended}{highest_free_row}" # gets the attended range

                data.append({ # im too tired to explain this
                    "range": username_range_name,
                    "values": [[username]]
                })
                data.append({
                    "range": rank_range_name,
                    "values": [[getrank(attended)]]
                })
                data.append({
                    "range": attended_range_name,
                    "values": [[attended]]
                })

                if getrank(attended) != "Landwehr":
                    promotion_list_content = (f"{username} **Landwehr ---> {getrank(attended)}**")
                    promotion_list.append(promotion_list_content)

                    try:
                        update_cell_background_color(highest_free_row-1, column_to_number(search_row_username))
                    except Exception as e:
                        await inter.send("An error occurred while updating the spreadsheet with error: " + str(e))
                        returnerror(e)

                highest_row = highest_row + 1
                highest_free_row = highest_free_row + 1

            try: # im too tired to explain this
                result = service.spreadsheets().values().batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body={
                        "valueInputOption": "USER_ENTERED",
                        "data": data
                    }).execute()
            except Exception as e:
                await inter.send("An error occurred while updating the spreadsheet with error: " + str(e))
                returnerror("failed to add a ranker with error: " + str(e))

            if promotion_list == []:
                promotion_list.append("No promotions")

            promotion_list_message = '\n'.join(promotion_list) 
            if len(promotion_list_message) > 1018:
                embed=disnake.Embed(title="Done", description="Everyone's attended points got updated", color=0x000000)
                embed.set_thumbnail(url="https://media.discordapp.net/attachments/697168778844176466/1131618178196328638/f7a110f49ce179e263d5d0f13674b548.png?width=676&height=676")
                embed.add_field(name="Promotions", value=f"The promotion list is too long! it will be sent in a following message", inline=False)
                embed.set_footer(text="by Maciek (macnt)")
                await inter.send(embed=embed)
                await inter.send(f"```{promotion_list_message}```")
                print(promotion_list_message)
            elif len(promotion_list_message) > 1900:
                embed=disnake.Embed(title="Done", description="Everyone's attended points got updated", color=0x000000)
                embed.set_thumbnail(url="https://media.discordapp.net/attachments/697168778844176466/1131618178196328638/f7a110f49ce179e263d5d0f13674b548.png?width=676&height=676")
                embed.add_field(name="Promotions", value=f"The promotion list is too long to send in a discord message, contant the developer to get the promotion list", inline=False)
                embed.set_footer(text="by Maciek (macnt)")
                await inter.send(embed=embed)
                print(promotion_list_message)
            else:
                embed=disnake.Embed(title="Done", description="Everyone's attended points got updated", color=0x000000)
                embed.set_thumbnail(url="https://media.discordapp.net/attachments/697168778844176466/1131618178196328638/f7a110f49ce179e263d5d0f13674b548.png?width=676&height=676")
                embed.add_field(name="Promotions", value=f"```{promotion_list_message}```", inline=False)
                embed.set_footer(text="by Maciek (macnt)")
                await inter.send(embed=embed)

            if highest_free_row > search_range_end: # im too tired to explain this
                embed = disnake.Embed(title="Command error", description="There was an error in the command you provided", color=0x780000)
                embed.set_author(name="ERROR 105")
                embed.set_thumbnail(url="https://media.discordapp.net/attachments/697168778844176466/1131618178196328638/f7a110f49ce179e263d5d0f13674b548.png?width=676&height=676")
                embed.add_field(name="The search range end is too low, please contact the developer to change it before proceeding", value="", inline=True)
                embed.set_footer(text="by Maciek (macnt)")
                await inter.send(embed=embed) 
                returnerror("The spreadsheet/search_range is too short, please clear it.")
            
            is_running = False
        except Exception as e:
            error_message = str(e) + "\n" + traceback.format_exc()
            await inter.send("An error occurred while running the run command: \n" + error_message)
            if error_message == "list index out of range":
                await inter.send("The audit log is empty, please paste the audit log and try again")
            if len(error_message) > 1900:
                await inter.send("Please check the terminal for more information.")
            returnerror(error_message)
            
    if is_running == True:
        embed = disnake.Embed(title="Command error", description="There was an error in the command you provided", color=0x780000)
        embed.set_author(name="ERROR 100")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/697168778844176466/1131618178196328638/f7a110f49ce179e263d5d0f13674b548.png?width=676&height=676")
        embed.add_field(name="The run command is already running, please wait", value="", inline=True)
        embed.set_footer(text="by Maciek (macnt)")
        await inter.send(embed=embed)

bot.run(token.read())
