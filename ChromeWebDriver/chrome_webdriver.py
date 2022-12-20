import os
import random
from time import sleep
# from selenium import webdriver
from seleniumwire import webdriver
from selenium.common import NoSuchElementException, InvalidArgumentException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.proxy import Proxy, ProxyType
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem


from Configuration.terminal import TerminalText


class ChromeWebDriver:
    """A Chrome Web Driver build on selenium, webdriver manager, random user agent and proxy.
    For create a new web driver object, need add one requirement argument = question"""

    def __init__(self, new_web_driver_options=None, use_proxy=True, debug=False):
        self.debug = debug
        self.driver = None
        self.add_new_webdriver_options = new_web_driver_options
        self.use_proxy = use_proxy

    def run(self):
        # USER_AGENT
        software_names = [SoftwareName.CHROME.value]
        operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
        # user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

        # Get Random User Agent String.
        # user_agent = user_agent_rotator.get_random_user_agent()
        user_agent = 'Mozilla/5.0 (Windows NT 8.1; WOW64) AppleWebKit/537.34 (KHTML, like Gecko) Chrome/36.0.2039.82 Safari/537.34'
        if self.debug:
            TerminalText(f'User Agent is {user_agent}').cyan()

        # proxy
        path_ip = os.getcwd()
        proxy_ip = open(f'{path_ip}/proxy_ip.txt', 'r')
        proxy_ip_list = proxy_ip.readlines()
        proxy_ip = random.choice(proxy_ip_list)
        proxy_random = str(proxy_ip + ':50100').replace('\n', '')
        proxy_options = {
            'proxy': {
                'https': f'https://{os.getenv("PROXY_USER")}:{os.getenv("PROXY_PASS")}@{proxy_random}'
            }
        }

        # OPTIONS
        options = webdriver.ChromeOptions()
        arguments = [
            '--enable-javascript',
            '--disable-blink-features=AutomationControlled',
            '--user-data-dir=config/google-chrome/Profile 3',
            f'user-agent={user_agent}',
        ]
        # add new argument
        if self.add_new_webdriver_options:
            for arg in self.add_new_webdriver_options:
                options.add_argument(arg)

        # add required arguments
        for argument in arguments:
            options.add_argument(argument)

        # CREATE_WEBDRIVER
        try:
            if self.debug:
                TerminalText('Create WebDriver with options, run behavior driver').header()
            self.driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=options,
                seleniumwire_options=proxy_options
            )
            if self.debug:
                version = self.driver.capabilities
                TerminalText(f'All Capabilities {version}').cyan()

                version = version.get('browserVersion')
                TerminalText('Driver chrome version --> ' + version).cyan()
            # sleep(2)
            # DriverLogic
        except Exception as E:
            text = '''Problem with create webdriver. \n
            Find in ==> chrome_webdriver.py ==> ChromeWebDriver ==> run'''
            TerminalText(text).report_to_slack(E)
            if self.debug:
                TerminalText('Something went wrong!').fail()

        return self.driver


class DriverLogic:
    """This class drive webdriver and initialize behavior"""

    def __init__(self, question_url, driver, debug):
        self.question = question_url
        self.driver = driver
        self.debug = debug
        self.class_name = 'xpc'
        self.page_list = list()

    def _search_and_click_elements(self):
        try:
            for iteration in range(1, 20):
                people_also_ask_elements = self.driver.find_elements(By.CLASS_NAME, value=self.class_name)

                if self.debug:
                    TerminalText(f'Iteration ==> {iteration}').warning()
                    TerminalText(f'Clicked on ==> {self.class_name}').warning()
                    TerminalText(f'People also ask ==> {people_also_ask_elements}').warning()

                for element in people_also_ask_elements:
                    element.click()
                # sleep(30)

                self.page_list.append(self.driver.page_source)
                self.driver.find_element(By.CLASS_NAME, value='f4J0H').click()
                # sleep(2)

        except NoSuchElementException as NSEE:
            text = '''Problem with search and click element. \n
            Find in ==> chrome_webdriver.py ==> DriverLogic ==> _search_and_click_elements'''
            TerminalText(text).report_to_slack(NSEE)
            if self.debug:
                TerminalText('Something went wrong!').fail()


    def _get_page_with_answer(self):
        try:
            self.driver.get(str(self.question))
        except InvalidArgumentException as IAE:
            text = '''Problem with get page. \n
            Find in ==> chrome_webdriver.py ==> DriverLogic ==> _get_page_with_answer'''
            TerminalText(text).report_to_slack(IAE)
            if self.debug:
                TerminalText('Something went wrong!').fail()
                TerminalText('''Error getting answer\n'
                      Please check your url and try again\n
                      Your question should look like a url\n
                      Find bugs in chrome_webdriver.py->DriverLogic->_get_page_with_answer\n''').fail()
                TerminalText(f'Exception: {IAE}').bold()

    def run(self):
        self._get_page_with_answer()
        self._search_and_click_elements()
        self.driver.quit()
        return self.page_list


def create_webdriver_and_get_page_with_answer(question=None, driver_options=None, debug=False):
    driver = ChromeWebDriver(new_web_driver_options=driver_options,
                             debug=debug).run()
    list_with_pages = DriverLogic(driver=driver, question_url=question, debug=debug).run()
    return list_with_pages
