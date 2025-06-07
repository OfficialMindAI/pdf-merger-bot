import os
import logging
import tempfile
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from PyPDF2 import PdfReader, PdfWriter, PdfMerger

# Enable logging
telemetry = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

# Conversation states
WAITING_FOR_PDF, HAS_PDFS, WAITING_FOR_PAGE_NUMBER = range(3)

# PDF utilities
def remove_page(input_path: str, output_path: str, page_num: int) -> None:
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for idx, page in enumerate(reader.pages):
        if idx != page_num - 1:
            writer.add_page(page)
    with open(output_path, 'wb') as out_f:
        writer.write(out_f)


def merge_pdfs(paths: list[str], output_path: str) -> None:
    merger = PdfMerger()
    for p in paths:
        merger.append(p)
    with open(output_path, 'wb') as out_f:
        merger.write(out_f)
    merger.close()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Welcome! Please send me a PDF to begin."
    )
    return WAITING_FOR_PDF

# Cancel handler\ n
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # cleanup user files\ n    
    files = context.user_data.get('pdfs', [])
    for f in files:
        try:
            os.remove(f)
        except:
            pass
    context.user_data.clear()
    await update.message.reply_text("Operation cancelled. Use /start to begin again.")
    return ConversationHandler.END

# Receive PDF
async def receive_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    msg = update.message
    if not msg.document or msg.document.mime_type != 'application/pdf':
        await msg.reply_text("Please send a valid PDF document.")
        return WAITING_FOR_PDF

    # download
    tmp = tempfile.gettempdir()
    user_id = msg.from_user.id
    idx = len(context.user_data.get('pdfs', []))
    path = os.path.join(tmp, f"{user_id}_{idx}.pdf")
    file = await context.bot.get_file(msg.document.file_id)
    await file.download_to_drive(path)  # v20 compatibility

    context.user_data.setdefault('pdfs', []).append(path)
    return await show_menu(update, context)

# Show menu\ n
async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pdfs = context.user_data['pdfs']
    buttons = [[InlineKeyboardButton("Add another PDF", callback_data='add')]]

    if len(pdfs) == 1:
        buttons += [
            [InlineKeyboardButton("Remove a page", callback_data='remove')],
            [InlineKeyboardButton("Finish & get PDF", callback_data='finish')]
        ]
    else:
        buttons += [
            [InlineKeyboardButton("Remove page (last PDF)", callback_data='remove')],
            [InlineKeyboardButton("Merge all PDFs", callback_data='merge')],
            [InlineKeyboardButton("Reset", callback_data='reset')]
        ]

    kb = InlineKeyboardMarkup(buttons)
    if update.callback_query:
        await update.callback_query.edit_message_text("Choose an option:", reply_markup=kb)
    else:
        await update.message.reply_text("Choose an option:", reply_markup=kb)
    return HAS_PDFS

# Menu handler
async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    choice = query.data

    if choice == 'add':
        await query.edit_message_text("Send another PDF:")
        return WAITING_FOR_PDF

    if choice == 'remove':
        context.user_data['remove_idx'] = len(context.user_data['pdfs']) - 1
        await query.edit_message_text("Which page number to remove? (e.g., 1)")
        return WAITING_FOR_PAGE_NUMBER

    if choice == 'merge':
        out_path = os.path.join(tempfile.gettempdir(), f"merged_{update.effective_user.id}.pdf")
        merge_pdfs(context.user_data['pdfs'], out_path)
        # cleanup old
        for p in context.user_data['pdfs']:
            os.remove(p)
        context.user_data['pdfs'] = [out_path]
        await query.edit_message_text("PDFs merged.")
        return await show_menu(update, context)

    if choice == 'reset':
        for p in context.user_data['pdfs']:
            os.remove(p)
        context.user_data.clear()
        await query.edit_message_text("Reset complete. Send a PDF to start.")
        return WAITING_FOR_PDF

    if choice == 'finish':
        out = context.user_data['pdfs'][0]
        await context.bot.send_document(chat_id=query.message.chat_id, document=open(out, 'rb'))
        os.remove(out)
        context.user_data.clear()
        await query.edit_message_text("Here is your PDF. Use /start to run again.")
        return ConversationHandler.END

    return HAS_PDFS

# Receive page number
async def receive_page_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if not text.isdigit():
        await update.message.reply_text("Enter a valid number.")
        return WAITING_FOR_PAGE_NUMBER

    page = int(text)
    idx = context.user_data['remove_idx']
    src = context.user_data['pdfs'][idx]
    reader = PdfReader(src)
    if page < 1 or page > len(reader.pages):
        await update.message.reply_text(f"Number out of range. Enter 1-{len(reader.pages)}.")
        return WAITING_FOR_PAGE_NUMBER

    out = os.path.join(tempfile.gettempdir(), f"mod_{update.effective_user.id}_{idx}.pdf")
    remove_page(src, out, page)
    os.remove(src)
    context.user_data['pdfs'][idx] = out

    await update.message.reply_text("Page removed.")
    return await show_menu(update, context)

# Main
if __name__ == '__main__':
    TOKEN = 'YOUR_TOKEN'  # Set env var
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WAITING_FOR_PDF: [MessageHandler(filters.Document.PDF, receive_pdf)],
            HAS_PDFS: [CallbackQueryHandler(handle_menu)],
            WAITING_FOR_PAGE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_page_number)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv)
    app.run_polling()
