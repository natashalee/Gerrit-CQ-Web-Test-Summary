import sys
from lxml import html
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests

jobs = ["linux-rel", "mac-rel", "win7-rel", "win10_chromium_x64_rel_ng"]

class Render(str):
    def __init__(self, url):
        print("Loading page...")
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        # Try to start the browser driver given the url
        self.browser = webdriver.Chrome(chrome_options=options)
        try:
            self.browser.get(url)
            # Wait for the try jobs section to load onto the page
            WebDriverWait(self.browser, 50).until(EC.presence_of_all_elements_located((By.TAG_NAME, "cr-buildbucket-view")))
        except:
            self.browser.quit()
            print("failed to get url")
            sys.exit()

    def GetTryJobs(self):
        print("Getting try jobs...")
        # Try jobs section should have loaded when we initialized
        nav = self.browser.find_element_by_tag_name("cr-buildbucket-view")
        # Now we wait for specific job to show
        WebDriverWait(self.browser, 50).until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, "div.style-scope.cr-buildbucket-view"), "win7-rel"))
        try:
            # get the list of try job elements
            try_job_elements = nav.find_elements_by_css_selector("div.group.style-scope.cr-build-block")
        except:
            print("failed to find try job elements")
            self.browser.quit()
            sys.exit()

        tryjobs = []
        for element in try_job_elements:
            # We only want the release jobs
            if(element.text in jobs):
                print(element.text)
                element_link = element.find_element_by_css_selector("a.title.style-scope.cr-build-block")
                # save a list of the job name and their links to each try job
                tryjobs.append((element.text, element_link.get_attribute("href")))
        self.browser.quit()
        return tryjobs


def main():
    if(len(sys.argv) != 2):
        print("Usage: gerrit_scraper.py <gerrit_url>")
        sys.exit()
    url = sys.argv[1]
    r = Render(url)

    # r = Render("https://chromium-review.googlesource.com/c/chromium/src/+/1521819")
    try_jobs_list = r.GetTryJobs()
    # loop through the try jobs and visit their summary page 
    for tryjob in try_jobs_list:
        response = requests.get(tryjob[1])
        #tree = html.fromstring(response.text)
        
if __name__ == "__main__":
    main()
