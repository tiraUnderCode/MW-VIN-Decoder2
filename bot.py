from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests

# Define your Telegram bot token
TOKEN = '6879428578:AAHVQeIwfMBMQUvnoV6hwumA5wgvXS0Mrr8'

# Set up Chrome WebDriver
chrome_options = Options()
chrome_options.add_argument('--headless')  # Run Chrome in headless mode
service = Service('./chromedriver')  # Replace with your path to chromedriver
driver = webdriver.Chrome(service=service, options=chrome_options)

# Start command handler
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='مرحبًا! يرجى إرسال رقم VIN الخاص بالسيارة أو رقم السيارة للبحث عن المعلومات.')

# Text message handler
def handle_text(update, context):
    input_text = update.message.text.strip()

    if input_text == '/start':
        context.bot.send_message(chat_id=update.effective_chat.id, text='يرجى إرسال رقم VIN الخاص بالسيارة أو رقم السيارة للبحث عن المعلومات.')
    elif len(input_text) == 17:
        try:
            driver.get('https://bimmervin.com/en')
            vin_input = driver.find_element(By.ID, 'vin')
            vin_input.clear()
            vin_input.send_keys(input_text)
            submit_button = driver.find_element(By.CSS_SELECTOR, 'button.btn.btn-primary')
            submit_button.click()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.col-sm-12.text-start')))
            vehicle_info_element = driver.find_element(By.CSS_SELECTOR, 'div.col-sm-12.text-start')
            vehicle_info = vehicle_info_element.text

            # Extract series information
            series = extract_series(vehicle_info)
            # Get Wikipedia URL for the series
            wikipedia_url = f'http://en.wikipedia.org/wiki/BMW_{series}'
            # Send the Wikipedia URL
            context.bot.send_message(chat_id=update.effective_chat.id, text=wikipedia_url)

            # Format the vehicle info with HTML
            formatted_info = f'<pre>{vehicle_info}</pre>'
            # Send the formatted info
            context.bot.send_message(chat_id=update.effective_chat.id, text=formatted_info)

            # Send the buttons as an Inline Keyboard
            context.bot.send_message(chat_id=update.effective_chat.id, text='T̷I̷R̷A̷B̷I̷M̷M̷E̷R̷')
        except Exception as e:
            print('Error:', str(e))
            context.bot.send_message(chat_id=update.effective_chat.id, text='حدث خطأ أثناء جلب معلومات السيارة. يرجى المحاولة مرة أخرى.')
    else:
        try:
            url = f'https://www.check-car.co.il/report/{input_text}/'
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract VIN number
            vin_number = soup.find(class_='table_col', attrs={'data-name': 'misgeret'}).find(class_='value').text.strip()
            # Extract car information
            car_info = soup.find(class_='add_fav')['data']

            # Compose reply message
            reply_message = f'بيانات السيارة:\n'
            reply_message += f'الموديل: {car_info["model"]}\n'
            reply_message += f'الماركة: {car_info["heb"]}\n'
            reply_message += f'السنة: {car_info["year"]}\n'
            reply_message += f'النوع: {car_info["type"]}\n'
            reply_message += f'رقم VIN: {vin_number}\n'
            reply_message += 'T̷I̷R̷A̷B̷I̷M̷M̷E̷R̷\n'

            # Send the reply message to the user
            context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)
        except Exception as e:
            context.bot.send_message(chat_id=update.effective_chat.id, text='حدث خطأ أثناء جلب المعلومات. يرجى التأكد من صحة رقم السيارة والمحاولة مرة أخرى.')

# Define the extract_series function
def extract_series(vehicle_info):
    series_match = re.search(r'Series\s+(.*?)\n', vehicle_info)
    return series_match.group(1) if series_match else ''

# Create the updater and pass in the bot's token
updater = Updater(token=TOKEN, use_context=True)

# Get the dispatcher to register handlers
dispatcher = updater.dispatcher

# Register handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

# Start the Bot
updater.start_polling()

# Run the bot until you press Ctrl-C
updater.idle()
