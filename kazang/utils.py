import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from django.conf import settings

# Configure logging
logger = logging.getLogger(__name__)
DEBUG = settings.KAZANG_DEBUG

class Worker:
	def __init__(self):
		try:
			self.chrome_options = Options()

			if not DEBUG:
				# Configure Chrome options for headless mode
				self.chrome_options.add_argument("--headless")  # Run in headless mode
				self.chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
				self.chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
				self.chrome_options.add_argument("--window-size=1920,1080")  # Set window size

			self.service = None
			self.driver = None
			self.soup = None
			self.base_url = 'https://store.kazang.net/'
			self.start()
		except Exception as e:
			logger.error("Failed to initialize WebDriver", exc_info=True)
			raise e

	def navigate(self, page=''):
		try:
			url = self.base_url + page
			self.driver.get(url)
			self.driver.implicitly_wait(5)
			self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')
		except Exception as e:
			logger.error(f"Failed to navigate to {url}", exc_info=True)
			raise e

	def login(self):
		try:
			self.navigate()
			username_field = self.driver.find_element(By.ID, 'username')
			password_field = self.driver.find_element(By.ID, 'password')
			username_field.send_keys(settings.KAZANG_USERNAME)
			password_field.send_keys(settings.KAZANG_PASSWORD)
			password_field.send_keys(Keys.RETURN)
		except Exception as e:
			logger.error("Login failed", exc_info=True)
			raise e

	def logout(self):
		try:
			self.navigate('logout.php')
		except Exception as e:
			logger.error("Logout failed", exc_info=True)
			raise e


	def stop(self):
		"""Clean up WebDriver and its service."""
		try:
			if self.driver:
				self.driver.quit()  # Close all browser windows and end the session
			if self.service:
				self.service.stop()  # Stop the WebDriver service
		except Exception as e:
			logger.error("Failed to stop WebDriver service", exc_info=True)

	def start(self):
		try:
			self.service = Service(ChromeDriverManager().install())
			self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)			
			self.login()
		except Exception as e:
			logger.error("Failed to start the Worker", exc_info=True)
			self.stop()  # Ensure cleanup in case of failure

	def query_params(self):
		try:
			parsed_url = urlparse(self.driver.current_url)
			params = parse_qs(parsed_url.query)
			return params
		except Exception as e:
			logger.error("Failed to parse query parameters", exc_info=True)
			raise e

	@property
	def error_message(self):
		query_params = self.query_params()
		return query_params.get('error', [False])[0]

	def __del__(self):
		"""Ensure cleanup on object deletion."""
		self.stop()


class GenericVoucher(Worker):
	product_id = ''
	voucher_number_field_id = 'voucher_number'
	voucher_pin_field_id = 'voucher_pin'

	@property
	def page(self):
		return f'vending.php?cat=Money_Send&product_id={self.product_id}'

	def redeem_voucher(self, voucher_number, voucher_pin):
		try:
			self.navigate(self.page)
			voucher_number_field = self.driver.find_element(By.ID, self.voucher_number_field_id)
			voucher_pin_field = self.driver.find_element(By.ID, self.voucher_pin_field_id)
			
			# Submit form
			voucher_number_field.send_keys(voucher_number)
			voucher_pin_field.send_keys(voucher_pin)
			voucher_pin_field.send_keys(Keys.RETURN)
			self.driver.implicitly_wait(5)

			if self.error_message:
				raise Exception(self.error_message)
			else:
				return (200,"Voucher redeemed successfully")
		except Exception as e:

			logger.warning("Failed to redeem voucher", exc_info=True)
			return (500,e.args[0])

class Standardbank(GenericVoucher):
	product_id = 'Std_Bank_Money_5686'
	voucher_pin_field_id = 'user_pin'

class Capitecbank(GenericVoucher):
	product_id = 'Capitec_Cash_Out_6451'

class Nedbank(GenericVoucher):
	product_id = 'Nedbank_Cashout_6137'
