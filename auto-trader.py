import time
import sys
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select

'''
Setup:
1. Download the Stable release chromedriver binary for your OS here: https://googlechromelabs.github.io/chrome-for-testing/
2. Unzip in the auto-trader directory and rename the unzipped directory to 'chromedriver'
3. Update the CHROME_DRIVER_DIRECTORY constant to the path to the chrome executable file

Tips:
1. Run this locally to avoid accidentally committing passwords: 'git update-index --assume-unchanged robinhood-logins.json'

TODOs:
1. Update this to not use Selenium because Robinhood can detect that you're a bot and then force you to pass CAPTCHA
   Also see if we can still use Selenium but avoid detection: https://stackoverflow.com/questions/53039551/selenium-webdriver-modifying-navigator-webdriver-flag-to-prevent-selenium-detec/53040904#53040904
'''

# constants
CHROME_DRIVER_DIRECTORY = r'C:/Users/wspur/Documents/python-programs/auto-trader/chromedriver/chromedriver.exe'
ROBINHOOD_LOGINS_FILE = 'robinhood-logins.json'

def read_command_line():
	command_line_arguments = sys.argv
	command_line_length = len(command_line_arguments)
	if (command_line_length != 7):
		raise ValueError(f'command line arguments length is {command_line_length}, but expects a length of 7')

	# TODO: extract this to a separate function for each value and add validation

	command_key_index = command_line_arguments.index('--command')
	command = command_line_arguments[command_key_index + 1]
	ticker_key_index = command_line_arguments.index('--ticker')
	ticker = command_line_arguments[ticker_key_index + 1]
	quantity_key_index = command_line_arguments.index('--quantity')
	quantity = command_line_arguments[quantity_key_index + 1]
	# authoritative_key_index = command_line_arguments.index('--authoritative')

	return command, ticker, quantity

# TODO: maybe make this a general config file instead of just logins
# TODO: add support for other brokerage websites
def read_logins():
	logins_json = {}
	with open(ROBINHOOD_LOGINS_FILE) as robinhood_logins_file:
		logins_json = json.load(robinhood_logins_file)

	return logins_json['logins']

def main():
	command, ticker, quantity = read_command_line()
	print(f'command: {command}, ticker: {ticker}, quantity: {quantity}')

	logins = read_logins()
	print(f'logins_json: {logins}')

	options = webdriver.ChromeOptions()
	options.add_argument('--disable-blink-features=AutomationControlled')
	options.add_experimental_option("excludeSwitches", ["enable-automation"])
	options.add_experimental_option('useAutomationExtension', False)
	driver = webdriver.Chrome(executable_path=CHROME_DRIVER_DIRECTORY, options=options)

	for login in logins:
		# Log in and get to the Robinhood homepage
		driver.get('https://robinhood.com/login')
		time.sleep(5)
		# TODO: extract this to a separate function
		email_text_box_element = driver.find_element(by=By.NAME, value='username')
		email_text_box_element.send_keys(login['email'])
		password_text_box_element = driver.find_element(by=By.ID, value='current-password')
		password_text_box_element.send_keys(login['password'])
		time.sleep(2)
		login_button_element = driver.find_element(by=By.XPATH, value='//*[@id="submitbutton"]/div/button')
		login_button_element.click()
		time.sleep(2)
		sms_verification_button_element = driver.find_element(by=By.XPATH, value='//*[@id="react_root"]/div[1]/div[2]/div/div/div/div[2]/div/div/div/div/button')
		if sms_verification_button_element is not None:
			sms_verification_button_element.click()
			time.sleep(2)
			sms_password = input('Please enter sms verification password: ')
			# TODO: add validation that the password is 6 characters and is a number
			sms_verification_text_box_element = driver.find_element(by=By.XPATH, value='//*[@id="react_root"]/div[3]/div/div[3]/div/div/section/div/div/div/form/div/div/input')
			sms_verification_text_box_element.send_keys(sms_password)
			sms_verification_continue_button_element = driver.find_element(by=By.XPATH, value='//*[@id="react_root"]/div[3]/div/div[3]/div/div/section/div/footer/div[1]/button')
			sms_verification_continue_button_element.click()
			time.sleep(5)

		# Get to ticker page and select 'buy' or 'sell'
		actions = ActionChains(driver)
		actions.send_keys('/') # select search bar
		actions.pause(1)
		actions.send_keys(ticker)
		actions.send_keys(Keys.DOWN) # TODO: This action isn't working
		actions.send_keys(Keys.ENTER)
		actions.pause(2)
		if command == 'buy':
			actions.send_keys('b')
		elif command == 'sell':
			actions.send_keys('s')
		else:
			raise ValueError(f'command {command} is invalid. Must be \'buy\' or \'sell\'')
		actions.perform()

		if command == 'buy':
			buy_in_dropdown_element = driver.find_element(by=By.XPATH, value='//*[@id="downshift-162-toggle-button"]')
			buy_in_select = Select(buy_in_dropdown_element)
			buy_in_select.select_by_visible_text('Shares')
		else:
			sell_in_dropdown_element = driver.find_element(by=By.XPATH, value='//*[@id="downshift-1861-toggle-button"]')
			if sell_in_dropdown_element is None:
				raise ValueError('\'sell\' command cannot be performed. There is probably no shares to sell')
			sell_in_select = Select(sell_in_dropdown_element)
			sell_in_select.select_by_visible_text('Shares')

		# execute trade
		shares_text_box_element = driver.find_element(by=By.XPATH, value='//*[@id="sdp-ticker-symbol-highlight"]/div[1]/form/div[2]/div/div[3]/div/div/div/div/input')
		shares_text_box_element.send_keys(quantity)
		shares_text_box_element.send_keys(Keys.ENTER)

		time.sleep(1000)
	
	driver.quit()

if __name__ == '__main__':
	main()
