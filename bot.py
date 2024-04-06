from telegraf import Telegraf
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import axios
from bs4 import BeautifulSoup

# Define your Telegram bot token
token = '6879428578:AAHVQeIwfMBMQUvnoV6hwumA5wgvXS0Mrr8'

# Create a new Telegram bot
bot = Telegraf(token)

# Set up Chrome WebDriver
chrome_options = Options()
chrome_options.add_argument('--headless')  # Run Chrome in headless mode
service = Service('./chromedriver')  # Replace with your path to chromedriver
driver = webdriver.Chrome(service=service, options=chrome_options)

# Telegram bot start command handler
@bot.start
def start(ctx):
    ctx.reply('مرحبًا! يرجى إرسال رقم VIN الخاص بالسيارة أو رقم السيارة للبحث عن المعلومات.')

# Telegram bot text handler
@bot.on_text
async def handle_text(ctx):
    input_text = ctx.message.text.strip()

    if input_text == '/start':
        ctx.reply('يرجى إرسال رقم VIN الخاص بالسيارة أو رقم السيارة للبحث عن المعلومات.')
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
            ctx.reply(wikipedia_url)

            # Format the vehicle info with HTML
            formatted_info = f'<pre>{vehicle_info}</pre>'
            # Send the formatted info
            ctx.reply_with_html(formatted_info)

            # Send the buttons as an Inline Keyboard
            ctx.reply('T̷I̷R̷A̷B̷I̷M̷M̷E̷R̷')
        except Exception as e:
            print('Error:', str(e))
            ctx.reply('حدث خطأ أثناء جلب معلومات السيارة. يرجى المحاولة مرة أخرى.')
    else:
        try:
            url = f'https://www.check-car.co.il/report/{input_text}/'
            response = await axios.get(url)
            soup = BeautifulSoup(response.data, 'html.parser')

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
            ctx.reply(reply_message)
        except Exception as e:
            ctx.reply('حدث خطأ أثناء جلب المعلومات. يرجى التأكد من صحة رقم السيارة والمحاولة مرة أخرى.')

# Launch the Telegram bot
bot.launch()

# Extract series information from vehicle info
def extract_series(vehicle_info):
    series_match = re.search(r'Series\s+(.*?)\n', vehicle_info)
    return series_match.group(1) if series_match else ''

