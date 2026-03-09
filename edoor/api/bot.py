#updater = Updater('5027474274:AAGiZtbOzO1xCNOql0B5PuxTDIG9GncGd6Y', True)
import frappe
from telegram.ext import *
 
    
print('Starting a bot....')

     
async def start_commmand(update, context):
    await update.message.reply_text('Hello! your odrer is here ')
    print(update)

async def start_commmand2(update, context):
    await update.message.reply_text('Hello! than for ur order')

async def send_today_revenue(update, context):
    data =["Pheakdey"]
    data = frappe.get_doc("Sale","SO2024-0175")
    
    
    await update.message.reply_text(data.name)


if __name__ == '__main__':
    application = Application.builder().token('5027474274:AAGiZtbOzO1xCNOql0B5PuxTDIG9GncGd6Y').build()

    # Commands
    application.add_handler(CommandHandler('myorder', start_commmand))
    application.add_handler(CommandHandler('neworder', start_commmand2))
    application.add_handler(CommandHandler('TodayRevenue', send_today_revenue))

    # Run bot
    application.run_polling(1.0)
