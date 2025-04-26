from selenium.webdriver.common.by import By

class LOGIN_CONFIGS:

    LOGIN_CONFIG_FOR_YMGRAD = {
        "USERNAME_FIELD": (By.XPATH, "//input[@id='id_username']"),
        "PASSWORD_FIELD": (By.XPATH, "//input[@id='id_password']"),
        "LOGIN_BUTTON": (By.XPATH, "//input[@type='submit' and @value='Login']"),
        "LOGGED_IN_INDICATOR": (By.XPATH, "//*[contains(text(), 'Welcome') or contains(text(), 'Dashboard')]"),
        "LOGIN_TIMEOUT": 30
    }

    LOGIN_CONFIG_FOR_YOCKET = {
        "USERNAME_FIELD": (By.XPATH, "//input[@id='id_username']"),
        "PASSWORD_FIELD": (By.XPATH, "//input[@id='id_password']"),
        "LOGIN_BUTTON": (By.XPATH, "//input[@type='submit' and @value='Login']"),
        "LOGGED_IN_INDICATOR": (By.XPATH, "//*[contains(text(), 'Welcome') or contains(text(), 'Dashboard')]"),
        "LOGIN_TIMEOUT": 30
    }

    LOGIN_CONFIG_FOR_THEGRADCAFE = {
        "USERNAME_FIELD": (By.XPATH, "//input[@id='email']"),
        "PASSWORD_FIELD": (By.XPATH, "//input[@id='password']"),
        "LOGIN_BUTTON": (By.XPATH, "//button[@name='signin' and contains(text(), 'Sign in')]"),
        "LOGGED_IN_INDICATOR": (By.XPATH, "//*[contains(text(), 'Share Your Grad School Admission Results') or contains(text(), 'Dashboard')]"),
        "LOGIN_TIMEOUT": 30
    }