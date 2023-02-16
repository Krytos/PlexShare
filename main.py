import asyncio
import logging
import os
from dataclasses import dataclass

import stripe
import uvicorn
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, Request, Response
from pymongo import MongoClient
from telebot import types
from telebot.async_telebot import AsyncTeleBot

# from overseerr import get_active_requests, main as overseerr_main
from plex import update_plex_user
from stripe_manage import get_prices

load_dotenv(find_dotenv())

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logging.getLogger("uvicorn").addHandler(handler)
logging.getLogger("uvicorn").setLevel(logging.INFO)
logger = logging.getLogger("uvicorn")

# locale.setlocale(locale.LC_MONETARY, 'de_DE')

app = FastAPI()
# apihelper.API_URL = "http://localhost:4200/bot{0}/{1}"
# TODO: Change to production bot
bot = AsyncTeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))
logger.info("Bot started")

# stripe.api_key = os.getenv("STRIPE_KEY_LIVE")
stripe.api_key = os.getenv("STRIPE_KEY_LIVE")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
host = os.getenv("HOST")
client = MongoClient(os.getenv("MONGO_URL"))
db = client['plexshare']


@dataclass()
class User:
	email: str = None
	plex_id: int = None
	cr_id: str = None
	stripe_id: str = None
	status: str = None


async def update_db_user(user: dataclass):
	db.users.update_one({"email": user.email}, {"$set": user.__dict__}, upsert=True)


async def get_db_user(email: str) -> dataclass:
	return User(**db.users.find_one({"email": email}, {'_id': False})) if db.users.find_one({"email": email}) else None


async def get_db_all_users() -> list:
	return "\n".join([User(**u) for u in db.users.find({}, {'_id': False})])


# @bot.message_handler(commands=["start"])
# async def search_stripe_user(message):
# 	telegram_id = message.from_user.id
# 	button_data = f"butt_{telegram_id}"
# 	chat_id = message.chat.id
# 	user = stripe.Customer.search(query=f"metadata['telegram_id']:'{telegram_id}'").data
# 	if user:
# 		menu = types.InlineKeyboardMarkup(row_width=2)
# 		menu.add(
# 			types.InlineKeyboardButton("Abo erstellen", callback_data=button_data)
# 		)
# 		await bot.send_message(chat_id, "Willkommen zurück!", reply_markup=menu, )
# 		return True
# 	else:
# 		return False
#
# @bot.callback_query_handler(func=lambda call: True)
# async def callback_query(call):
# 	data = call.data
# 	user_id = call.from_user.id
# 	if data.startswith("butt_") and data.split("_")[1] == str(user_id):
# 		await bot.answer_callback_query(call.id, "Abo erstellen")
# 		# await handle_subscribe(call.message)
# 		await bot.send_message(user_id, "Das ist leider noch nicht eingebaut.")


@bot.message_handler(commands=['subscribe', 'abo'])
async def handle_subscribe(message):
	await bot.delete_message(message.chat.id, message.message_id)
	user_id = message.from_user.id
	# if await search_stripe_user(user_id, message.chat.id):
	# 	return
	msg = "Bitte wähle ein Abo:\n\n"
	links = stripe.PaymentLink.list(active=True).data
	prices = stripe.Price.list(active=True).data
	subs = await get_prices(links, prices)
	buttons = [types.InlineKeyboardButton(
		text=f"{sub['name']} - {sub['price_format']}", url=f"{sub['url']}?client_reference_id={user_id}",
	) for sub in subs]
	markup = types.InlineKeyboardMarkup(row_width=2)
	markup.add(*buttons)

	await bot.send_photo(
		user_id, photo="AgACAgQAAxkBAANBY9a6bGpnHukwlmVeczL1EdJM9BoAAiq7MRucErhSRHMDRluHAwIBAAMCAAN4AAMtBA",
		caption=msg, reply_markup=markup
	)


# @bot.message_handler(commands=['start'])
# async def handle_start(message):
# 	await bot.delete_message(message.chat.id, message.message_id)
# 	await bot.send_message(message.from_user.id, """
# 		Hallo, wie kann ich dir weiter helfen? Mit /abo kannst du ein Abo für den Plex Server kaufen. Mit /konto kannst
# 		du über die Stripe Webseite dein Abo verwalten. Mit /requests kannst du dir die aktuellen Overseerr Requests
# 		anzeigen lassen. Mit /clearrequests kannst du alle Overseerr Requests deren Verfügbarkeit falsch angezeigt
# 		wurde löschen lassen. Mit /help kannst du dir diese Nachricht erneut anzeigen lassen.
# 		""")
#
# @bot.message_handler(commands=['help'])
# async def handle_help(message):
# 	await bot.delete_message(message.chat.id, message.message_id)
# 	await bot.send_message(message.from_user.id, """
# 		Mit /abo kannst du ein Abo für den Plex Server kaufen. Mit /konto kannst
# 		du über die Stripe Webseite dein Abo verwalten. Mit /requests kannst du dir die aktuellen Overseerr Requests
# 		anzeigen lassen. Mit /clearrequests kannst du alle Overseerr Requests deren Verfügbarkeit falsch angezeigt
# 		wurde löschen lassen. Mit /help kannst du dir diese Nachricht erneut anzeigen lassen.
# 		""")
#
# @bot.message_handler(commands=['requests'])
# async def handle_requests(message):
# 	await bot.delete_message(message.chat.id, message.message_id)
# 	await bot.send_message(message.chat.id, text=get_active_requests())
#
#
# @bot.message_handler(commands=['clearrequests'])
# async def handle_clearrequests(message):
# 	await bot.delete_message(message.chat.id, message.message_id)
# 	await overseerr_main()
# 	await bot.send_message(message.chat.id, text="Nicht mehr vorhandene requests wurden gelöscht.")


