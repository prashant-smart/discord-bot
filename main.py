import discord
import asyncio
import re
import yt_dlp as youtube_dl

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)

# Global variables for music player
voice_clients = {}
song_queue = []

yt_dl_opts = {'format': 'bestaudio/best'}
ytdl = youtube_dl.YoutubeDL(yt_dl_opts)

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',  # Add reconnect options
    'options': '-vn',
}


# Dictionary to store greeting channels for each guild
greeting_channels = {}

@client.event
async def on_ready():
    print("The bot is ready!")
    print("-----------------")

@client.event
async def on_message(message):
    global voice_channel
    global voice_client
    global is_playing
    global voice_clients
    global song_queue

    if message.author == client.user:
        return

    user_message = str(message.content)

    if user_message.startswith('!hello'):
        greeting = f"👋🏽 Hello {message.author.mention}! 😊 How are you today?"
        await message.channel.send(greeting)

    elif user_message.startswith('!ban'):
        mention = message.mentions[0] if message.mentions else None
        if message.author.guild_permissions.kick_members:
            if mention:
                await message.guild.ban(mention)
                await message.channel.send(f"👋🏽 {mention.display_name} has been banned. Say goodbye! 👋🏽")
            else:
                await message.channel.send("Please mention the user you want to ban.")
        else:
             await message.channel.send(f"You dont have permission to ban **{mention.display_name}**.")

    elif user_message.startswith('!kick'):
        mention = message.mentions[0] if message.mentions else None
        if message.author.guild_permissions.kick_members:
            if mention:
                await message.guild.kick(mention)
                await message.channel.send(f"👢 {mention.display_name} has been kicked. Out you go! 👋🏽")
            else:
                await message.channel.send("Please mention the user you want to kick.")
        else:
            await message.channel.send(f"You dont have permission to kick **{mention.display_name}**.")

    elif user_message.startswith('!broadcast'):
        # Check if the message is sent in a direct message (DM) channel
        if isinstance(message.channel, discord.DMChannel):
            # Extract server name, message, and delay from the command
            server_name = None
            message_content = None
            delay_str = None

            server_parts = re.search(r'server\s*:\s*"([^"]*)"', user_message)
            if server_parts:
                server_name = server_parts.group(1).strip()

            message_parts = re.search(r'message\s*:\s*"([^"]*)"', user_message)
            if message_parts:
                message_content = message_parts.group(1).strip()

            delay_parts = re.search(r'delay\s*:\s*"([^"]*)"', user_message)
            if delay_parts:
                delay_str = delay_parts.group(1).strip()
            try:
                if message_content == None or server_name == None:
                    raise Exception()
                # Check if the bot is a member of the specified server
                target_server = discord.utils.get(client.guilds, name=server_name)
                if target_server:
                    # Fetch all members in the server
                    async for member in target_server.fetch_members(limit=None):
                        pass  # Iterating to force the fetching of members
                    # Check if the user has the 'use_bot' role
                    use_bot_role = discord.utils.get(target_server.roles, name="use_bot")
                    member = target_server.get_member(
                        message.author.id) or await target_server.fetch_member(message.author.id)
                    if use_bot_role and member and use_bot_role in member.roles:
                        # Send the broadcast message to all members of the specified server
                        loading_msg = await message.channel.send("📡 Broadcasting...")

                        if delay_str:
                            # Schedule the broadcast with a delay
                            try:
                                parts = delay_str.split(":")
                                if len(parts) == 3:
                                    days, hours, seconds = map(int, parts)
                                    total_seconds = (
                                        days * 24 * 60 * 60) + (hours * 60 * 60) + seconds

                                    if total_seconds >= 0:  # Allow a delay of 0 seconds
                                        await asyncio.sleep(total_seconds)
                                    else:
                                        raise ValueError(
                                            "Delay must be a non-negative integer.")
                                else:
                                    raise ValueError(
                                        "**Invalid delay format**. Use DD:HH:SS (ex: 00:02:00 for 2 Min).")
                            except ValueError:
                                await loading_msg.edit(
                                    content="❌ **Invalid delay format**.\n Use !broadcast \nserver:\"server_name\", \nmessage:\"your_message\", \ndelay: \"DD:HH:SS\" (ex: 00:02:00 for **2 Min**).")
                                return

                        for member in target_server.members:
                            # Exclude the bot itself and the user who triggered the command
                            if member.bot or member == message.author:
                                continue
                            try:
                                await member.send(f"**Broadcast from {target_server.name}:**\n {message_content}")
                            except discord.Forbidden:
                                # Ignore members who have DMs disabled or blocked the bot
                                pass

                        if delay_str != None:
                            await loading_msg.edit(content=f"✅ Scheduled Broadcast has been sent to all members of **{target_server.name}**\n\n **Delayed Time**: {delay_str} (DD:HH:SS Format) \n\n **Message** : {message_content}.")
                        else:
                            await loading_msg.edit(content=f"✅ Broadcast sent to all members of **{target_server.name}**\n\n **Message** : {message_content}.")
                    else:
                        await loading_msg.edit(content="❌ You do not have the 'use_bot' role to use this command.")
                else:
                    await loading_msg.edit(content=f"❌ The bot is not a member of the specified server: **{server_name}**.")
            except:
                await message.channel.send("❌ **Invalid command format**.\n\n For **message without delay** Use !broadcast \nserver:\"server_name\", \nmessage:\"your_message\",  \n\n For **message with delay** Use !broadcast \nserver:\"server_name\", \nmessage:\"your_message\", \ndelay: \"DD:HH:SS\" (ex: 00:02:00 for **2 Min**).")
        else:
            await message.channel.send("❌ The !broadcast command can only be used in direct messages (DMs) with the bot.")
    elif user_message.startswith('!setgreetingchannels'):
        if message.author.guild_permissions.administrator:
            if discord.utils.get(message.author.roles, name="use_bot"):
                await set_greeting_channels(message)
            else:
                await message.channel.send("❌ You do not have the 'use_bot' role to use this command.")
        else:
            await message.channel.send("❌ You do not have necessary permission to remove Greeting Channels.")
    elif message.content.startswith('!removegreetingchannel'):
        if message.author.guild_permissions.administrator:
            if discord.utils.get(message.author.roles, name="use_bot"):
                await remove_greeting_channel(message)
            else:
                await message.channel.send("❌ You do not have the 'use_bot' role to use this command.")
        else:
            await message.channel.send("❌ You do not have necessary permission to remove Greeting Channels.")
        
    elif user_message.startswith('!help'):
        help_message = (
            "🤖 **Available Commands:**\n"
            "!hello - Greet the bot\n"
            "!help - Display this help message\n"
            "!ban @user - Ban a user (requires 'ban_members' permission)\n"
            "!kick @user - Kick a user (requires 'kick_members' permission)\n"
            "!broadcast - Send a broadcast message to a server\n\n"
            "   **Format without delay:** \n`!broadcast server:\"server_name\", \nmessage:\"your_message\"`\n\n"
            "   **Format with delay:** \n`!broadcast server:\"server_name\", \nmessage:\"your_message\",\ndelay:\"DD:HH:SS\"`\n\n"
            "   **Note**: To use !broadcast, you need the '**use_bot**' role in the specified server. \n\n"
            "🎤 **Music Commands:**\n"
            "!play song_name - Play a song by name\n"
            "!pause - Pause the currently playing song\n"
            "!resume - Resume the paused song\n"
            "!stop - Stop the current song and leave the voice channel\n\n"
            "**👋 Greeting Commands:**\n"
            "!setgreetingchannels channels:\"channel_id_1, channel_id_2, ...\" - Set greeting channels for new member greetings\n"
            "!removegreetingchannel channels:\"channel_id_1, channel_id_2, ...\" - Remove greeting channels\n"
            "**Note**: To use !removegreetingchannel and !setgreetingchannels , you need the '**use_bot**' role in this server. \n\n"
        )
        await message.channel.send(help_message)

    elif user_message.startswith('!play'):
        try:
            # Check if the bot is in a voice channel
            if message.author.voice and message.author.voice.channel:
                # Connect to the voice channel
                voice_channel = message.author.voice.channel
                if voice_channel.guild.id not in voice_clients:
                    voice_client = await voice_channel.connect()
                    voice_clients[voice_channel.guild.id] = voice_client

                query = user_message.split(' ', 1)[1]
                await play_song(message.guild.id, query, message)
            else:
                await message.channel.send("❌ You need to be in a voice channel to use this command!")
        except Exception as e:
            print(e)
            await message.channel.send("❌ An error occurred while processing the command.")

    elif user_message.startswith('!pause'):
        await pause_song(message.guild.id, message.channel)

    elif user_message.startswith('!resume'):
        await resume_song(message.guild.id, message.channel)

    elif user_message.startswith('!stop'):
        await stop_song(message.guild.id, message.channel)
    

