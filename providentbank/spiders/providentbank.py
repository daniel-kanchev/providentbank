import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from providentbank.items import Article


class ProvidentbankSpider(scrapy.Spider):
    name = 'providentbank'
    start_urls = ['https://www.provident.bank/press-releases']

    def parse(self, response):
        links = response.xpath('//a[@class="press-para-btn "]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="next"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//div[@class="detailpage-heading"]/text()').get()
        if title:
            title = title.strip()

        date = "".join(response.xpath('//h4[@class="insight-detail-month"]//text()').getall())
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="row clearfix insight-detail-content"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
