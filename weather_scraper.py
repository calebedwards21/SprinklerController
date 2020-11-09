from bs4 import BeautifulSoup as bs
import requests
import argparse
import json


class Scraper:
    """
    This class will scrape google weather for local weather readings
    """

    def __init__(self):
        """
        Constructor for the scraper
        """
        self.USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
        self.LANGUAGE = "en-US,en;q=0.5"
        self.URL = "https://www.google.com/search?1r=lang_en&ie=UTF-8&q=weather"
        parser = argparse.ArgumentParser(description="Quick Script For Extracting Weather data using Google Weather")
        parser.add_argument("region", nargs="?", help="""Region to get weather for, must be available region.
                                Default is your current location determined by your IP Address""", default="")

        args = parser.parse_args()
        region = args.region
        self.URL += region


    def create_scraper(self):
        """
        Creates the scraper used to scrape google
        """
        session = requests.Session()
        session.headers['User-Agent'] = self.USER_AGENT
        session.headers['Accept-Language'] = self.LANGUAGE
        session.headers['Content-Language'] = self.LANGUAGE
        html = session.get(self.URL)
        self.soup = bs(html.text, "html.parser")


    def get_weather_now(self):
        """
        Scrapes Google Weather and returns results
        """
        result = {}
        ret = {}
        result['region'] = self.soup.find("div", attrs={"id": "wob_loc"}).text
        result['temp_now'] = self.soup.find("span", attrs={"id": "wob_tm"}).text
        result['dayhour'] = self.soup.find("div", attrs={"id": "wob_dts"}).text
        result['weather_now'] = self.soup.find("span", attrs={"id": "wob_dc"}).text
        result['precipitation'] = self.soup.find("span", attrs={"id": "wob_pp"}).text
        result['humidity'] = self.soup.find("span", attrs={"id": "wob_hm"}).text
        result['wind'] = self.soup.find("span", attrs={"id": "wob_ws"}).text
        ret['today'] = result
        return ret


    def get_weather_future(self):
        """
        Gets the weather data for the next few days
        """
        # Next few days of weather
        future = {}
        result = {}
        days = self.soup.find("div", attrs={"id": "wob_dp"})
        for idx,day in enumerate(days.findAll("div", attrs={"class": "wob_df"})):
            day_name = day.find("div", attrs={"class": "QrNVmd Z1VzSb"}).text
            weather = day.find("img", attrs={"class": "uW5pk"})
            max = day.find("div", attrs={"class": "vk_gy gNCp2e"})
            max_temp = max.find("span", attrs={"style": "display:inline"}).text
            min = day.find("div", attrs={"class": "QrNVmd ZXCv8e"})
            min_temp = min.find("span", attrs={"style": "display:inline"}).text
            future[day_name.lower()] = {"weather": weather['alt'], "weather_img": weather['src'], "max_temp": max_temp, "min_temp": min_temp}        
        result['future_weather'] = future
        return result


    def get_separate_future(self):
        """
        Returns all days as separate objects in a list
        """
        future_list = []
        future = {}
        days = self.soup.find("div", attrs={"id": "wob_dp"})
        for day in days.findAll("div", attrs={"class": "wob_df"}):
            day_name = day.find("div", attrs={"class": "QrNVmd Z1VzSb"}).text
            weather = day.find("img", attrs={"class": "uW5pk"})
            max = day.find("div", attrs={"class": "vk_gy gNCp2e"})
            max_temp = max.find("span", attrs={"style": "display:inline"}).text
            min = day.find("div", attrs={"class": "QrNVmd ZXCv8e"})
            min_temp = min.find("span", attrs={"style": "display:inline"}).text
            future[day_name.lower()] = {"day": day_name.lower(), "weather": weather['alt'], "weather_img": weather['src'], "max_temp": max_temp, "min_temp": min_temp}        
            future_list.append(future[day_name.lower()])
        return future_list


    def write_file(self):
        """
        Writes JSON to an output file
        """
        data = {}        
        
        today = self.get_weather_now()        
        data['today'] = today['today']

        future = self.get_weather_future()
        data['future'] = future['future_weather']        

        with open('weather.json', 'w') as outfile:
            json.dump(data, outfile)


    def write_separate(self):
        """
        Write all data in separate json
        """
        today = self.get_weather_now()
        with open('today.json', 'w') as outfile:
            json.dump(today, outfile)

        future = self.get_separate_future()
        for item in future:
            with open('%s.json' % item['day'], 'w') as outfile:
                json.dump(item, outfile)