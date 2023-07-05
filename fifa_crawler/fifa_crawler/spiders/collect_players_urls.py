
import scrapy
class MySpider(scrapy.Spider):
    name = 'players_urls'
    custom_settings = { 'CONCURRENT_REQUESTS': '1' }
    def start_requests(self):
        for i in range(int(720/60)):
            yield scrapy.Request(f'https://sofifa.com/players?col=oa&sort=desc&offset={i*60}',self.parse,priority=i)

    def parse(self, response):
        link_player= response.css(".table.table-hover.persist-area > .list > tr > .col-name > a::attr(href)").getall()
        link_player=[i for i in link_player if '?' not in i]
        for i in link_player:
          yield dict.fromkeys(['player_url'],'/'.join(i.split('/')[:3]))