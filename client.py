import time

# This module handles the login into LinkedIn


class LIClient(object):
    def __init__(self, driver, username, password, **kwargs):
        self.username = username
        self.password = password
        self.driver = driver

    def driver_quit(self):
        self.driver.quit()

    def login(self):
        """login to linkedin then wait 3 seconds for page to load"""
        time.sleep(3)
        # input login

        if self.username == 'exit' or self.password == 'exit':
            return

        elem = self.driver.find_element_by_id('username')
        elem.send_keys(self.username)
        # input password

        elem = self.driver.find_element_by_id('password')
        elem.send_keys(self.password)

        # submit login
        btn = '//div[@class="login__form_action_container "]'
        elem = self.driver.find_element_by_xpath(btn)
        elem.click()

        # Wait a few seconds for the page to load
        time.sleep(3)
        print('logged in successfully')
