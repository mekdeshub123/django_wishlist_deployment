import selenium
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from django.test import LiveServerTestCase

class TitleTest(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):#this method is called before tests in an an individual class are run.
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_title_shown_on_home_page(self):
        self.selenium.get(self.live_server_url)
        assert 'Travel Wishlist' in self.selenium.title

class AddEditPlacesTests(LiveServerTestCase):
    fixtures = ['test_places']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_add_new_place(self):
        self.selenium.get(self.live_server_url)#load home page
        input_name = self.selenium.find_element_by_id('id_name')#find input text box.
        input_name.send_keys('Denver')#enter place name
        add_button = self.selenium.find_element_by_id('add-new-place')#find the add button
        add_button.click()#click the add button

        #this test code wait for the server to processthe request and for page to reload and
        #  for new element to appear on page
        wait_for_denver = self.selenium.find_element_by_id('add-name-5')
        wait_for_denver.send_keys([5])

        #Assert places from test_places and new places on page
        assert 'Tokyo' in self.selenium.page_source
        assert 'New York' in self.selenium.page_source
        assert 'Denver' in self.selenium.page_source

    def test_mark_place_as_visited(self):
        self.selenium.get(self.live_server_url)#load home page
        visited_button = self.selenium.find_element_by_id('visited-button-2')
        visited_button.click()# click button

        wait = WebDriverWait(self.selenium, 3)
        ny_has_gone = wait.until(EC.invisibility_of_element_located((By.ID, 'place-name-2')))
        ny_has_gone.send_keys([2])
        self.assertIn('San Francisco', self.selenium.page_source) #assert San Fracisco is stil on page
        self.assertNotIn('New York', self.selenium.page_source) #but New York is not
        self.selenium.get(self.live_server_url + '/visited') #load visited page
        self.assertIn('New York', self.selenium.page_source) #New York now should be on visited page
        self.assertIn('Tokyo', self.selenium.page_source)
        self.assertIn('Moab', self.selenium.page_source)

class PageContentTests(LiveServerTestCase):
    fixtures = ['test_users','test_places']

    def seUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)
        self.browser.get(self.live_server_url + '/admin') # expect to be redirected to login page
        self.browser.find_element_by_id('id_username').send_keys('alice')
        self.browser.find_element_by_id('id_password').send_keys('qwertyuiop')
        self.browser.find_element_by_css_selector('input[type="submit"]').click()

    def tearDown(self):
        self.browser.quit()

    def test_get_home_page_list_of_places(self):
        self.browser.get(self.live_server_url)
        self.assertIn('San Francisco', self.browser.page_source)
        self.assertIn('New York', self.browser.page_source)
        self.assertNotIn('Tokyo', self.browser.page_source)
        self.assertNotIn('Moab', self.browser.page_source)

    def test_get_list_of_visited_places(self):
        self.browser.get(self.live_server_url + '/visited')
        self.assertIn('Tokyo', self.browser.page_source)
        self.assertIn('Moab', self.browser.page_source)

        self.assertNotIn('San Francisco', self.browser.page_source)
        self.assertNotIn('New York', self.browser.page_source)