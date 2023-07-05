import scrapy
import json

class collect_player_info(scrapy.Spider):
    name = 'players_info'
    custom_settings = { 'CONCURRENT_REQUESTS': '1' }
    url=[]
    def __init__(self):
        players = [{'player_url':''}]
        try:
            with open('./dataset/players_urls.json') as f:
                players = json.load(f)
            player_count = 1

        except IOError:
            print("File not found")
        for i in players:
            self.url = self.url+[i['player_url']]


    def start_requests(self):
        for i in self.url:
            yield scrapy.Request(f'https://sofifa.com{i}',self.parse)

    def parse(self, response):
        def makedict(keys,values,isRemoveSpace=False):
            res={}
            if(len(values)==0):
                return keys
            for key in keys:
                for value in values:
                    if(isRemoveSpace):
                        res[key.replace(" ", "")] = value
                    else:
                        res[key] = value
                    values.remove(value)
                    break
            return res
        def makenumber(i):
            k=i
            for j in range(len(i)):
                if i[j].strip().isnumeric():
                    k[j]=int(i[j].strip())
                else:
                    k[j]=i[j]
            return k
        books={}
        books['id']=response.request.url.split('/')[4]
        books['name']=response.css(".bp3-card.player > .info > h1::text").get()
        books['primary_position']=response.css(".center > .grid > .col.col-4 > .pl > .ellipsis > span::text").get()
        books['positions']=response.css(".meta.ellipsis > span::text").getall()
        books['age'] = response.css(".table.table-hover.persist-area > .list > tr > .col-ae::text").get()
        info=response.css(".info > .meta.ellipsis::text").getall()[::-1][0]
        info=[i for i in info.split(' ') if i!='']
        books['age']=''.join([i for i in info[0] if (i>='0' and i<='9')])
        books['birth_date']=''.join([i for i in '/'.join([info[3],info[1],info[2]]) if ((i != ')') and (i != '(' ) and (i !=','))])
        books['height']=int(''.join([i for i in info[4] if (i>='0' and i<='9')]))
        books['weight'] =int( ''.join([i for i in info[5] if (i >= '0' and i <= '9')]))
        temp=response.xpath('//section[@class="card spacing"]/div/div/span/text()').extract()
        books['Overall Rating'],books['Potential']=[int(i) for i in temp if i.isnumeric()]
        books['Value'], books['Wage']=[i for i in response.xpath('//section[@class="card spacing"]/div/div/text()').extract() if i!=' ']

        curr_selectors=response.xpath('//div[@class="col col-12"]/div[@class="block-quarter"]/div/ul')
        curr_selectors=[scrapy.selector.Selector(text=i) for i in curr_selectors.css('.ellipsis').getall()]
        for i in curr_selectors:
            if (len(i.xpath('//label/text()').extract()) == 0):
                continue
            elif (i.xpath('//label/text()').extract()[0] == ' ' or i.xpath('//label/text()').extract()[0] == '\n'):
                continue
            elif (i.xpath('//label/text()').extract()[0] == 'Position' or i.xpath('//label/text()').extract()[0] == 'ID'):
                continue
            elif (i.xpath('//label/text()').extract()[0] == 'Preferred Foot'):
                books['Preferred Foot'] = i.xpath('//text()').extract()[1]
            elif (i.xpath('//text()').extract_first().strip().isnumeric()):
                books[i.xpath('//label/text()').extract()[0]] = int(i.xpath('//text()').extract_first().strip())
            else:
                books[i.xpath('//label/text()').extract()[0]] = i.xpath('//text()').extract()[::-1][0]

        keys=response.xpath('//div[@class="col col-12"]/div[@class="block-quarter"]/div/h5/a/text()').extract()
        values=[i for i in response.xpath('//div[@class="col col-12"]/div[@class="block-quarter"]/div/ul[@class="ellipsis pl"]/li/span/text()').extract() if i.isnumeric()]
        values = makenumber(values)
        books['teams']=makedict(keys,values)
        curr_selectors = response.xpath('//div[@class="col col-12"]/div[@class="block-quarter"]')
        curr_selectors = [scrapy.selector.Selector(text=i) for i in curr_selectors.css('.card').getall()]
        temp = []
        for i in curr_selectors:
            if (len(i.xpath('//h5/text()').extract()) == 0):
                continue
            elif (i.xpath('//h5/text()').extract()[0] == 'Profile'):
                continue
            elif (i.xpath('//h5/text()').extract()[0] == 'Player Specialities'):
                temp = i

            else:
                keys = i.xpath('//ul/li/span[@role="tooltip"]/text()').extract()
                values = i.css('.bp3-tag::text').getall()
                values = makenumber(values)
                books[i.xpath('//h5/text()').extract()[0].lower()] = makedict(keys, values, isRemoveSpace=True)
        try:
            books['player_traits'] = books.pop('traits')
        except:
            books['player_traits']=[]
        books['player_specialities'] = temp.css('ul > li ::text').getall()
        yield books