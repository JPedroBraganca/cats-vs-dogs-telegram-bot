from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PreCheckoutQueryHandler, CallbackContext, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, Update
from io import BytesIO
import requests
import os
import cv2
import requests
import base64
import numpy as np
import mysql.connector
import os

HOST_MYSQL = os.environ["HOST_MYSQL"]
TOKEN_MYSQL = os.environ["TOKEN_MYSQL"]
AUTH_TOKEN = os.environ["AUTH_TOKEN"]
API_URL = os.environ["API_URL"]
ADMIN_CHAT_ID = os.environ["ADMIN_CHAT_ID"]
PAY_TEST_TOKEN = os.environ["PAY_TEST_TOKEN"]

config = {
    'user': 'root',
    'password': TOKEN_MYSQL,
    'host': HOST_MYSQL,
    'database': 'jpbottest'}

cnxn = mysql.connector.connect(**config)
cursor = cnxn.cursor() 

def main_menu_keyboard():
  
  keyboard = [[InlineKeyboardButton('Check Credits', callback_data='m1')],
              [InlineKeyboardButton('Buy Credits', callback_data='m2')],
              [InlineKeyboardButton('About', callback_data='m3')],
              [InlineKeyboardButton('Help', callback_data='m4')]]
  return InlineKeyboardMarkup(keyboard)

def menu_keyboard():

    keyboard = [[InlineKeyboardButton('Buy Credits', callback_data='m2')]]
    return InlineKeyboardMarkup(keyboard)


def start(update, context):
    
    update.message.reply_text(
        
    """Hey! Welcome to the JP's bot! 
    
    This bot classifies images into dogs or cats!

    To make a prediction, just upload a photo! (price: 1 credit)
    
    Choose an option to continue!
    
    """, reply_markup=main_menu_keyboard())
    user_id = update.effective_user.id
    #user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name
    username = update.message.from_user.username

    sql = """INSERT INTO usersdata (user_id, first_name, last_name, username, credits, n_predicts)
         SELECT * FROM (SELECT %s AS user_id, %s AS first_name, %s AS last_name, %s AS username, %s AS credits, %s AS n_predicts) AS tmp
         WHERE NOT EXISTS (
        SELECT user_id FROM usersdata WHERE user_id = %s
        ) LIMIT 1"""

    the_vals = (user_id, first_name, last_name, username, 5, 0, user_id)
    cursor.execute(sql, the_vals)
    cnxn.commit()

    query = "SELECT credits FROM usersdata WHERE user_id = %s"

    vals = (user_id, )

    cursor.execute(query, vals)

    myresult = cursor.fetchall()

    n_credits = myresult[0][0]

    context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f'✅ {user_id} - {first_name} {last_name} - {username} started the bot!')
    context.bot.send_message(chat_id=user_id, text=f"Welcome! You have {n_credits} credits!")

def main_menu_message():
  return 'Choose an option:'

def main_menu(bot, update):
  bot.callback_query.message.edit_text(main_menu_message(),
                          reply_markup=main_menu_keyboard())

def the_help(update, context):
    context.bot.send_message(chat_id=update.effective_user.id,
                             text="To make a prediction, just upload a photo!")

def the_about(update, context):
    context.bot.send_message(chat_id=update.effective_user.id,
                             text="""
    
    This bot was made by João Pedro de Bragança (based on sweat and tears, but with love!)
    
    GitHub: https://github.com/JPedroBraganca
    Medium: https://medium.com/@joaopedrodebraganca
    
    """)

def handle_message(update, context):
    #update.message.reply_text(update.message.from_user.id)
    name = update.message.from_user.first_name
    #update.message.reply_text(update.message.from_user.last_name)
    #update.message.reply_text(update.message.from_user.username)
    update.message.reply_text(f"Hey {name}! Ready for some predicts? =D", reply_markup=main_menu_keyboard())

def add_credits(update, context):
    
    user_id = update.effective_user.id
    val = int(context.args[0])    
    context.bot.send_message(chat_id=user_id, text=f"Adding {val} credits!")
    
    query = "SELECT credits FROM usersdata WHERE user_id = %s"

    vals = (user_id, )

    cursor.execute(query, vals)

    myresult = cursor.fetchall()

    new_value = myresult[0][0] + val
    new_value = (new_value, user_id)

    query_2 = "UPDATE usersdata SET credits = %s WHERE user_id = %s"

    cursor.execute(query_2, new_value)
    
    cnxn.commit()
    
    cursor.execute(query, vals)
    myresult = cursor.fetchall()
    n_credits = myresult[0][0] 
    
    context.bot.send_message(chat_id=user_id, text=f"Now you have {n_credits} credits!")

def check_credits(update, context):

    user_id = update.effective_user.id
    
    query = "SELECT credits FROM usersdata WHERE user_id = %s"

    vals = (user_id, )

    cursor.execute(query, vals)

    myresult = cursor.fetchall()
    n_credits = myresult[0][0] 

    context.bot.send_message(chat_id=user_id, text=f"You have {n_credits} credits!")


