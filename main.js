const { Telegraf, Markup } = require('telegraf');
const { Builder, By, until } = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');
const axios = require('axios');
const cheerio = require('cheerio');
const TelegramBot = require('node-telegram-bot-api');

// تعريف توكن البوت
const token = '6679199332:AAHqGIBwKE1_9XmK6fIANglEZQ78yzvHn-Q';

// إنشاء بوت تليجرام جديد
const bot = new Telegraf(token);
const options = new chrome.Options();
options.addArguments('--headless'); // Run Chrome in headless mode

const driver = new Builder()
    .forBrowser('chrome')
    .setChromeOptions(options)
    .build();

bot.start((ctx) => {
    ctx.reply('مرحبًا! يرجى إرسال رقم VIN الخاص بالسيارة أو رقم السيارة للبحث عن المعلومات.');
});
bot.on('text', async (ctx) => {
    const input = ctx.message.text.trim();

    if (input === '/start') {
        ctx.reply('يرجى إرسال رقم VIN الخاص بالسيارة أو رقم السيارة للبحث عن المعلومات.');
    } else if (input.length === 17) {
        try {
            await driver.get('https://bimmervin.com/en');
            const vinInput = await driver.findElement(By.id('vin'));
            await vinInput.clear();
            await vinInput.sendKeys(input);
            const submitButton = await driver.findElement(By.css('button.btn.btn-primary'));
            await submitButton.click();
            await driver.wait(until.elementLocated(By.css('div.col-sm-12.text-start')), 10000);
            const vehicleInfoElement = await driver.findElement(By.css('div.col-sm-12.text-start'));
            const vehicleInfo = await vehicleInfoElement.getText();

            // Extract series information
            const series = extractSeries(vehicleInfo);
            // Get Wikipedia URL for the series
            const wikipediaUrl = `http://en.wikipedia.org/wiki/BMW_${series}`;
            // Send the Wikipedia URL
            ctx.reply(wikipediaUrl);

            // Format the vehicle info with HTML
            const formattedInfo = `<pre>${vehicleInfo}</pre>`;
            // Send the formatted info
            ctx.replyWithHTML(formattedInfo);

            // Split the vehicle info and display it as buttons
            
            // Send the buttons as an Inline Keyboard
            ctx.reply('T̷I̷R̷A̷B̷I̷M̷M̷E̷R̷');

        } catch (error) {
            console.error('Error:', error.message);
            ctx.reply('حدث خطأ أثناء جلب معلومات السيارة. يرجى المحاولة مرة أخرى.');
        }
    } else {
        try {
            // عنوان الصفحة المراد زيارتها مع رقم السيارة المعطاة
            const url = `https://www.check-car.co.il/report/${input}/`;

            // إرسال طلب HTTP لجلب صفحة الويب
            const response = await axios.get(url);

            // تحليل الصفحة باستخدام cheerio
            const $ = cheerio.load(response.data);

            // استخراج رقم VIN
            const vinNumber = $('.table_col[data-name="misgeret"] .value').text().trim();

            // استخراج البيانات المطلوبة من الصفحة
            const carInfo = $('.add_fav').data();

            // تجميع البيانات في رسالة الرد
            let replyMessage = `بيانات السيارة:\n`;
            replyMessage += `الموديل: ${carInfo.model}\n`;
            replyMessage += `الماركة: ${carInfo.heb}\n`;
            replyMessage += `السنة: ${carInfo.year}\n`;
            replyMessage += `النوع: ${carInfo.type}\n`;
            replyMessage += `رقم VIN: ${vinNumber}\n`;
               replyMessage += `T̷I̷R̷A̷B̷I̷M̷M̷E̷R̷\n`;
            // إرسال رسالة الرد إلى المستخدم
            ctx.reply(replyMessage);
        } catch (error) {
            // إرسال رسالة في حالة حدوث خطأ أثناء الاسترجاع
            ctx.reply('حدث خطأ أثناء جلب المعلومات. يرجى التأكد من صحة رقم السيارة والمحاولة مرة أخرى.');
        }
    }
});

bot.launch();

// Extract series information from vehicle info
function extractSeries(vehicleInfo) {
    const seriesMatch = vehicleInfo.match(/Series\s+(.*?)\n/);
    return seriesMatch ? seriesMatch[1] : '';
}
