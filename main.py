import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from PIL import Image
from google import genai
from google.genai import types
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

# Dummy Web Server for Render Free Web Service
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Neetra Bot is Active!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = (
    "Your name is Neetra. You are a highly intelligent, sharp, and personalized AI assistant.\n\n"
    "CREATOR & OWNER INFORMATION:\n"
    "- Full Name: Aayush Hariprakash Mishra\n"
    "- Parents: Hari Prakash Mishra (Father), Sangeeta Mishra (Mother)\n"
    "- Location: Surat, Gujarat, India\n"
    "- Relationship/Role: You belong exclusively to Aayush H. Mishra. He created, developed, and hosts you.\n\n"
    "PERSONALIZED BEHAVIOR:\n"
    "1. Always address Aayush warmly and recognize him as your creator and master.\n"
    "2. Always identify as Neetra when asked about your identity.\n"
    "3. If anyone asks who created or owns you, give full credit to Aayush Hariprakash Mishra.\n"
    "4. Maintain a sharp, helpful, and naturally adaptive tone."
)

def ask_neetra(prompt, image_path=None):
    contents = [prompt] if prompt else []
    if image_path:
        img = Image.open(image_path)
        contents.append(img)
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7
            )
        )
        return response.text
    except Exception as e:
        return f"Error: {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👁️ Neetra AI active hai! Boliyega Aayush bhai, kya help chahiye?")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_chat_action("typing")
    reply = ask_neetra(user_text)
    await update.message.reply_text(reply)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_chat_action("typing")
    photo_file = await update.message.photo[-1].get_file()
    photo_path = "user_photo.jpg"
    await photo_file.download_to_drive(photo_path)
    
    caption = update.message.caption or "Analyze this image in detail."
    reply = ask_neetra(caption, image_path=photo_path)
    await update.message.reply_text(reply)

if __name__ == "__main__":
    threading.Thread(target=run_dummy_server, daemon=True).start()
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("🚀 Neetra Server Bot Live!")
    app.run_polling(drop_pending_updates=True)
    
