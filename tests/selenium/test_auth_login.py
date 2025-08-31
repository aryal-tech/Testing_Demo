import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://127.0.0.1:5000"

class AuthUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        opts = webdriver.ChromeOptions()
        # normal browser (no headless)
        opts.add_argument("--start-maximized")
        cls.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=opts
        )
        cls.driver.implicitly_wait(3)
    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
    def test_register_and_login_fixed_user(self):
        d = self.driver
        d.get(BASE_URL)
        # go to register page
        d.find_element(By.ID, "header-register").click()

        uname = "aryalsudesh7@gmail.com"
        pwd = "12345"

        # fill register form
        d.find_element(By.ID, "reg-username").clear()
        d.find_element(By.ID, "reg-username").send_keys(uname)
        d.find_element(By.ID, "reg-password").clear()
        d.find_element(By.ID, "reg-password").send_keys(pwd)
        d.find_element(By.ID, "register-submit").click()

        # assert logged in
        whoami_text = d.find_element(By.ID, "whoami").text.strip()
        self.assertIn(uname, whoami_text)

if __name__ == "__main__":
    unittest.main(verbosity=2)
