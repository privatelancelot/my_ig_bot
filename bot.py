from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementClickInterceptedException
from utility_methods.utility_methods import *
import os
import time
import random

class InstagramBot:

    def __init__(self, tags):
        """
        Initializes an instance of the InstagramBot class.
        
        Call the login method to authenticate a user with IG.

        Args:
            tags:list: list of tags to browse

        Attributes:
            driver:Selenium.webdriver.Chrome: The Chromedriver that is used to control and automate browser actions
        """
        self.driver = webdriver.Chrome(config['ENVIRONMENT']['CHROMEDRIVER_PATH'])
        self.username = config['IG_AUTH']['USERNAME']
        self.password = config['IG_AUTH']['PASSWORD']
        self.get_tag_url = config['IG_URLS']['SEARCH_TAGS']
        self.base_url = 'https://www.instagram.com/'
        self.start_time = time.time()
        self.work_time_minutes = random.randint(20,30)
        self.pause_minutes_min = 120
        self.pause_minutes_max = 260        
        self.like_percentage_latest_post = 70
        self.like_percentage = 60
        self.user_followed = False
        self.likes = 0
        self.likes_per_user = 0
        self.follows = 0
        self.unfollows = 0
        self.comments = 0
        self.login()

        # self.unfollow_users()

        while True:
            for tag in tags:
                #self.browse_non_top_posts(tag)
                self.like_non_top_posts(tag)
                #sleep time could be randomized too
                time.sleep(4)

    # BASIC FUNCTIONALITIES

    def login(self):
        self.driver.get(self.base_url)
        time.sleep(2) # Wait for elements to be found
        self.driver.find_element_by_name('username').send_keys(self.username)
        self.driver.find_element_by_name('password').send_keys(self.password)
        time.sleep(1) # In case login button xpath highlight change takes time
        self.driver.find_element_by_xpath('/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div[4]/button/div').click()
        time.sleep(1)
        self.dont_save_login_info()

    def nav_user(self, username, print):
        """
        username:str
        print:boolean

        Navigates to user's page and prints statistics
        """
        time.sleep(random.randint(1,4))
        self.driver.get(self.base_url + username)
        if print:
            self.print_statistics()
        time.sleep(random.randint(1,2))
        

    def follow_user(self, username):
        """
        username:str

        Navigate to user's page to follow
        """
        self.nav_user(username, True)
        time.sleep(random.randint(1,2))
        follow_button = self.driver.find_elements_by_xpath("//button[contains(text(), 'Follow')]")[0]
        follow_button.click()
        msg = 'Following ', username
        logger.debug(str(msg))
        self.follows += 1

    def unfollow_user(self, username):
        """
        username:str

        Navigate to user's page to unfollow
        """
        self.nav_user(username, False)
        time.sleep(1)
        self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/div[1]/div[2]/span/span[1]/button').click()
        time.sleep(1)
        self.driver.find_elements_by_xpath("//button[contains(text(), 'Unfollow')]")[0].click()
        self.check_if_problem()
        msg = 'Unfollowed ', username
        logger.debug(str(msg))
        self.unfollows += 1

    def dont_save_login_info(self):
        """
        Answer no to IG's notification to save login info when logging in
        """
        time.sleep(random.randint(1,4))
        try:
            not_now_button = self.driver.find_elements_by_xpath("//button[contains(text(), 'Not Now')]")[0]
        except IndexError:
            return
        not_now_button.click()

    def search_tag(self, tag):
        """
        tag:str

        Search posts according to tag
        """
        time.sleep(random.randint(1,3))
        self.driver.get(self.get_tag_url.format(tag))

    def print_statistics(self):
        """
        Print bot statistics
        """
        msg = 'Overall Likes: ', self.likes, ' || Follows: ', self.follows, ' || Comments: ', self.comments,' || Elapsed time in minutes: ', round(self.time_elapsed_seconds()/60,1)
        logger.debug(str(msg))

    def comment(self):
        """
        Comment on an open post (card)
        """
        time.sleep(1)
        comment_input = self.driver.find_element_by_xpath('/html/body/div[4]/div[2]/div/article/div[2]/section[3]/div/form/textarea').click()
        time.sleep(1)
        comment_input = self.driver.find_element_by_xpath('/html/body/div[4]/div[2]/div/article/div[2]/section[3]/div/form/textarea').send_keys('Nice style! :)')
        time.sleep(1)
        self.driver.find_element_by_xpath('/html/body/div[4]/div[2]/div/article/div[2]/section[3]/div/form/button').click()

    def like(self):
        """
        Like an open post (card)
        """
        time.sleep(1)
        try:
            self.driver.find_elements_by_class_name('wpO6b')[1].click()
        except IndexError:
            time.sleep(random.randint(1,2))
            return
        time.sleep(random.randint(1,2))
        self.likes += 1
        self.likes_per_user += 1
        self.check_if_problem()

    def check_if_problem(self):
        """
        Check if ig is detecting a problem (due to excessive browsing)
        """
        time.sleep(random.randint(1,2))
        try:
            btn_problem = self.driver.find_elements_by_xpath("//button[contains(text(), 'Report a Problem')]")[0]
        except IndexError:
            return
        logger.debug('IG is onto us! Sleeping for an hour!')
        btn_problem.click()
        time.sleep(60*60)

    def check_time(self):
        """
        Check if time elapsed is more than set work time and takes a break if necessary
        """
        if self.time_elapsed_minutes() >= self.work_time_minutes:
            self.take_a_break()

    def take_a_break(self):
        """
        Go to sleep for a defined time and log when is time to wake up
        """
        logger.debug('Work time is over.. Bye!')
        time_sleep = random.randint(60*self.pause_minutes_min,60*self.pause_minutes_max)
        time_waking = time.time() + (time_sleep*60)
        time_waking_readable = time.strftime("%H:%M:%S", time.localtime(time_waking))
        msg = 'Sleeping for', round(time_sleep/60,0), 'mins.. Waking at ', time_waking_readable
        logger.debug(str(msg))
        time.sleep(time_sleep)
        self.start_time = time.time()

    def time_elapsed_seconds(self):
        elapsed_time = int(time.time() - self.start_time)
        return elapsed_time

    def time_elapsed_minutes(self):
        return int(self.time_elapsed_seconds()/60)

    def scroll_down_random(self):
        """
        Scroll down a page for a random amount
        """
        time.sleep(random.randint(1,2))
        scrollAmount = random.randint(1,9)

        if scrollAmount == 1:
            self.driver.execute_script("window.scrollBy({ top: 842, left: 0, behavior: 'smooth' });")
        elif scrollAmount == 2:
            self.driver.execute_script("window.scrollBy({ top: 1129, left: 0, behavior: 'smooth' });")
        elif scrollAmount == 3:
            self.driver.execute_script("window.scrollBy({ top: 1943, left: 0, behavior: 'smooth' });")
        elif scrollAmount == 4:
            self.driver.execute_script("window.scrollBy({ top: 2641, left: 0, behavior: 'smooth' });")
        elif scrollAmount == 5:
            self.driver.execute_script("window.scrollBy({ top: 2012, left: 0, behavior: 'smooth' });")
        elif scrollAmount == 6:
            self.driver.execute_script("window.scrollBy({ top: 3699, left: 0, behavior: 'smooth' });")
        elif scrollAmount == 7:
            self.driver.execute_script("window.scrollBy({ top: 541, left: 0, behavior: 'smooth' });")
        elif scrollAmount == 8:
            self.driver.execute_script("window.scrollBy({ top: 496, left: 0, behavior: 'smooth' });")
        elif scrollAmount == 9:
            self.driver.execute_script("window.scrollBy({ top: 1541, left: 0, behavior: 'smooth' });")
    
    def scroll_down(self, amount):
        """
        amount:int

        Scroll down the amount that is in amount-param
        """
        time.sleep(1)
        script = "window.scrollBy({ top:" + str(amount) + ", left: 0, behavior: 'smooth' });"
        self.driver.execute_script(script)

    def scroll_user_page(self):
        """
        Scroll down a (user) page to see rows 1-4 (Unreliable due to page length dependency on profile description)
        """
        time.sleep(1)
        self.driver.execute_script("window.scrollBy({ top: 650, left: 0, behavior: 'smooth' });")

    def scroll_to_non_top(self):
        """
        Scroll down a search result page to see most recent rows 1-5
        """
        time.sleep(1)
        self.driver.execute_script("window.scrollBy({ top: 1500, left: 0, behavior: 'smooth' });")

    def scroll_top(self):
        """
        Scroll back to the top of the page
        """
        time.sleep(random.randint(1,2))
        self.driver.execute_script("window.scrollTo({ top: 0, left: 0, behavior: 'smooth' });")

    def close_card(self):
        """
        Close an open card/post if open
        """
        time.sleep(2)
        try:
            self.driver.find_elements_by_xpath('/html/body/div[4]/div[3]/button')[0].click()
        except IndexError:
            logger.debug('Could not close Card')

    # HIGHER LEVEL FUNCTIONALITIES

    def browse_non_top_posts(self, tag):
        """
        tag:str

        Browse through (non-top) posts (in tag search result which has been scrolled down)
        """
        time.sleep(random.randint(1,2)) 
        rowMax = 5
        colMax = 4   
        for row in range(1, rowMax):
            for column in range(1, colMax):
                time.sleep(1)
                self.search_tag(tag)
                self.scroll_to_non_top()
                time.sleep(1)
                self.browse_specific_non_top_post(rowMax - row, colMax - column)
                
    def browse_specific_non_top_post(self, row, column):
        """
        row:int
        column:int

        Select a specific non-top post according to row and column then navigate to user's page to browse user posts
        """
        time.sleep(random.randint(1,2))
        try:
            post = self.driver.find_elements_by_xpath('/html/body/div[1]/section/main/article/div[2]/div/div[{}]/div[{}]/a/div/div[2]'.format(row,column))[0].click()
        except (IndexError, ElementClickInterceptedException) as e:
            logger.debug('browse_specific_non_top_post F')
            return
        time.sleep(1)
        try:
            username = self.driver.find_element_by_xpath('/html/body/div[4]/div[2]/div/article/header/div[2]/div[1]/div[1]/a/h1')
        except NoSuchElementException:
            username = self.driver.find_element_by_xpath('/html/body/div[4]/div[2]/div/article/header/div[2]/div[1]/div[1]/a')
        time.sleep(random.randint(1, 2))
        self.browse_all_user_posts(username.text)

    def browse_top_posts(self, row, column):
        """
        row:int
        column:int

        Select a specific top post according to row and column then navigate to user's page to browse user posts
        """
        time.sleep(2)
        try:
            post = self.driver.find_elements_by_xpath('/html/body/div[1]/section/main/article/div[1]/div/div/div[{}]/div[{}]/a/div/div[2]'.format(row,column))[0].click()
        except IndexError:
            logger.debug('F')
        time.sleep(1)
        try:
            username = self.driver.find_element_by_xpath('/html/body/div[4]/div[2]/div/article/header/div[2]/div[1]/div[1]/a/h1')
        except NoSuchElementException:
            username = self.driver.find_element_by_xpath('/html/body/div[4]/div[2]/div/article/header/div[2]/div[1]/div[1]/a')
        time.sleep(random.randint(1, 2))
        self.browse_all_user_posts(username.text)

    def browse_all_top_posts(self, tag):
        """
        tag:str

        Search a tag and browse top posts
        """
        for row in range(1, 4):
            for column in range(1, 4):
                time.sleep(1)
                self.search_tag(tag)
                time.sleep(1)
                self.browse_top_posts(row, column)

    def like_non_top_posts(self, tag):
        """
        tag:str

        Browse through (non-top) posts (in tag search result which has been scrolled down)
        and like posts depending on row- and colMax
        """
        time.sleep(random.randint(1,2))
        self.dont_save_login_info()
        time.sleep(random.randint(1,2))
        self.dont_save_login_info()
        time.sleep(random.randint(1,2))
        rowMax = 5
        colMax = 4
        self.search_tag(tag)
        time.sleep(2)
        self.scroll_to_non_top()
        for row in range(1, rowMax):
            for column in range(1, colMax):
                time.sleep(2)
                try:
                    post = self.driver.find_elements_by_xpath('/html/body/div[1]/section/main/article/div[2]/div/div[{}]/div[{}]/a/div/div[2]'.format(row,column))[0].click()
                except IndexError:
                    logger.debug('F')
                time.sleep(2)
                self.like()
                self.close_card()
                time.sleep(1)
                self.print_statistics()
                self.check_time()
                


    def browse_user_post(self, index, likeThreshold, commentThreshold):
        """
        index:int
        likeThreshold:int
        commentThreshold:int

        Browse a user post according to index and liking/commenting depending if randomizer meets parameter thresholds
        """
        time.sleep(random.randint(1,3))
        likePercentage = random.randint(0,100)
        commentPercentage = random.randint(0,100)
        try: 
            self.driver.find_elements_by_class_name('_9AhH0')[index].click()
        except (IndexError, ElementClickInterceptedException) as e:
            # fixing this later if occurs again
            logger.debug('browse_user_post: Post not found..')

        if likePercentage <= likeThreshold:
            time.sleep(random.randint(1,3))
            try:
                self.like()
            except IndexError:
                logger.debug('Post not open for a like')
                time.sleep(random.randint(1,3))

    def browse_all_user_posts(self, username):
        """
        username:str

        Browse a user's posts with different settable thresholds for likes/comments for latest post and randomly selected posts
        Follow if followThreshold is met (randomized between 2 and 3)
        """
        time.sleep(random.randint(1,3))
        followThreshold = random.randint(2,3)
        roundMax = random.randint(1,4)
        self.likes_per_user = 0
        self.user_followed = False
        self.browse_user_latest_post(username)
        for x in range(1,roundMax):
            random_index = random.randint(2,6)
            self.nav_user(username, True)
            time.sleep(1)
            self.scroll_down_random()
            time.sleep(1)
            self.browse_user_post(random_index,self.like_percentage,0)
            time.sleep(1)
            if self.likes_per_user >= followThreshold and self.user_followed != True:
                self.follow_user(username)
                self.user_followed = True
            if self.time_elapsed_minutes() >= self.work_time_minutes:
                self.take_a_break()

    def browse_user_latest_post(self, username):
        """
        username:str
        """
        time.sleep(random.randint(1,2))
        self.nav_user(username, True)
        time.sleep(random.randint(1,2))
        self.browse_user_post(0,self.like_percentage_latest_post,0)

    def unfollow_users(self):
        with open('unfollow_list.txt') as f:
            users = f.readlines()
        for user in users:
            try:
                self.unfollow_user(user.rstrip())
            except NoSuchElementException:
                logger.debug('Cannot unfollow as button could not be found.')
        logger.debug('End of unfollow list')

if __name__ == '__main__':
    config_file_path = './config.ini'
    config = init_config(config_file_path)
    logger_file_path = './bot.log'
    logger = get_logger(logger_file_path)

    ig_bot = InstagramBot(['photography','photographer','photographylovers'])