# xTheShouter Community Run Bot

Welcome to the xTheShouter Community Run Bot! This Discord bot helps manage community runs by allowing users to register, view registrations, and download the registration data as a CSV file. The bot also includes an admin-only feature to open and close registrations.

## Features

- **Register for a Community Run**: Users can register by selecting their character class, level, and other details.
- **View Registrations**: Admins can view all current registrations.
- **Download Registrations**: Admins can download the current registrations as a CSV file.
- **Open/Close Registrations**: Admins can open or close the registration period. When the registration is closed, all data is cleared, and a CSV file is generated for download.

## Installation

To run this bot, you need to have Python installed along with the necessary dependencies.

1. **Clone the Repository**
   git clone https://github.com/Hadizih/xTSGroupMe
   cd xTheShouter-Community-Run-Bot
   
2. **Create a Virtual Environment**
  python -m venv venv
  source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. **Install Dependencies**
  pip install -r requirements.txt
  Set Up Environment Variables

4. **Create a .env file in the root directory of the project and add your Discord bot token**
  DC_BOT_TOKEN=your_discord_bot_token_here

5. **Run the Bot**
  python bot.py

## Usage
### Commands
  /anmelden: Register for the community run.
  /abmelden: Unregister from the community run.
  /open_registration: (Admin) Open the registration period.
  /close_registration: (Admin) Close the registration period and export data.
  /show_registrations: (Admin) View all current registrations.
  /save_ragistrations: (Admin) Download the current registrations as a CSV file.

After running the bot, users in your Discord server can use the commands listed above to interact with the bot.

### Contributing
If you'd like to contribute to this project, feel free to fork the repository and submit a pull request. Please make sure to follow the code style and contribute to existing issues if possible.

### License
This project is licensed under the MIT License - see the LICENSE file for details.

### Acknowledgements
discord.py - The library used to interact with the Discord API.
Any other resources or tools you used in your project.

### How to Customize:








