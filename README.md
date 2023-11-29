# Discord Bot with Music and Greeting Features

Enhance your Discord server with this versatile bot that brings both music playback functionality and automated greetings for new members. The bot is built using Discord.py and includes a variety of commands for a more interactive server experience.

## Features:

### Music Commands:

- **!play song_name:** Play a song by name.
- **!pause:** Pause the currently playing song.
- **!resume:** Resume the paused song.
- **!stop:** Stop the current song and leave the voice channel.

### Greeting Channel Commands:

- **!setgreetingchannels channels:"channel_id_1, channel_id_2, ...":** Set greeting channels for new member greetings. (Requires 'use_bot' role)
- **!removegreetingchannel channels:"channel_id_1, channel_id_2, ...":** Remove greeting channels. (Requires 'use_bot' role)

### Broadcast Command:

- **!broadcast:** Send a broadcast message to a server.
  - **Format without delay:** `!broadcast server:"server_name", message:"your_message"`
  - **Format with delay:** `!broadcast server:"server_name", message:"your_message", delay:"DD:HH:SS"`

### General Commands:

- **!hello:** Greet the bot.
- **!ban @user:** Ban a user (requires 'ban_members' permission).
- **!kick @user:** Kick a user (requires 'kick_members' permission).
- **!help:** Display the help message.

## Setup:

1. Clone the repository.
2. Install the required Python packages using `pip install -r requirements.txt`.
3. Download and install [FFmpeg](https://ffmpeg.org/download.html).
4. Set up your bot token in the code.
5. Run the bot script using `python bot_script.py`.

**Note**:- You have to download FFMPEG in your system for the music feature of the bot, refer to [this tutorial](https://www.youtube.com/watch?v=IECI72XEox0).

Feel free to customize and expand upon this bot to suit the needs of your Discord server!

## Contributors:

- [Prashant Kumar Yadav]([https://github.com/prashant-smart])

## License:

This project is licensed under the [MIT License](LICENSE).
