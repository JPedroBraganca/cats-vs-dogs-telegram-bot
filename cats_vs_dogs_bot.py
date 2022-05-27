from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PreCheckoutQueryHandler, CallbackContext, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, Update, ReplyKeyboardMarkup, KeyboardButton
from io import BytesIO, StringIO
import requests
import os
import cv2
import requests
import base64
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime

AUTH_TOKEN = os.environ["AUTH_TOKEN"]
API_URL = os.environ["API_URL"]
ADMIN_CHAT_ID = os.environ["ADMIN_CHAT_ID"]
PAY_TEST_TOKEN = os.environ["PAY_TEST_TOKEN"]

check_button = KeyboardButton('Check Credits')



#keyboard_intro = ReplyKeyboardMarkup(keyboard=[["Help"], ["Check Credits", "Buy Credits"], ["About"]], resize_keyboard=True)
#keyboard_intro = ReplyKeyboardMarkup(
#                                    keyboard=[["Check", "Buy"], ["Help"], ["About"]],
#                                    resize_keyboard=True,
#                                    one_time_keyboard=False,
#                                    input_field_placeholder="okay")

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
    
    data = pd.read_csv("data.csv")
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

    

    context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f'✅ {user_id} - {first_name} {last_name} - {username} started the bot!')
    if user_id not in data["user_id"].unique():
        add_data = {"user_id": [user_id],
                    "first_name": [first_name],
                    "last_name": [last_name],
                    "username": [username],
                    "credits": [5]}
        add_data = pd.DataFrame(add_data)
        data = pd.concat((data, add_data), axis=0, ignore_index=True)
        data.to_csv("data.csv", index=False)
        context.bot.send_message(chat_id=user_id, text=f"Welcome, you have 5 free credits!")
    else:
        data_user = data[data.user_id == user_id]
        n_credits = data_user["credits"].values[0]
        context.bot.send_message(chat_id=user_id, text=f"Welcome back! You have {n_credits} credits!")

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
    
    data = pd.read_csv("data.csv")
    data = data[data.user_id == user_id]
    n_credits = data.loc[data.user_id == user_id, "credits"].values[0]
    data.loc[data.user_id == user_id, "credits"] = n_credits + val
    n_credits = data.loc[data.user_id == user_id, "credits"].values[0]
    context.bot.send_message(chat_id=user_id, text=f"Now you have {n_credits} credits!")
    data.to_csv("data.csv", index=False)

def check_credits(update, context):

    user_id = update.effective_user.id
    data = pd.read_csv("data.csv")
    n_credits = data.loc[data.user_id == user_id, "credits"].values[0]
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
        provider_token=os.environ["PAY_TEST_TOKEN"],
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
    
    data = pd.read_csv("data.csv")
    data = data[data.user_id == user_id]
    n_credits = data.loc[data.user_id == user_id, "credits"].values[0]
    data.loc[data.user_id == user_id, "credits"] = n_credits + 10
    n_credits = data.loc[data.user_id == user_id, "credits"].values[0]
    context.bot.send_message(chat_id=user_id, text=f"Now you have {n_credits} credits!", reply_markup=main_menu_keyboard())
    data.to_csv("data.csv", index=False)

    transactions = pd.read_csv("transactions.csv")
    this_transaction = pd.DataFrame({"user_id":[user_id],
                                     "time":[datetime.datetime.now()]})
    transactions = pd.concat((transactions, this_transaction), axis=0, ignore_index=True)


def handle_photo(update, context):

    data = pd.read_csv("data.csv")
    user_id =  update.effective_user.id
    data = data[data.user_id == user_id]
    n_credits = data.loc[data.user_id == user_id, "credits"].values[0]

    if n_credits <= 0:
        context.bot.send_message(chat_id=user_id,
                                 text=f"You have {n_credits} credits! Please buy more!",
                                 reply_markup=menu_keyboard())

    else:

        data.loc[data.user_id == user_id, "credits"] = n_credits - 1
        n_credits = data.loc[data.user_id == user_id, "credits"].values[0]
        context.bot.send_message(chat_id=user_id, text=f"Now you have {n_credits} credits!")
        data.to_csv("data.csv", index=False)

    
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
#dp.add_handler(CommandHandler("Help", help))
#dp.add_handler(CommandHandler("About", about))
dp.add_handler(CommandHandler("add_credits", add_credits))
#dp.add_handler(CommandHandler("Check", check_credits))
#dp.add_handler(CommandHandler("Buy", buy_credits))
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