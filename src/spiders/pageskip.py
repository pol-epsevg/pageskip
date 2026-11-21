from concurrent.futures import ThreadPoolExecutor
from urllib.parse import parse_qsl

import scrapy
from scrapy.http import FormRequest

from playwright.sync_api import sync_playwright

LOGIN_URL = "https://gn6.upc.edu/epsevg/serveis"
TICKET_WEBSITE_URL = "https://gn6.upc.edu/tiquets/control/**"
START_URL = "https://gn6.upc.edu/tiquets/control/tiquetsEquipConsulta"

REQUEST_PAYLOAD = "tipusCerca=simple&VIEW_INDEX=1&VIEW_SIZE=30&nomesTancats=on&personaAssignada=11713&cercant=on"


def run_login():
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("Please authenticate on the browser window.")

        page.goto(LOGIN_URL)
        page.wait_for_url(TICKET_WEBSITE_URL, timeout=0)
        page.wait_for_load_state("networkidle")

        cookies = context.cookies()
        browser.close()
        return cookies


class Pageskip(scrapy.Spider):
    name = "pageskip_spider"
    allowed_domains = ["gn6.upc.edu"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with ThreadPoolExecutor(max_workers=1) as executor:
            self.auth_cookies = executor.submit(run_login).result()

    async def start(self):
        yield scrapy.Request(
            url=START_URL,
            method="POST",
            body=REQUEST_PAYLOAD,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            cookies=self.auth_cookies,
            meta={'cookiejar': 1},
            callback=self.parse,
            dont_filter=True
        )

    def parse(self, response):
        ticket_hrefs = set(response.xpath(
            '//a[contains(@href, "tiquetDetallDadesGenerals?requirementId=")]/@href').getall())

        for href in ticket_hrefs:
            yield response.follow(
                href,
                callback=self.parse_ticket,
                meta={'cookiejar': 1}
            )

        # The ticket list only includes a few listings, the crawler should follow the "Next tickets on the list" link
        next_page_href = response.xpath(
            '//a[normalize-space(text())="Següent"]/@href').get()
        if next_page_href:
            yield response.follow(
                next_page_href,
                callback=self.parse,
                meta={'cookiejar': 1}
            )

    def parse_ticket(self, response):
        yield {
            'url': response.url,
            'html_content': response.text
        }
