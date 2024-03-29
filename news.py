import requests
from bs4 import BeautifulSoup
import random


class NewsScraper:
    '''
        @params:
            url : url to the site
            criteria : list of criteria used to filter the links
            nickname : name for the scraper
            debug : print connections or not

        @vars
            word_data : a string containing all paragraph data from all filtered links
            fil_links : the filtered links
            UAL : user agent list

        @description
            This class will take a URL and some filtering criteria to find links on a given site. It will then visit
            each link and append all paragraph data to a string. That string is then filtered through a whitelist of
            terms (this will hopefully be replaced by some ML that can determine more about the words). The final product
            is a counter variable called word_count

    '''

    def __init__(self,url,criteria,nickname='scraper',debug=False):
        #User Agent List
        UAL = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        ]

        self.word_data = ''
        self.nickname=nickname

        #generate random user agent
        randUserIndex = random.randint(0, len(UAL) - 1)
        instanceUser = UAL[randUserIndex]



        #make request to site
        mainRequest = requests.get(url,headers={'user-agent':instanceUser})

        #check status code
        if mainRequest.status_code == 200:
            #generate soup
            soup = BeautifulSoup(mainRequest.text,'html.parser')

            #class var for all links found
            links_ = []

            #use bs4 to find all links and then create an object with the link url and a list of the url split by /
            links = soup.find_all('a')
            for link in links:
                obj = {'url': link['href'], 'str': link['href'].split('/')}
                links_.append(obj)

            #Filter these links by the given criteria
            self.fil_links_ = []
            for item in links_:
                if all(words in item['str'] for words in criteria):
                    self.fil_links_.append(item['url'])


            #create session to make multiple requests in


            #check if there are any links to visit
            if self.fil_links_:
                sesh = requests.Session()

                #get each links page data
                for link in self.fil_links_:
                    tempReq = sesh.get(link,headers = {'user-agent': UAL[random.randint(0,len(UAL)-1)]})
                    if tempReq.status_code == 200:
                        if debug:
                            print('Connected to {}'.format(link))

                        tempSoup = BeautifulSoup(tempReq.text,'html.parser')

                        for item in tempSoup.find_all('p'):
                            if item.string is not None:
                                self.word_data += item.string

                sesh.close()
            else:
                print('no links filtered')
        else:
            print('Main Connection Failed')



class RedditInterface:
    def __init__(self, sub, listing, dataType='all', searchAmount=100, headNum=10):
        #
        self.sub = sub
        self.listing = listing
        self.dataType = dataType
        self.searchAmount = searchAmount
        self.headNum = headNum

        self.final = []

        CLIENT_ID = 'kmLjEwV4QdbwUg'
        SECRET_KEY = 'S02BLYQZfxR5CXgRRrzTFOlz2Ru_xg'

        auth = requests.auth.HTTPBasicAuth(CLIENT_ID, SECRET_KEY)

        login_data = {
            'grant_type': 'password',
            'username': 'DRIGONER',
            'password': '@Th3F0rc3'
        }

        headers = {'User-Agent': 'MyAPI/0.0.1'}

        res = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=login_data, headers=headers)

        TOKEN = res.json()['access_token']

        headers['Authorization'] = f'bearer {TOKEN}'

        res = requests.get(f'https://oauth.reddit.com/{self.sub}/{self.listing}', headers=headers,
                           params={'limit': f'{self.searchAmount}'})

        self.word_data = ''

        for post in res.json()['data']['children']:
            title = post['data']['title']
            selftext = post['data']['selftext']
            out_str = title + " " + selftext + " "
            self.word_data += out_str




