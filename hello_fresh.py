import recipe
import requests
import unicodedata
import pandas as pd
from bs4 import BeautifulSoup

__base_url = 'https://www.hellofresh.com'

def __verbose_print(to_print, verbose):
    if verbose:
        print(to_print)

##### SECTION 1:  Finding all recipe links #####

def __get_all_links(soup, base_url):
    links = []
    for x in soup.find_all('a', href=True):
        if '/recipes' in x['href']:
            links.append(x['href'].replace(base_url, ''))
    return links

def __filter_links(links):
    other_links = []
    recipe_links = []
    for link in links:
        if link[-1] == '/':
            link = link[:-1]
        if '-' in link and len(link.split('-')[-1]) >= 20:
            recipe_links.append(link)
        else:
            other_links.append(link)
    return recipe_links, other_links

def find_recipe_urls(verbose=False):
    prev_extensions = []
    search_extensions = ['/recipes']
    recipe_extensions = []
    
    while len(search_extensions) > 0:
        curr_search_extension = search_extensions.pop(0)
        __verbose_print(str(len(search_extensions)) + '\t' + curr_search_extension, verbose)
        prev_extensions.append(curr_search_extension)
    
        search_url = __base_url + curr_search_extension
        search_page = requests.get(search_url)
        search_soup = BeautifulSoup(search_page.content, "html.parser")
        search_links = __get_all_links(search_soup, __base_url)
        
        recipe_links, other_links = __filter_links(search_links)
        
        recipe_extensions.extend(recipe_links)
        for link in other_links:
            if link not in prev_extensions and link not in search_extensions:
                search_extensions.append(link)

    to_return = list(set(recipe_extensions))
    __verbose_print('Found ' + str(len(to_return)) + ' recipes from Hello Fresh', verbose)
    for i in range(len(to_return)):
        to_return[i] = __base_url + to_return[i]
    return to_return

##### SECTION 2:  Parsing recipe links to recipe objects #####

def __parse_numeric(num_str):
    try:
        return float(num_str)
    except:
        if len(num_str) == 1:
            return unicodedata.numeric(num_str)
        else:
            return float(num_str[:-1]) + unicodedata.numeric(num_str[-1])

def __get_recipe_df(url):
    recipe_page = requests.get(url)
    recipe_soup = BeautifulSoup(recipe_page.content, "html.parser")
    
    recipe_elements = [x.text for x in recipe_soup.find_all('p')]
    
    while 'produced' not in recipe_elements[0].lower():
        recipe_elements = recipe_elements[1:]
    recipe_elements = recipe_elements[1:]
    while 'people' in recipe_elements[0]:
        recipe_elements = recipe_elements[1:]
    recipe_elements = [x.strip() for x in recipe_elements]
    recipe_elements = [x for x in recipe_elements if x != '']
    
    max_index = 0
    for i in range(len(recipe_elements)):
        if 'salt' == recipe_elements[i].lower().split(' ')[-1] or 'pepper' == recipe_elements[i].lower().split(' ')[-1]:
            max_index = i
            
    recipe_elements = recipe_elements[:max_index+1]
    
    recipe_dict_list = []
    new_item = {}
    for i in range(len(recipe_elements)):
        if any(char.isdigit() or char.isnumeric() for char in recipe_elements[i]):
            new_item['qty'] = ''
            new_item['unit'] = ''
            
            amount_elements = recipe_elements[i].split(' ')
            for element in amount_elements:
                if any(char.isdigit() or char.isnumeric() for char in element):
                    new_item['qty'] += element + ' '
                else:
                    new_item['unit'] += element + ' '
            
            new_item['qty'] = new_item['qty'][:-1]
            new_item['unit'] = new_item['unit'][:-1]
        else:
            new_item['item'] = recipe_elements[i]
            recipe_dict_list.append(new_item)
            new_item = {}
    
    df = pd.DataFrame(recipe_dict_list, columns=['qty', 'unit', 'item'])
    df = df[df.item != 'unit']
    df['qty'] = df['qty'].apply(__parse_numeric)
    
    return df

def get_recipe(url):
    recipe_df = None
    try:
        recipe_df = __get_recipe_df(url)
    except:
        raise recipe.RecipeParseException('Invalid Recipe URL\n' + url)

    to_return = recipe.Recipe(url, recipe_df)
    return to_return