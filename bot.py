from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import io

# Replace with your bot token
TOKEN = "7591873096:AAGvlYqxIRv2VNroqFdvuQTjXgLq2S_DgzQ"

# Temporary storage for user images
user_images = {}

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! 👋 Send me photos or image files, and I will create a PDF for you.\n"
        "When ready, type /createpdf to get your PDF."
    )

# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Commands:\n"
        "/start - Welcome message\n"
        "/help - Show this help\n"
        "Send me photos or image files, then type /createpdf to generate your PDF."
    )

# Handle incoming photos
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Get highest resolution photo
    photo = update.message.photo[-1]
    photo_file = await photo.get_file()
    photo_bytes = await photo_file.download_as_bytearray()

    if user_id not in user_images:
        user_images[user_id] = []
    user_images[user_id].append(photo_bytes)

    await update.message.reply_text(f"✅ Image received! Total images: {len(user_images[user_id])}")

# Handle incoming documents (images only)
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    doc = update.message.document

    # Only accept image files
    if doc.mime_type.startswith("image/"):
        doc_file = await doc.get_file()
        doc_bytes = await doc_file.download_as_bytearray()

        if user_id not in user_images:
            user_images[user_id] = []
        user_images[user_id].append(doc_bytes)

        await update.message.reply_text(f"✅ Image file received! Total images: {len(user_images[user_id])}")
    else:
        await update.message.reply_text("❌ Only image files are accepted!")

# /createpdf command
async def create_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    images = user_images.get(user_id)

    if not images:
        await update.message.reply_text("❌ You haven't uploaded any images yet!")
        return

    await update.message.reply_text(f"📄 Creating PDF from {len(images)} images...")

    pdf_images = []
    for img_bytes in images:
        img = Image.open(io.BytesIO(img_bytes))
        if img.mode != "RGB":
            img = img.convert("RGB")
        pdf_images.append(img)

    pdf_bytes = io.BytesIO()
    pdf_images[0].save(pdf_bytes, format="PDF", save_all=True, append_images=pdf_images[1:])
    pdf_bytes.seek(0)

    await update.message.reply_document(document=pdf_bytes, filename="images.pdf")
    user_images[user_id] = []

    await update.message.reply_text("✅ PDF created and sent! You can start uploading new images.")

# Main function
def main():
    app = Application.builder().token(TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("createpdf", create_pdf))

    # Photo handler
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Document handler (images only)
    app.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
