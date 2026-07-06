const puppeteer = require('puppeteer');
const axios = require('axios');

const WEB_URL = process.env.WEB_URL || 'http://web:5000';

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function visit(url, username, password) {
    console.log(`[Bot] Visiting ${url}`);
    let browser;
    try {
        browser = await puppeteer.launch({
            executablePath: '/usr/bin/chromium',
            args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-xss-auditor']
        });
        const page = await browser.newPage();
        
        // 1. Login as admin
        await page.goto(`${WEB_URL}/`);
        await page.type('input[name="username"]', username);
        await page.type('input[name="password"]', password);
        await page.click('button[type="submit"]');
        await page.waitForNavigation();
        
        // 2. Visit the reported URL
        await page.goto(url, { waitUntil: 'networkidle0', timeout: 5000 });
        // wait a bit for scripts or RPO to load
        await sleep(3000);
        console.log(`[Bot] Visited ${url} successfully.`);
    } catch (err) {
        console.error(`[Bot] Error visiting ${url}:`, err.message);
    } finally {
        if (browser) await browser.close();
    }
}

async function main() {
    console.log("[Bot] Started.");
    while (true) {
        try {
            const res = await axios.get(`${WEB_URL}/api/get_reports`);
            const data = res.data;
            if (data && data.reports && data.reports.length > 0) {
                for (const url of data.reports) {
                    await visit(url, data.admin_username, data.admin_password);
                }
            }
        } catch (e) {
            // Ignore connection errors if web is starting up
        }
        await sleep(3000);
    }
}

main();
