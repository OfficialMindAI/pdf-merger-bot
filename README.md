# 📄 Telegram PDF Bot
A Telegram bot for manipulating PDF documents. Users can upload one or more PDF files, remove specific pages, or merge multiple files into a single document — all directly through Telegram.

## 🚀 Features
Upload and manage multiple PDFs

Remove specific pages from any uploaded PDF

Merge multiple PDF files into one

Automatically sends the final PDF back to the user

Clean and intuitive Telegram UI using inline keyboards

Session-specific temporary file handling and cleanup

## 🧰 Libraries Used
Library	Purpose	Version (tested)
python-telegram-bot	Telegram Bot Framework	20.8
PyPDF2	PDF reading, writing, and merging	3.0.1
logging	Logging events and bot operations	Standard Library
tempfile, os	Temporary file creation and cleanup	Standard Library

Note: Tested with Python 3.11+

## 🛠 Installation
1. Clone the repository
 
git clone  https://github.com/OfficialMindAI/pdf-merger-bot
cd telegram-pdf-bot
## 2. Create a virtual environment (optional but recommended)
 
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
## 3. Install dependencies
 
pip install -r requirements.txt
 
  
## 🔐 Bot Token Setup
Create a Telegram bot using @BotFather.

Copy your bot token.

Set the token as an environment variable:

On macOS/Linux:
 
export TELEGRAM_TOKEN="your-telegram-token"
On Windows:
 
set TELEGRAM_TOKEN=your-telegram-token
Or you can hardcode it temporarily (not recommended for production):
 
TOKEN = "your-telegram-token"
## ▶️ Running the Bot
 
python bot.py
The bot will start and wait for users to send PDFs through Telegram.

## 🧪 Example Use Case
User sends a PDF to the bot.

Bot offers options:

Add another PDF

Remove a page

Merge PDFs

Finish and send final file

User selects “Remove a page”, inputs the page number.

Final output is sent directly via chat.

## 📂 Temporary File Management
All PDFs are stored temporarily using the system's temp directory.

Files are deleted after the session ends or is cancelled.

Prevents disk clutter and ensures user privacy.

## 🧼 Error Handling
Verifies file type on upload.

Handles invalid page numbers with validation.

Gracefully cancels operations with /cancel.

## 📝 License
This project is open source and available under the MIT License.

## 🙋‍♂️ Contributing
Contributions are welcome! Please open an issue or submit a pull request.

