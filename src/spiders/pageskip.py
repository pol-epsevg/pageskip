from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import re
from urllib.parse import parse_qsl

import scrapy
from scrapy.http import FormRequest
import trafilatura

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

    def parse_header(self, response):
        # Ticket headers look like this:
        # `0000001 - Ticket title | Requesting person | Creat: 01-01-2026 08:00`
        header_div = response.xpath(
            '//div[contains(@class, "tabletextTiquet")]')

        # `0000001 - Ticket title`
        subject = header_div.xpath('./a/text()').get(default='').strip()
        subject_match = re.split(r'\s+-\s+', subject, maxsplit=1)

        # `| Requesting person | Creat: 01-01-2026 08:00`
        header_text = " ".join(header_div.xpath('./text()').getall())
        date_match = re.search(r'Creat:\s*([\d-]{10}\s[\d:]{5})', header_text)

        ticket_number = None
        if len(subject_match) == 2:
            # `0000001`
            ticket_number = subject_match[0].strip()

            # `Ticket title`
            subject = subject_match[1].strip()

        if date_match:
            # `01-01-2026 08:00`
            parsed_date = datetime.strptime(
                date_match.group(1), "%d-%m-%Y %H:%M")
            creation_date = parsed_date.isoformat()
        else:
            creation_date = None

        return (subject, ticket_number, creation_date)

    def parse_ticket(self, response):
        (subject, ticket_number, creation_date) = parse_header(response)

        description_html = response.xpath(
            '//div[@class="caixa"][.//div[@class="Titol" and normalize-space(text())="Descripció"]]//div[contains(@class, "consultafck")]').getall()
        description_html = "".join(description_html)

        comments_html = "".join(response.xpath(
            '//div[contains(@class, "Comentari")]').getall())

        html = f"<html><body><main><article>{description_html}{comments_html}</article></main></body></html>"

        extracted_text = trafilatura.extract(
            html,
            include_comments=True,
            no_fallback=False
        )

        yield {
            'url': response.url,
            'number': ticket_number,
            'subject': subject,
            'creation_date': creation_date,
            'text': extracted_text,
        }
