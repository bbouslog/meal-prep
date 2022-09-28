import pandas as pd

class RecipeParseException(Exception):
    pass

class Recipe:
    def __init__(self, recipe_url=None, recipe_df=None, recipe_dict=None):
        if recipe_dict == None:
            self.set_recipe_url(recipe_url)
            self.set_recipe_df(recipe_df)
        else:
            self.set_recipe_dict(recipe_dict)

    def set_recipe_url(self, recipe_url):
        self.__recipe_url = recipe_url

    def set_recipe_df(self, recipe_df):
        self.__recipe_df = recipe_df

    def set_recipe_dict(self, recipe_dict):
        self.__recipe_url = recipe_dict['url']
        self.__recipe_df = pd.DataFrame(recipe_dict['recipe'], columns=['qty', 'unit', 'item'])

    def get_recipe_url(self):
        return self.__recipe_url

    def get_recipe_df(self):
        return self.__recipe_df

    def get_recipe_dict(self):
        to_return = {}
        to_return['url'] = self.__recipe_url
        to_return['recipe'] = []
        for idx, row in self.__recipe_df.iterrows():
            to_return['recipe'].append(row)
        return to_return