from collections import namedtuple

from selenium import webdriver

import config
from pages.exceptions import PageException


class OsfPage(object):

    default_url = None

    def __init__(self, *args, **kwargs):
        # If no driver was passed, make a new default driver
        if kwargs.get('driver'):
            self.driver = kwargs.get('driver')
        else:
            self.driver = self._make_driver()

        if not kwargs.get('driver'):
            # If no driver was passed, go to the url passed or the default
            self.driver.get(kwargs.get('url', self.default_url))
        elif kwargs.get('url'):
            # If a driver was passed, go to the URL if provided.
            self.driver.get(kwargs.get('url'))

        # Verify the page is what you expect it to be.
        if not self._verify_page():
            url = self.driver.current_url
            self.driver.close()
            raise PageException('Unexpected page structure: `{}`'.format(
                url
            ))

    @property
    def logged_in(self):
        """ True if a user is logged in; else, False

         This is determined by examining the header bar, looking for a "log out"
         link
        """
        return len(
            self.driver.find_elements_by_css_selector(
                'ul#navbar-icons a[href="/logout"]'
            )
        ) > 0

    def log_out(self):
        self.driver.find_element_by_css_selector(
            'ul#navbar-icons a[href="/logout"]'
        ).click()

    def _make_driver(self):
        driver = webdriver.Firefox()
        driver.implicitly_wait(5)
        return driver

    def _verify_page(self):
        return True

    def reload(self):
        self.driver.get(self.driver.current_url)

    def close(self):
        self.driver.quit()

    @property
    def user_dashboard(self):
        from pages.auth import UserDashboardPage
        self.driver.get('{}/dashboard'.format(config.osf_home))
        return UserDashboardPage(
            driver=self.driver
        )

    @property
    def user_login(self):
        from pages.auth import LoginPage
        self.driver.get('{}/account'.format(config.osf_home))
        return LoginPage(driver=self.driver)

    def node(self, node_id, parent_project=None):
        from pages.project import ProjectPage
        self.driver.get(
            '{}/project/{}/'.format(
                config.osf_home,
                '{}/node/{}'.format(
                    parent_project,
                    node_id
                ) if parent_project else node_id,
            )
        )

        return ProjectPage(driver=self.driver)


ApiKey = namedtuple('ApiKey', ('label','key'))