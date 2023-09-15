# TrainingDatasetBuilder class for creating a training dataset from source data.
# The source data includes pages and XPath elements to click on, in order to open the desired pages.

from bs4 import BeautifulSoup
from lxml import etree

class TrainingDatasetBuilder:
    # In order this class to work you need to create folder 'data' in the project folder root.
    # And extract files and folders from page.zip there
    # Also, it is necessary to add pages.csv to folder 'data'

    # Arguments:
    # page_dir - the directory where bank website pages are located
    # bank_i - bank index
    def __init__(self, page_dir, bank_i):
        self.page_dir = page_dir
        self.bank_i = bank_i

    # get_clickable loads clickable elements
    # url_id - url identifier, matches the name of the file with the page that is loaded when this url is opened
    def get_clickable(self, url_id) -> None:
        with open(f'{self.page_dir}/{self.bank_i}/{url_id}', 'r', encoding='utf-8') as file:
            text = file.read()
        print(text)


ds_builder = TrainingDatasetBuilder('data/pages', '263')
ds_builder.get_clickable(334)