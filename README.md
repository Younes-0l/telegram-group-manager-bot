# 🤖 Telegram Group Manager Bot

A Python-based Telegram bot designed to simplify group administration, improve community security, and automate moderation tasks.

Built with the **Telegram Bot API** and **PostgreSQL**, this project provides a collection of moderation and anti-spam features to help group administrators maintain a safer, more organized, and better-managed environment.

## ✨ Features

### 🛡️ Moderation & Member Management

- **Warning System** — Issue warnings to users, remove individual warnings, and clear a user's warning history.
- **Member Restrictions** — Mute or ban users who violate group rules.
- **Message Moderation** — Automatically detect and remove inappropriate messages.
- **Custom Word Filtering** — Detect messages containing filtered words and moderate them according to the bot's configured behavior.

### 🔒 Group Security & Anti-Spam

- **Anti-Spam Protection** — Help prevent spam and unwanted messages in group conversations.
- **Link Filtering** — Detect and remove messages containing prohibited links.
- **Automated Moderation** — Reduce the need for manual intervention by automating routine moderation tasks.

### 💬 Communication & Group Utilities

- **Private Messaging Between Members** — Enable members to send private messages to one another through the bot.
- **Group Rules** — Store and display group rules to help members understand community guidelines.
- **Daily Reports** — Provide daily summaries of group activity and moderation status.

## 🛠️ Tech Stack

| Technology | Purpose |
| --- | --- |
| Python | Core application logic |
| Telegram Bot API | Telegram communication and group interactions |
| PostgreSQL | Persistent data storage |
| `psycopg2` | PostgreSQL connectivity |

## 🏗️ Project Structure

The project follows a modular structure that separates request handling, business logic, database access, and shared utilities.

```text
telegram-group-manager-bot/
├── database/       # Database-related components
├── handlers/       # Telegram update and command handlers
├── repositories/   # Data access layer
├── services/       # Business logic and application services
├── utils/          # Shared utilities and helper functions
├── .env.example    # Example environment configuration
├── main.py         # Application entry point
└── requirements.txt
```

This separation helps keep the codebase maintainable and makes it easier to extend individual features without unnecessarily affecting other parts of the application.

## 🚀 Getting Started

Follow these steps to set up the project locally.

### Prerequisites

Before running the bot, make sure you have:

- Python installed.
- PostgreSQL installed and running, or access to a PostgreSQL server.
- A Telegram bot token created through [@BotFather](https://t.me/BotFather).
- Git installed on your system.

### 1. Clone the Repository

```bash
git clone https://github.com/Younes-0l/telegram-group-manager-bot.git
cd telegram-group-manager-bot
```

### 2. Create a Virtual Environment

Create an isolated Python environment:

```bash
python -m venv .venv
```

Activate it on Linux or macOS:

```bash
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install Dependencies

Install the project's Python dependencies:

```bash
python -m pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file from the provided example.

On Linux or macOS:

```bash
cp .env.example .env
```

On Windows:

```powershell
Copy-Item .env.example .env
```

Open `.env` and configure the following variables:

| Variable | Description |
| --- | --- |
| `DOWNLOADER_TOKEN` | Telegram bot token obtained from BotFather |
| `DB_HOST` | PostgreSQL server hostname |
| `DB_PORT` | PostgreSQL server port, typically `5432` |
| `DB_NAME` | Name of the PostgreSQL database |
| `DB_USER` | PostgreSQL username |
| `DB_PASSWORD` | PostgreSQL password |

Example configuration:

```dotenv
DOWNLOADER_TOKEN=your_telegram_bot_token

DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
```

Replace the example values with your actual credentials. Never commit your real `.env` file or expose your bot token and database credentials in a public repository.

### 5. Prepare the Database

Create a PostgreSQL database and configure the connection settings in `.env`.

Make sure the configured database user has the required permissions to access and modify the database.

If the project requires additional database initialization steps, follow the implementation provided in the `database/` directory.

### 6. Run the Bot

With the virtual environment activated and the configuration completed, start the application:

```bash
python main.py
```

## ⚙️ Telegram Group Setup

To use the bot's moderation features:

1. Create your bot through [@BotFather](https://t.me/BotFather).
2. Add the bot to your Telegram group.
3. Grant the bot the necessary administrator permissions for the features you intend to use, including deleting messages and restricting members.
4. Configure the environment variables and PostgreSQL connection.
5. Start the application and verify that the bot responds correctly.

**Note:** The exact permissions required depend on the moderation actions enabled in your group.

## 🔐 Security Considerations

- Keep your Telegram bot token and database credentials private.
- Store sensitive configuration values in environment variables rather than hardcoding them in the source code.
- Grant the bot only the Telegram permissions it needs.
- Use a dedicated PostgreSQL user with appropriately limited privileges.
- Test moderation behavior in a test group before deploying the bot to an active community.

## 🧩 Design Principles

The project is organized around a modular architecture with distinct responsibilities:

- **Separation of Concerns** — Handlers, services, repositories, and database components are organized separately.
- **Maintainability** — Individual components can be updated with fewer unrelated changes.
- **Extensibility** — The modular structure provides a foundation for adding new moderation and group-management features.
- **Persistent Storage** — PostgreSQL provides a relational database for application data.

## 🤝 Contributing

Contributions, bug reports, and feature suggestions are welcome.

1. Fork the repository.
2. Create a feature branch:

   ```bash
   git checkout -b feature/your-feature
   ```

3. Commit your changes:

   ```bash
   git commit -m "Add your feature"
   ```

4. Push the branch to your fork:

   ```bash
   git push origin feature/your-feature
   ```

5. Open a Pull Request describing your changes.

## 📄 License

Please refer to the repository's license file, if available, for the applicable terms of use.

## 👨‍💻 Author

**Younes**

- GitHub: [@Younes-0l](https://github.com/Younes-0l)
- Repository: [telegram-group-manager-bot](https://github.com/Younes-0l/telegram-group-manager-bot)

---

If you find this project useful, consider giving the repository a ⭐ on GitHub.
