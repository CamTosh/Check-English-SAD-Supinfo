#!/usr/bin/python3
from selenium import webdriver
from bs4 import BeautifulSoup
import re
import json
import pendulum

import discord
import asyncio
import time

IDBOOSTER = ""
SUPINFO_PASSWORD = ""
DISCORD_SECRET = ""
DISCORD_CHANNEL_ID = ""

client = discord.Client()

# Get JSON slots on <script> tags
def check_available_slots(inner_html):
	bs = BeautifulSoup(inner_html, 'html.parser')
	scriptElements = bs.find_all('script')
	el = scriptElements[-2].text

	available = json.loads(re.search("(?<=var availabilities =).*?(?=;)", el).group())
	registeredAvailabilities = json.loads(re.search("(?<=var registeredAvailabilities =).*?(?=;)", el).group())

	slots = []
	
	for slot in available:
		if slot not in slots:
			slots.append(slot)

	for slot in registeredAvailabilities:
		if slot not in slots:
			slots.append(slot)

	return slots

# Format date
def get_date(slot):
	slot_time = pendulum.parse(slot, tz='Europe/Paris')
	return slot_time.format('dddd DD [of] MMMM YYYY HH:mm') + " - " + str(int(slot[-8:][0:2]) + 2) + ":00"

# Create discord message content
def create_message(slots):
	slotAvailable = len(slots)
	subject = "[English] " + str(slotAvailable) + " slot(s) available !"
	body = "@everyone They are " + str(slotAvailable) + " slot(s) available on http://english.sad.supinfo.com/\n\n"

	for slot_time in sorted(slots, key=lambda k: k['beginDate']):
		body += "The " + get_date(slot_time['beginDate']) + "\n"

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
			print("run")
			browser = get_html_site()

			next_month_button = browser.find_element_by_xpath("//*[contains(text(),'>')]")
			next_month_button.click()

			inner_html = browser.execute_script("return document.body.innerHTML")	
			slots = check_available_slots(inner_html)

			browser.quit()

			if len(slots):
				print("Found " + str(len(slots)) + " slot(s) available !")		
				msg = create_message(slots)

				if msg['available'] > 0:
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