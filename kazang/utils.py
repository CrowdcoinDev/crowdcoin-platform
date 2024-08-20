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
        """Initialize the Worker with WebDriver setup."""
        try:
            self.chrome_options = Options()

            if not DEBUG:
                # Configure Chrome options for headless mode
                self.chrome_options.add_argument("--headless")
                self.chrome_options.add_argument("--disable-gpu")
                self.chrome_options.add_argument("--no-sandbox")
                self.chrome_options.add_argument("--window-size=1920,1080")

            self.service = None
            self.driver = None
            self.soup = None
            self.base_url = 'https://store.kazang.net/'
            self.start()
        except Exception as e:
            logger.error("Failed to initialize WebDriver", exc_info=True)
            raise e

    def start(self):
        """Start the WebDriver and perform login."""
        try:
            # Initialize and start the WebDriver service
            self.service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
            self.login()  # Perform login
        except Exception as e:
            logger.error("Failed to start the Worker", exc_info=True)
            self.stop()  # Ensure cleanup in case of failure

    def stop(self):
        """Clean up WebDriver and its service."""
        try:
            if self.driver:
                self.driver.quit()  # Close all browser windows and end the session
            if self.service:
                self.service.stop()  # Stop the WebDriver service
        except Exception as e:
            logger.error("Failed to stop WebDriver service", exc_info=True)

    def navigate(self, page=''):
        """Navigate to the specified page."""
        try:
            url = self.base_url + page
            self.driver.get(url)
            self.driver.implicitly_wait(5)  # Wait for the page to load
            self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        except Exception as e:
            logger.error(f"Failed to navigate to {url}", exc_info=True)
            raise e

    def login(self):
        """Perform login."""
        try:
            self.navigate()  # Navigate to the base URL
            username_field = self.driver.find_element(By.ID, 'username')
            password_field = self.driver.find_element(By.ID, 'password')
            username_field.send_keys(settings.KAZANG_USERNAME)
            password_field.send_keys(settings.KAZANG_PASSWORD)
            password_field.send_keys(Keys.RETURN)
        except Exception as e:
            logger.error("Login failed", exc_info=True)
            raise e

    def logout(self):
        """Perform logout."""
        try:
            self.navigate('logout.php')
        except Exception as e:
            logger.error("Logout failed", exc_info=True)
            raise e

    def query_params(self):
        """Extract query parameters from the current URL."""
        try:
            parsed_url = urlparse(self.driver.current_url)
            return parse_qs(parsed_url.query)
        except Exception as e:
            logger.error("Failed to parse query parameters", exc_info=True)
            raise e

    @property
    def error_message(self):
        """Extract error message from query parameters."""
        query_params = self.query_params()
        return query_params.get('error', [False])[0]

    def __del__(self):
        """Ensure cleanup on object deletion."""
        self.stop()  # Clean up WebDriver service on deletion


class GenericVoucher(Worker):
    product_id = ''
    voucher_number_field_id = 'voucher_number'
    voucher_pin_field_id = 'voucher_pin'

    @property
    def page(self):
        """Construct the URL for the voucher page."""
        return f'vending.php?cat=Money_Send&product_id={self.product_id}'

    def redeem_voucher(self, voucher_number, voucher_pin):
        """Redeem a voucher."""
        try:
            self.navigate(self.page)
            voucher_number_field = self.driver.find_element(By.ID, self.voucher_number_field_id)
            voucher_pin_field = self.driver.find_element(By.ID, self.voucher_pin_field_id)
            
            # Submit the voucher
            voucher_number_field.send_keys(voucher_number)
            voucher_pin_field.send_keys(voucher_pin)
            voucher_pin_field.send_keys(Keys.RETURN)
            self.driver.implicitly_wait(5)  # Wait for the action to complete

            # Check for errors
            if self.error_message:
                raise Exception(self.error_message)
            else:
                return (200, "Voucher redeemed successfully")
        except Exception as e:
            logger.warning("Failed to redeem voucher", exc_info=True)
            return (500, str(e))


# Bank-specific implementations
class Standardbank(GenericVoucher):
    product_id = 'Std_Bank_Money_5686'
    voucher_pin_field_id = 'user_pin'


class Capitecbank(GenericVoucher):
    product_id = 'Capitec_Cash_Out_6451'


class Nedbank(GenericVoucher):
    product_id = 'Nedbank_Cashout_6137'


class Vodapay(GenericVoucher):
    product_id = 'VodaPay_Cash_Out_6065'
