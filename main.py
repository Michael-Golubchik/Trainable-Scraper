# TrainingDatasetBuilder class for creating a training dataset from source data.
# The source data includes pages and XPath elements to click on, in order to open the desired pages.

from bs4 import BeautifulSoup
from lxml import etree
import pandas as pd
import re


# get_elements - принимает:
# html_str - содержание страницы
# xpath_str - путь xpath к элементам
# возвращает элементы найденные на странице.
def get_elements(html_str: str, xpath_str: str):
    soup = BeautifulSoup(html_str, "html.parser")
    dom = etree.HTML(str(soup))
    return dom.xpath(xpath_str)


def get_anchor(element):
    anchor = (element.xpath('string()')
              .replace("\n", "")
              .strip())
    return anchor


# elements[0].xpath('string()').replace("\n", "")


class TrainingDatasetBuilder:
    # In order this class to work you need to create folder 'data' in the project folder root.
    # And extract files and folders from page.zip there
    # Also, it is necessary to add pages.csv to folder 'data'

    # Arguments:
    # page_dir - the directory where bank website pages are located
    def __init__(self, data_dir):
        self.data_dir = data_dir

    # get_clickable loads clickable elements from web page and save info to corresponding files
    # to train Scraper. Clickable elements will be marked: to click them or not.
    def get_clickable(self) -> None:
        # Saving in pages_df info about loaded pages
        pages_df = pd.read_csv(f'{self.data_dir}/pages.csv')
        # Добавим новую колонку с индексами родительских url и заполним нулями
        pages_df = pages_df.assign(parent_url_id=-1)
        # Датафрейм со всеми анкорами всех страниц всех банков
        anchor_df = pd.DataFrame(columns=['bank_i', 'url_id', 'parent_url_id', 'anchor', 'to_click'])

        # Iterate through banks
        for bank_i in pages_df['bank_i'].unique():
            print(bank_i)
            # bank_pages_df - contains only page for current bank_i
            bank_pages_df = pages_df[pages_df['bank_i'] == bank_i]
            # Создаем словарь page_dict, где ключи url страниц текущего банка.
            # А значение - содержание этих страниц
            page_dict = {}
            # anchor_dfs dictionary of dataframes to store anchors of clickable elements аnd 'to_click' them or not.
            anchor_dfs = {}
            # Iterate through pages of the current bank
            for page_i, page in bank_pages_df.iterrows():
                # print(page['bank_i'])
                # cur_url - url of the current page
                cur_url = page["url"]
                url_id = page["url_id"]
                print('url_id', url_id)

                anchor_dfs[url_id] = pd.DataFrame(columns=['anchor', 'to_click'])

                # Open loaded page to variable 'page_content'
                page_file_path = f'{self.data_dir}/pages/{bank_i}/{url_id}'
                with open(f'{page_file_path}', 'r', encoding='utf-8') as file:
                    page_content = file.read()

                page_dict[cur_url] = page_content

                # parent_url - parent url of the current page
                parent_url = str(page["parent_url"])
                if parent_url != "nan":
                    # Если есть родительская url
                    parent_url_id = bank_pages_df.loc[bank_pages_df['url'] == parent_url, 'url_id'].iloc[0]
                    print('parent_url_id', parent_url_id)
                    # Добавим информацию об id родительской url в датафрейм со страницами
                    pages_df.loc[pages_df['url_id'] == url_id, 'parent_url_id'] = int(parent_url_id)

                    # Выделяем последнюю команду на кликанье элемента
                    click_xpath = cur_url.replace(page["parent_url"], '')
                    # Убираем саму команду и оставляем от нее только путь xpath
                    match = re.search(r".+:(//.+)", click_xpath)
                    if match:
                        click_xpath = match.group(1)
                    else:
                        print('Ошибка. Не нашли xpath в элементе, который нужно кликать')
                        exit(1)

                    # Ищем элемент, который кликнули на родительской странице, чтобы открыть
                    # текущую страницу
                    elements = get_elements(page_dict[parent_url], click_xpath)
                    # Loading all clickable elements in list: 'elements'
                    if len(elements) > 0:
                        # Если нашли на странице с родительским url элемент, который кликали
                        anchor_to_click = get_anchor(elements[0])
                    else:
                        print('Ошибка. Не нашли на странице с родительским url элемент который кликали')
                        exit(1)

                    print('cur_url', cur_url)
                    print('click_xpath:', click_xpath)
                    print('anchor_to_click:', anchor_to_click)
                    print('parent_url:', parent_url)

                    # Отметим анкор в родительской url, которые нужно было кликать, чтобы попасть на
                    # текущую url
                    if ((anchor_dfs[parent_url_id]['anchor'] == anchor_to_click).sum()) == 0:
                        print('Ошибка. В анкорах родительской страницы не нашли того на который кликать')
                        exit(1)
                    else:
                        anchor_dfs[parent_url_id].loc[
                            anchor_dfs[parent_url_id]['anchor'] == anchor_to_click,
                            'to_click'] = True

                    # print(anchor_dfs[parent_url_id][anchor_dfs[parent_url_id]['to_click']])
                    # print(anchor_dfs.keys())

                elements = get_elements(page_content, '//a | //button')
                # Loading all clickable elements in list: 'elements'
                for element in elements:
                    # print(element.text)
                    # В cur_anchor заносим текст внутри найденной ссылки, но удаляем переносы строк
                    cur_anchor = get_anchor(element)
                    # We are adding next clickable element on page to the training data frame: anchor_dfs[cur_url]
                    anchor_dfs[url_id].loc[len(anchor_dfs[url_id].index)] = \
                        [cur_anchor, False]
                    # print('***', cur_anchor, '***')

            # Сохраняем все anchor всех страниц, когда уже найдено какие anchor кликать а какие нет
            for page_i, page in bank_pages_df.iterrows():
                url_id = page["url_id"]
                # anchor_file_path - путь к файлу с анкорами на странице
                anchor_file_path = f'{self.data_dir}/pages/{bank_i}/{url_id}_anchors.csv'
                # Save dataframe to store anchors to file
                anchor_dfs[url_id].to_csv(anchor_file_path, index=False)
                # Добавим информацию по анкорам в общий датафрейм anchor_df для всех сайтов банков
                temp_anchor_df = anchor_dfs[url_id].copy()
                temp_anchor_df = temp_anchor_df.assign(
                    bank_i=bank_i,
                    url_id=url_id,
                    parent_url_id=pages_df.loc[pages_df['url_id'] == url_id, 'parent_url_id'].iloc[0])
                anchor_df = pd.concat([anchor_df, temp_anchor_df],
                                      ignore_index=True)

            # After finishing with the bank, we delete the dataframes for it to restore memory
            del anchor_dfs
            del bank_pages_df
            del page_dict

        # Сохраняем информацию о загруженных страницах потому что добавили индекс родительской url
        pages_df.to_csv(f'{self.data_dir}/pages_out.csv', index=False)
        # Сохраняем информацию о всех анкорах на всех страницах всех банков
        anchor_df.to_csv(f'{self.data_dir}/anchor_out.csv', index=False)


ds_builder = TrainingDatasetBuilder('data')
ds_builder.get_clickable()