async def play_song(guild_id, query, message):
    try:
        loop = asyncio.get_event_loop()

        # Use youtube_dl to search for the video
        search_url = f"ytsearch:{query}"
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(search_url, download=False))

        # Check if search results are available
        if 'entries' in data and data['entries']:
            # Get the first result
            first_result = data['entries'][0]
            song_url = first_result['url']

            # Create audio player
            player = discord.FFmpegPCMAudio(song_url, **ffmpeg_options)

            # Check if there is already a voice client for the guild
            if guild_id in voice_clients:
                voice_client = voice_clients[guild_id]
            else:
                # If not, create a new voice client
                voice_client = await voice_channel.connect()
                voice_clients[guild_id] = voice_client

            # Stop the current song if playing
            if voice_client.is_playing():
                voice_client.stop()

            # Play the new song
            voice_client.play(player)

            # Send a message to the text channel with song details
            song_details = f"🎶 Now playing: **{first_result['title']}**"
            await voice_channel.send(song_details)
            await message.channel.send(song_details)

        else:
            await voice_channel.send("❌ No search results found. Unable to play the requested song.")
            
    except Exception as e:
        print(e)
        await voice_channel.send("❌ An error occurred while trying to play the song.")

async def pause_song(guild_id, text_channel):
    try:
        if guild_id in voice_clients:
            voice_client = voice_clients[guild_id]
            voice_client.pause()
        else:
            await text_channel.send("❌ Bot is not currently playing any music.")
    except Exception as e:
        print(e)

