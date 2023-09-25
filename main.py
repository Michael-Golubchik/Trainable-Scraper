# TrainingDatasetBuilder class for creating a training dataset from source data.
# The source data includes pages and XPath elements to click on, in order to open the desired pages.

from bs4 import BeautifulSoup
from lxml import etree
import pandas as pd


class TrainingDatasetBuilder:
    # In order this class to work you need to create folder 'data' in the project folder root.
    # And extract files and folders from page.zip there
    # Also, it is necessary to add pages.csv to folder 'data'

    # Arguments:
    # page_dir - the directory where bank website pages are located
    def __init__(self, data_dir):
        self.data_dir = data_dir

    # get_clickable loads clickable elements and save info to corresponding files
    def get_clickable(self) -> None:
        # Saving in pages_df info about loaded pages
        pages_df = pd.read_csv(f'{self.data_dir}/pages.csv')
        for page_i, page in pages_df.iterrows():
            # print(page['bank_i'])
            # Open loaded page to variable 'page_content'
            with open(f'{self.data_dir}/pages/{page["bank_i"]}/{page["url_id"]}', 'r', encoding='utf-8') as file:
                page_content = file.read()

            # Loadong allclickable elements in list: 'elements'
            soup = BeautifulSoup(page_content, "html.parser")
            dom = etree.HTML(str(soup))
            elements = dom.xpath('//a')
            for element in elements:
                print(element.text)
        # print(pages_df['url_id'].head(2))
        # with open(f'{self.data_dir}/pages/{self.bank_i}/{url_id}', 'r', encoding='utf-8') as file:
        #     text = file.read()
        # soup = BeautifulSoup(text, "html.parser")
        # dom = etree.HTML(str(soup))
        # elements = dom.xpath('//a[@href="/offices/"]')
        print
        # for element in elements:
        # print(element.text)
        # full_xpath = dom.getpath(element)
        # print(full_xpath)
        # print(text)


ds_builder = TrainingDatasetBuilder('data')
ds_builder.get_clickable()
