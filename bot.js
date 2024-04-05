const { Telegraf, Markup } = require('telegraf');
const { Builder, By, until } = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');
const axios = require('axios');
const fs = require('fs');

const CHROMEDRIVER_PATH = './chrome.exe';

const bot = new Telegraf('6879428578:AAHVQeIwfMBMQUvnoV6hwumA5wgvXS0Mrr8');
const options = new chrome.Options();
options.addArguments('--headless'); // Run Chrome in headless mode

const driver = new Builder()
    .forBrowser('chrome')
    .setChromeOptions(options)
    .build();

bot.start((ctx) => {
    ctx.reply('مرحبًا! يرجى إرسال رقم VIN الخاص بالسيارة.');
});

bot.on('text', async (ctx) => {
    const vin = ctx.message.text.trim();
    if (vin === '/start') {
        ctx.reply('يرجى إرسال رقم VIN الخاص بالسيارة.');
    } else {
        try {
            await driver.get('https://bimmervin.com/en');
            const vinInput = await driver.findElement(By.id('vin'));
            await vinInput.clear();
            await vinInput.sendKeys(vin);
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
            const infoLines = vehicleInfo.split('\n');
            const buttons = infoLines.map(line => {
                const parts = line.split('\t');
                if (parts.length === 2) {
                    return [Markup.button.callback(parts[1], parts[0])];
                } else {
                    return null;
                }
            }).filter(btn => btn !== null);

            // Send the buttons as an Inline Keyboard
            ctx.reply('T̷I̷R̷A̷B̷I̷M̷M̷E̷R̷', Markup.inlineKeyboard(buttons.flat()));
            
        } catch (error) {
            console.error('Error:', error.message);
            ctx.reply('حدث خطأ أثناء جلب معلومات السيارة. يرجى المحاولة مرة أخرى.');
        }
    }
});

bot.launch();

// Extract series information from vehicle info
function extractSeries(vehicleInfo) {
    const seriesMatch = vehicleInfo.match(/Series\s+(.*?)\n/);
    return seriesMatch ? seriesMatch[1] : '';
}

// Search Wikipedia for image related to the series
async function searchWikiForImage(wikipediaUrl) {
    try {
        const response = await axios.get(wikipediaUrl);
        const imageUrlMatch = response.data.match(/<meta property="og:image" content="(.*?)"/);
        return imageUrlMatch ? imageUrlMatch[1] : '';
    } catch (error) {
        console.error('Error searching for image:', error.message);
        return '';
    }
}
