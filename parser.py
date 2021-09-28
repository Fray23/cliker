import time
import datetime
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from settings import INSTAGRAM_LOGIN, INSTAGRAM_PASSWORD, FULL_PROFILE
from db import TaskGRUD, PostGRUD

chrome_option = Options()
chrome_option.add_argument('--user-data-dir={}'.format(FULL_PROFILE))

instagram_url = 'https://www.instagram.com/'


class InstagramApi:
    def __init__(self, driver):
        self.driver = driver

    def authenticate(self):

        self.driver.get(instagram_url)
        inbox_button = "//a[@href='/direct/inbox/']"
        try:
            self.driver.find_element(By.XPATH, inbox_button)
        except NoSuchElementException as e:
            wait = WebDriverWait(self.driver, 20)
            wait.until(EC.element_to_be_clickable((By.NAME, "username"))).send_keys(INSTAGRAM_LOGIN)
            wait.until(EC.element_to_be_clickable((By.NAME, "password"))).send_keys(INSTAGRAM_PASSWORD)
            wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@class="sqdOP  L3NKy   y3zKF     "]'))).click()

    def follow(self):
        time.sleep(2)
        try:
            follow_button = self.driver.find_element(By.XPATH, '//button[text()="Follow"]')
        except NoSuchElementException as e:
            logging.info('alredy follow to ' + self.driver.current_url)
        else:
            follow_button.click()
            logging.info('follow to ' + self.driver.current_url)

    def switch_to_profile(self, username_slug):
        profile_url = instagram_url + username_slug + '/'
        self.driver.get(profile_url)

    def get_post_like_count(self):
        like_count = None
        try:
            like_count_a_el = self.driver.find_element(By.XPATH, '//a[@class="zV_Nj"]')
            span_like_count_el = like_count_a_el.find_element(By.TAG_NAME, 'span')
            like_count = span_like_count_el.text
        except Exception as e:
            logging.warning('like count close')

        if like_count is not None:
            like_count = int(like_count.replace(',', ''))
        return like_count

    def get_post_datetime(self):
        time_el = self.driver.find_element(By.XPATH, '//time[@class="_1o9PC Nzb55"]')
        time_str = time_el.get_attribute('datetime')
        post_datetime = datetime.datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        return post_datetime

    def like_posts(self, n):
        last_post = self.driver.find_element(By.XPATH, '//div[@class="v1Nh3 kIKUG  _bz0w"]')
        last_post.click()
        wait = WebDriverWait(self.driver, 20)

        for _ in range(n):   
            time.sleep(2)

            buttons_section = wait.until(lambda d: d.find_element(By.XPATH, '//section[@class="ltpMr  Slqrh"]'))

            PostGRUD.create_post_info(
                post_url=self.driver.current_url,
                number_of_likes=self.get_post_like_count(),
                post_created_on=self.get_post_datetime()
                )

            like_button = buttons_section.find_element_by_class_name('wpO6b  ')
            like_button.click()

            try:
                next_button = self.driver.find_element(By.XPATH, '//a[text()="Next"]')
            except NoSuchElementException as e:
                logging.warning('posts are over or the design has changed')
                break
            else:
                next_button.click()

    def quit(self):
        self.driver.quit()


def main():
    driver = webdriver.Chrome(options=chrome_option)
    api = InstagramApi(driver=driver)

    while True:
        task = TaskGRUD.get_first_new_tasks()
        if task:
            task_id, profile, number_of_posts, hostname, created_on, time_taking_to_work, time_finish, status = task
            logging.info('parser start working: task_id {}, profile: {}, number_of_posts {}, created_on {}'.format(
                task_id, profile, number_of_posts, created_on
                ))

            TaskGRUD.update_to_take_to_work(task_id)

            try:
                api.authenticate()
                api.switch_to_profile(username_slug=profile)
                api.follow()
                api.like_posts(number_of_posts)
            except Exception as e:
                TaskGRUD.update_to_log_error(task_id)
                logging.error('task_id: {}'.format(task_id), e)
                api.quit()
                break
            else:
                TaskGRUD.update_to_finish(task_id)

        else:
            logging.info('no tasks parser is sleeping')
            time.sleep(5)


if __name__ == '__main__':
    main()