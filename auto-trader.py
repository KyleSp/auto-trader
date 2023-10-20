import time
import sys
import json
from selenium import webdriver
from selenium.webdriver.common.by import By

'''
Setup:
1. Download the Stable release chromedriver binary for your OS here: https://googlechromelabs.github.io/chrome-for-testing/
2. Unzip in the auto-trader directory and rename the unzipped directory to 'chromedriver'
3. Update the CHROME_DRIVER_DIRECTORY constant to the path to the chrome executable file
'''

# constants
CHROME_DRIVER_DIRECTORY = r'C:/Users/wspur/Documents/python-programs/auto-trader/chromedriver/chromedriver.exe'
ROBINHOOD_LOGINS_FILE = 'robinhood-logins.json'

def read_command_line():
	command_line_arguments = sys.argv
	command_line_length = len(command_line_arguments)
	if (command_line_length != 7):
		raise ValueError(f'command line arguments length is {command_line_length}, but expects a length of 7')

	command_key_index = command_line_arguments.index('--command')
	command = command_line_arguments[command_key_index + 1]
	ticker_key_index = command_line_arguments.index('--ticker')
	ticker = command_line_arguments[ticker_key_index + 1]
	quantity_key_index = command_line_arguments.index('--quantity')
	quantity = command_line_arguments[quantity_key_index + 1]

	return command, ticker, quantity

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

	driver = webdriver.Chrome(executable_path=CHROME_DRIVER_DIRECTORY)

	for login in logins:
		driver.get('https://robinhood.com/login')
		time.sleep(5)
		email_text_box_element = driver.find_element(by=By.NAME, value='username')
		email_text_box_element.send_keys(login['email'])
		password_text_box_element = driver.find_element(by=By.ID, value='current-password')
		password_text_box_element.send_keys(login['password'])
		time.sleep(5)
		login_button_element = driver.find_element(by=By.XPATH, value='//*[@id="submitbutton"]/div/button')
		login_button_element.click()
		time.sleep(1000)
	
	# driver.quit()

if __name__ == '__main__':
	main()
