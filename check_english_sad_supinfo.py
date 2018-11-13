#!/usr/bin/python3
from selenium import webdriver
import discord
import asyncio
import time

IDBOOSTER = ""
SUPINFO_PASSWORD = ""
BROWSER = "Chrome"
DISCORD_SECRET = ""
DISCORD_CHANNEL_ID = ""

client = discord.Client()

def check_available_slot(inner_html):
	if "<span style=\"color: green;\">" in inner_html:
		return True
	else:
		return False

def get_date(inner_html):
	if "<span style=\"color: green;\">" not in inner_html:
		return False

	# Get the Year
	i = inner_html.index("2018</strong>")
	i_end = i + 4

	# Get the month
	while inner_html[i] != ">":
		i -= 1

	# Get the month and year
	date = str(inner_html[i + 1:i_end])

	# Get the time
	i = inner_html.index("<span style=\"color: green;\">")
	slot_time = inner_html[i + 28: i + 30] + "h to " + inner_html[i + 37: i + 39] + "h"

	# Get the day number
	i = inner_html.index("<span style=\"color: green;\">")

	while inner_html[i:i + 18] != "<span class=\"day\">":
		i += 1

	# Add some text
	date += " from " + slot_time

	if inner_html[i + 19] == "<":
		return str(inner_html[i + 18] + " " + date)
	else:
		return str(inner_html[i + 18:i + 20] + " " + date)

def create_message(place_time):
	slotAvailable = len(place_time)

	subject = "[English - Check] " + str(slotAvailable) + " slot(s) available !"
	body = "@everyone They are " + str(slotAvailable) + " slot(s) available on http://english.sad.supinfo.com/\n\n"

	for slot_time in place_time:
		body += "The " + slot_time + "\n\n"

	return {
		'subject': subject,
		'body': body,
		'available': slotAvailable
	}

def get_html_site():
	options = webdriver.ChromeOptions()
	options.add_argument("--headless")
	browser = webdriver.Chrome(options=options)

	# Go to the English website
	browser.get("http://english.sad.supinfo.com/default/login")

	time.sleep(2)

	# Find and input the IDBOOSTER
	id_booster = browser.find_element_by_name("boosterId")
	id_booster.send_keys(IDBOOSTER)

	# Log in to the website
	button = browser.find_element_by_xpath("//input[@value='Connexion'][@type='submit']")
	button.click()

	time.sleep(2)

	# Find and input the IDBOOSTER
	id_booster = browser.find_element_by_name("Id")
	id_booster.send_keys(IDBOOSTER)

	# Log in to the SSO
	password = browser.find_element_by_id("Password")
	password.send_keys(SUPINFO_PASSWORD)

	button = browser.find_element_by_xpath("//button[@name='button'][@value='login']")
	button.click()

	time.sleep(2)

	# Go to the calendar tab
	browser.get("http://english.sad.supinfo.com/student/calendar")

	time.sleep(2)

	return browser


@client.event
async def on_message(message):
	if message.author == client.user:
		return

	if message.content.startswith('!english init'):
		while True:
			print('Run')
			browser = get_html_site()

			slot_time = []

			# Check for the current month and the 4 next ones
			for i in range(5):
				if i != 0:
					next_month_button = browser.find_element_by_xpath("//*[contains(text(),'>')]")
					next_month_button.click()

				inner_html = browser.execute_script("return document.body.innerHTML")

				if check_available_slot(inner_html):
					slot_time.append(get_date(inner_html))

			browser.quit()

			if not slot_time:
				print("Found " + str(len(slot_time)) + " slot(s) available !")
				msg = create_message(slot_time)
				print(str(msg))

				if msg['slotAvailable'] > 0:
					embed = discord.Embed(title=msg['subject'], colour=discord.Colour(0x8aa3cc), description=msg['body'])
					channel = client.get_channel(DISCORD_CHANNEL_ID)
					await client.send_message(channel, embed=embed)
			else:
				print("Nothing found ...")
			time.sleep(60 * 4)


@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')


client.run(DISCORD_SECRET)