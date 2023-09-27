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

        # Iterate through banks
        for bank_i in pages_df['bank_i'].unique():
            print(bank_i)
            # bank_pages_df - contains only page for current bank_i
            bank_pages_df = pages_df[pages_df['bank_i'] == bank_i]

            for page_i, page in bank_pages_df.iterrows():
                # print(page['bank_i'])
                # Open loaded page to variable 'page_content'
                page_file_path = f'{self.data_dir}/pages/{bank_i}/{page["url_id"]}'
                with open(f'{page_file_path}', 'r', encoding='utf-8') as file:
                    page_content = file.read()

                # cur_url - url of the current page
                cur_url = page["url"]
                # anchor_dfs dictionary of dataframes to store anchors of clickable elements аnd to_click them or not.
                anchor_dfs = {cur_url: pd.DataFrame(columns=['anchor', 'to_click'])}

                soup = BeautifulSoup(page_content, "html.parser")
                dom = etree.HTML(str(soup))
                elements = dom.xpath('//a')
                # Loading all clickable elements in list: 'elements'
                for element in elements:
                    # print(element.text)
                    anchor_dfs[cur_url].loc[len(anchor_dfs[cur_url].index)] =\
                        [element.text, False]
                # print(anchor_df)
                # print(page["url_id"])
                # Save dataframe to store anchors to file
                anchor_dfs[cur_url].to_csv(f'{page_file_path}_anchors.csv', index=False)
                del anchor_dfs
            del bank_pages_df
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
