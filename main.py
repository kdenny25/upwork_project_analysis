from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import pandas as pd
import re


class uw_projects:
    def __init__(self, searchterm):
        self.searchterm = searchterm
        self.uw_search_url = 'https://www.upwork.com/services/search?q='

    def project_details(self, driver, path):
        # gather details from selected project
        project_title = driver.find_element('xpath', (path + '//h3[@class="project-tile__title mb-0 flex-1 project-tile__title-link"]/strong')).text
        project_price = float(driver.find_element('xpath', (path + '//p[@class="price m-0"]')).text.replace('From $', ''))
        project_rating = float(driver.find_element('xpath', (path + '//div[@title="Rating"]')).text[:4])
        project_num_ratings = int(driver.find_element('xpath', (path + '//div[@title="Rating"]/span')).text.replace('(', '').replace(')', ''))
        project_url = driver.find_element('xpath', (path + '//div[@class="project-tile__container tile flex-1 tile_flexible"]/a')).get_attribute('href')

        return [project_title, project_price, project_rating, project_num_ratings, project_url]

    def collect_data_from_projects(self):
        options = Options()
        options.headless = False
        driver = webdriver.Chrome('./driver/chromedriver.exe', options=options)

        # create url to search for term
        base_url = self.uw_search_url + self.searchterm
        # navigate to search results
        driver.get(base_url)

        # get number of projects
        num_projects = driver.find_element('xpath', '//strong[@data-qa="extended-results-title"]/h2').text
        num_projects = int(num_projects.replace('projects available', '').strip().replace(',', ''))

        print(num_projects)

        combined_details = {
            'title': [],
            'price': [],
            'rating': [],
            'num_ratings': [],
            'url': []}

        try:
            # loop through all projects
            # replace 12 with num_projects for full report.
            for idx in range(num_projects):
                # check if project number is divisable by 24
                # if it is then we click the load button and
                # recapture the container
                if idx % 24 == 0:
                    # click the button
                    driver.find_element('xpath', '//button[@aria-label="Load More Results"]').click()
                    print(idx)


                path = f'//div[@data-qa="search-results"]/div[{str(idx + 1)}]'

                # get project details
                project_det_list = self.project_details(driver, path)

                # add list items to the dictionary
                combined_details['title'].append(project_det_list[0])
                combined_details['price'].append(project_det_list[1])
                combined_details['rating'].append(project_det_list[2])
                combined_details['num_ratings'].append(project_det_list[3])
                combined_details['url'].append(project_det_list[4])
        except:
            print('An error has occured.')
            temp_df = pd.DataFrame(combined_details)
            temp_df.to_csv('./data/errored_report.csv')

        # create dataframe from dictionary
        projects_df = pd.DataFrame(combined_details)

        return projects_df


data_projects = uw_projects('data')
new_df = data_projects.collect_data_from_projects()
new_df.to_csv('./data/upwork_projects.csv')
print('complete')