@bot.message_handler(commands=['konto', 'account'])
async def handle_account(message):
	await bot.delete_message(message.chat.id, message.message_id)
	buttons = [types.InlineKeyboardButton(
		text="Konto verwalten", url=f"https://billing.stripe.com/p/login/dR64gUdF79LS12waEE",
	)]
	markup = types.InlineKeyboardMarkup(row_width=4)
	markup.add(*buttons)
	await bot.send_message(message.from_user.id, "Kunden Konto öffnen", reply_markup=markup)



@bot.message_handler(commands=['users'])
async def handle_users(message):
	await bot.delete_message(message.chat.id, message.message_id)
	if message.from_user.id == 17508705:
		users = await get_db_all_users()
		await bot.send_message(message.from_user.id, text=users)


@bot.message_handler()
async def handle_message(message):
	if message.from_user.id != 17508705:
		await bot.delete_message(message.chat.id, message.message_id)


@app.on_event("startup")
async def startup():
	logger.info("Starting up...")
	asyncio.create_task(bot.polling(none_stop=True, interval=0.1))


async def get_plex_id(user):
	while not user.plex_id:
		await update_plex_user(user)
		await asyncio.sleep(10)
	await update_db_user(user)


@app.post("/webhook_stripe")
async def stripe_webhook(request: Request, response: Response):
	payload = await request.body()
	sig_header = request.headers['stripe-signature']
	event = None

	try:
		event = stripe.Webhook.construct_event(
			payload, sig_header, endpoint_secret
		)
	except ValueError as e:
		# Invalid payload
		return response.status_code
	except stripe.error.SignatureVerificationError as e:
		# Invalid signature
		return response.status_code

	positive_events = ["customer.subscription.updated", "customer.subscription.resumed",
	                   "customer.subscription.created", "checkout.session.completed"]
	negative_events = ["customer.subscription.deleted", "customer.subscription.trial_will_end",
	                   "customer.subscription.paused"]

	if event['type'] in positive_events or event["type"] in negative_events:
		customer = stripe.Customer.retrieve(event.data.object.customer)
		user = await get_db_user(customer.email)
	else:
		return response.status_code
	try:
		if user:
			user.status = event.data.object.status
		else:
			user = User(plex_id=None, stripe_id=customer.id, email=customer.email, status=event.data.object.status)
		await update_db_user(user)
	except Exception as e:
		logger.info(e)
	if event['type'] == "checkout.session.completed":
		try:
			logger.info("Checkout completed")
			user.cr_id = event.data.object.client_reference_id
			await update_db_user(user)
			logger.info(f"User_cr: {user.cr_id}")
		except IndexError:
			logger.info("User-List is empty")
	if (user.status == "active" or user.status == "trialing") and event['type'] in positive_events:
		logger.info("User active! Updating User...")
		user = await update_plex_user(user)
		await update_db_user(user)
		if not user.plex_id:
			if not any(task.get_name() == f"get_plex_id_{user.email}" for task in asyncio.all_tasks()):
				asyncio.create_task(get_plex_id(user), name=f"get_plex_id_{user.email}")
		try:
			await bot.send_message(chat_id=user.cr_id, text=f"Dein Abo wurde erfolgreich aktualisiert.")
		except Exception as e:
			logger.info(e)

	elif (user.status == "canceled" or user.status == "unpaid" or user.status == "paused") and event['type'] in negative_events:
		logger.info("User not active! Updating User...")
		user = await update_plex_user(user)
		try:
			await bot.send_message(
				chat_id=user.cr_id, text=f"Dein Abo wurde gekündigt / ist abgelaufen. "
				                         f"Dein Plex Account wurde deaktiviert. Antworte mit /abo um ein neues Abo zu "
				                         f"erstellen."
			)
		except Exception as e:
			logger.info(e)
		await update_db_user(user)

	return response.status_code

if __name__ == "__main__":
	uvicorn.run(app, host=host, port=4242)