async def resume_song(guild_id, text_channel):
    try:
        if guild_id in voice_clients:
            voice_client = voice_clients[guild_id]
            voice_client.resume()
        else:
            await text_channel.send("❌ Bot is not currently playing any music.")
    except Exception as e:
        print(e)

async def stop_song(guild_id, text_channel):
    try:
        if guild_id in voice_clients:
            voice_client = voice_clients[guild_id]
            voice_client.stop()
            await voice_client.disconnect()
            del voice_clients[guild_id]
        else:
            await text_channel.send("❌ Bot is not currently playing any music.")
    except Exception as e:
        print(e)

@client.event
async def on_member_join(member):
    # Greet the member in specified channels
    guild_id = member.guild.id
    channels = greeting_channels.get(guild_id, [])
    
    greeting_message = f"👋🏽 Welcome {member.mention} to the server! 🎉"
    
    tasks = [greet_member_in_channel(channel, greeting_message) for channel in channels]
    await asyncio.gather(*tasks)



async def greet_member_in_channel(channel_id, greeting_message):
    channel = client.get_channel(channel_id)
    if channel:
        # Send the greeting message in text form
        greeting = await channel.send(greeting_message)
        # Delete the greeting message after 5 seconds
        await asyncio.sleep(5)
        await greeting.delete()

async def set_greeting_channels(message):
    try:
        # Extract channels from the command
        channels_str = re.search(r'channels\s*:\s*"([^"]*)"', message.content)
        if not channels_str:
            raise Exception()

        new_channels = [int(channel_id) for channel_id in channels_str.group(1).split(",")]

        # Update greeting channels for the guild
        guild_id = message.guild.id
        existing_channels = greeting_channels.get(guild_id, [])
        
        added_channels = list(set(new_channels) - set(existing_channels))
        already_present_channels = list(set(new_channels).intersection(existing_channels))
        
        greeting_channels[guild_id] = existing_channels + added_channels

        response = []
        if added_channels:
            response.append(f"Added greeting channels: {added_channels}")
        if already_present_channels:
            response.append(f"Already present greeting channels: {already_present_channels}")

        await message.channel.send("\n".join(response))
    except:
        await message.channel.send("**Invalid command format**. Use !setgreetingchannels channels:\"channel_id_1, channel_id_2, ...\"")

async def remove_greeting_channel(message):
    try:
        # Extract channel IDs from the command
        channel_ids_str = re.search(r'channels?\s*:\s*"([^"]*)"', message.content)
        if not channel_ids_str:
            raise Exception()

        channel_ids = [int(channel_id) for channel_id in channel_ids_str.group(1).split(",")]

        # Initialize response lists
        removed_channels = []
        not_present_channels = []

        # Remove channels from greeting channels for the guild
        guild_id = message.guild.id
        if guild_id in greeting_channels:
            for channel_id in channel_ids:
                if channel_id in greeting_channels[guild_id]:
                    greeting_channels[guild_id].remove(channel_id)
                    removed_channels.append(channel_id)
                else:
                    not_present_channels.append(channel_id)
        else:
            not_present_channels = channel_ids

        # Build and send response
        response = []
        if removed_channels:
            response.append(f"Removed greeting channels: {removed_channels}")
        if not_present_channels:
            response.append(f"Ids which are either Invalid or Not present in greeting channels list: {not_present_channels}")

        await message.channel.send("\n".join(response))
    except:
        await message.channel.send("**Invalid command format**. Use !removegreetingchannel channels:\"channel_id_1, channel_id_2, ...\"")


@client.event
async def on_disconnect():
    # Handle reconnection logic here
    print("Disconnected. Reconnecting...")
    await asyncio.sleep(5)  # Wait for 5 seconds before attempting to reconnect
    await client.connect()
    await voice_channel.send("🔗 Connection to voice channel lost. Reconnecting...")
client.run('YOUR_BOT_TOKEN')