def the_buy_credits(update: Update, context: CallbackContext):
    """Sends an invoice with shipping-payment."""
    context.bot.send_message(chat_id=update.effective_user.id,
    
    
    text=f"""
    The payment system really works, and the money lands on my account! 
    
    Now the system is enabled for TESTING ONLY, so don't put your real credit card!

    Use this one to test the payment system:

    NUMBER: 5555 5555 5555 4444
    DATE: Any 3 digits
    CVC: Any future date
    
    """)
    
    chat_id = update.effective_user.id
    title = "Buying Credits"
    description = "10 credits"
    # select a payload just for you to recognize its the donation from your bot
    payload = "Custom-Payload"
    # In order to get a provider_token see https://core.telegram.org/bots/payments#getting-a-token
    currency = "BRL"
    # price in dollars
    price = 10
    # price * 100 so as to include 2 decimal points
    # check https://core.telegram.org/bots/payments#supported-currencies for more details
    prices = [LabeledPrice("Test", price * 100)]

    # optionally pass need_name=True, need_phone_number=True,
    # need_email=True, need_shipping_address=True, is_flexible=True
    context.bot.send_invoice(
        chat_id=chat_id,
        title=title,
        description=description,
        payload=payload,
        provider_token=PAY_TEST_TOKEN,
        start_parameter=payload,
        currency=currency,
        prices=prices,
        need_name=False,
        need_phone_number=False,
        need_email=False,
        need_shipping_address=False,
        is_flexible=False,
    )

def error(update, context):
    print(f'Update {update} caused error {context.error}')

def precheckout_callback(update: Update, context: CallbackContext):
    """Answers the PreQecheckoutQuery"""
    query = update.pre_checkout_query
    # check the payload, is this from your bot?
    if query.invoice_payload != "Custom-Payload":
        # answer False pre_checkout_query
        query.answer(ok=False, error_message="Something went wrong...")
    else:
        query.answer(ok=True)

def successful_payment_callback(update: Update, context: CallbackContext):
    """Confirms the successful payment."""
    # do something after successfully receiving payment?
    update.message.reply_text("Thank you for your payment!")
    user_id = update.effective_user.id    
    context.bot.send_message(chat_id=user_id, text="Adding 10 credits!")

    query = "SELECT credits FROM usersdata WHERE user_id = %s"

    vals = (user_id, )

    cursor.execute(query, vals)

    myresult = cursor.fetchall()

    new_value = myresult[0][0] + 10
    new_value = (new_value, user_id)

    query_2 = "UPDATE usersdata SET credits = %s WHERE user_id = %s"

    cursor.execute(query_2, new_value)
    
    cnxn.commit()
    
    cursor.execute(query, vals)
    myresult = cursor.fetchall()
    n_credits = myresult[0][0]
    
    context.bot.send_message(chat_id=user_id, text=f"Now you have {n_credits} credits!", reply_markup=main_menu_keyboard())


def handle_photo(update, context):
    
    user_id =  update.effective_user.id
    
    query = "SELECT credits FROM usersdata WHERE user_id = %s"

    vals = (user_id, )

    cursor.execute(query, vals)

    myresult = cursor.fetchall()

    n_credits = myresult[0][0]

    if n_credits <= 0:
        context.bot.send_message(chat_id=user_id,
                                 text=f"You have {n_credits} credits! Please buy more!",
                                 reply_markup=menu_keyboard())

    else:

        query_2 = "UPDATE usersdata SET credits = %s WHERE user_id = %s"

        cursor.execute(query_2, (n_credits - 1, user_id))
        cnxn.commit()

        cursor.execute(query, vals)
        myresult = cursor.fetchall()
        n_credits = myresult[0][0]
        
        context.bot.send_message(chat_id=user_id, text=f"Now you have {n_credits} credits!")
    
        context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f'✅ {user_id} is using the model!')
        file = context.bot.get_file(update.message.photo[-1].file_id)
        f = BytesIO(file.download_as_bytearray())
        file_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)

        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        string_img = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()

        update.message.reply_text("""
    
            Predicting...

        It may take a while for the first predict!

        (GCP - cold start =/)
        
        """)

        r = requests.post(API_URL, json={'image': string_img})
    
    
        prob_dog = r.json()["prob_dog"] * 100 
        prob_cat = r.json()["prob_cat"] * 100
        predicted_class = r.json()["predicted_class"]
        update.message.reply_text(f"""
        
        Result!

    Predicted Class: {predicted_class}
    Probability - Dog: {prob_dog:.2f}%
    Probability - Cat: {prob_cat:.2f}%
        
        """, reply_markup=main_menu_keyboard())
    

updater = Updater(AUTH_TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("add_credits", add_credits))
dp.add_handler(MessageHandler(Filters.text, handle_message))
dp.add_handler(MessageHandler(Filters.photo, handle_photo))
dp.add_handler(MessageHandler(Filters.photo, handle_photo))
dp.add_handler(MessageHandler(Filters.successful_payment, successful_payment_callback))
dp.add_handler(PreCheckoutQueryHandler(precheckout_callback))
dp.add_handler(CallbackQueryHandler(check_credits, pattern='m1'))
dp.add_handler(CallbackQueryHandler(the_buy_credits, pattern='m2'))
dp.add_handler(CallbackQueryHandler(the_about, pattern='m3'))
dp.add_handler(CallbackQueryHandler(the_help, pattern='m4'))
dp.add_error_handler(error)

updater.start_polling()
updater.idle()