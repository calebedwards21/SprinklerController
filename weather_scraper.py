from bs4 import BeautifulSoup as bs
import requests
import argparse


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
		result['region'] = self.soup.find("div", attrs={"id": "wob_loc"}).text
		result['temp_now'] = self.soup.find("span", attrs={"id": "wob_tm"}).text
		result['dayhour'] = self.soup.find("div", attrs={"id": "wob_dts"}).text
		result['weather_now'] = self.soup.find("span", attrs={"id": "wob_dc"}).text
		result['precipitation'] = self.soup.find("span", attrs={"id": "wob_pp"}).text
		result['humidity'] = self.soup.find("span", attrs={"id": "wob_hm"}).text
		result['wind'] = self.soup.find("span", attrs={"id": "wob_ws"}).text
		return result


	def get_weather_future(self):
		"""
		Gets the weather data for the next few days
		"""
		# Next few days of weather
		result = {}
		next_days = []
		days = self.soup.find("div", attrs={"id": "wob_dp"})
		for day in days.findAll("div", attrs={"class": "wob_df"}):
			day_name = day.find("div", attrs={"class": "vk_lgy"}).attrs['aria-label']
			weather = day.find("img").attrs["alt"]
			temp = day.findAll("span", {"class": "wob_t"})
			max_temp = temp[0].text
			min_temp = temp[2].text
			next_days.append({"name": day_name, "weather": weather, "max_temp": max_temp, "min_temp": min_temp})
		result['next_days'] = next_days
		return result
