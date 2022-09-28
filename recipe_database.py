import json
import recipe
from tqdm import tqdm
import hello_fresh as hf

__recipe_database_filename = 'recipe_database.json'

def __verbose_print(to_print, verbose):
    if verbose:
        print(to_print)

def __parse_all_recipes(verbose=True):
    all_recipes = []

    all_urls_hf = hf.find_recipe_urls(verbose=verbose)
    __verbose_print('Parsing Hello Fresh Recipes', verbose)
    for url in tqdm(all_urls_hf):
        try:
            all_recipes.append(hf.get_recipe(url))
        except recipe.RecipeParseException:
            continue

    return all_recipes

def __save_all_recipes(verbose=True):
    all_recipes = __parse_all_recipes(verbose=verbose)
    all_recipes_dict = [recipe_obj.get_recipe_dict() for recipe_obj in all_recipes]

    with open(__recipe_database_filename, 'w') as output_file:
        json.dump(all_recipes_dict, output_file)

def read_all_recipes():
    all_recipes_dict = []
    with open(__recipe_database_filename, 'r') as input_file:
        all_recipes_dict = json.load(input_file)

    all_recipes = [recipe.Recipe(recipe_dict=recipe_dict) for recipe_dict in all_recipes_dict]
    return all_recipes

if __name__ == "__main__":
    __save_all_recipes(verbose=True)