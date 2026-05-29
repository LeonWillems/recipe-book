import json
import pandas as pd
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent

""" ASSUMPTIONS FOR THE BOOK ITSELF

- You are assumed to have the following ingredients and thus should not be
    mentioned in the ingredients list:
    salt, pepper, water & olive oil
- Even though adding salt is mentioned sometimes, every step of the cooking
    process benefits from adding a bit of salt. Gauge yourself how much is good
- There is no mention of any special kitchen aid stuff in a list,
    should be extracted by the user from the recipe
- When we mention `butter`, the exact butter depends on context. For baking
    desserts and stuff, it's `roomboter`. For cooking, it's `bakboter`

Some thoughts while making this book:
- Ingredients lists are always ordered the way we use them in the recipe

"""


def read_json_to_dict(file_location: Path, file_name: str) -> dict:
    """Read in a .json file.

    Parameters:
    - file_location (Path): Folder to put file in (e.g. Path('this/path/'))
    - file_name (str): Name of file, without extension (e.g. 'employees_table')

    Returns:
    - dict: Contents of the .json-file in dictionary format
    """
    complete_path = (file_location / file_name).with_suffix('.json')

    with open(complete_path) as f:
        json_dict = json.load(f, )

    return json_dict


def process_recipes_dict(recipes_dict: dict) -> list[list]:
    recipes_list = []

    for recipe_name, val in recipes_dict.items():
        specs = val['specs']
        recipe_dict: dict = {
            'key': recipe_name,
            'name': val['name'],
            'persons': specs['persons'],
            'price': specs['price'][3:],
            'type': specs['type'],
            'prep_time': specs['prep_time'],
            'cook_time': specs['cook_time'],
            'diet': specs['diet'],
            'scalability': specs['scalability'],
            'rating': specs['my_rating'],
            'len_procedure': len(val['procedure']),
            'len_ingredients': len(val['ingredients']),
            'len_subassembly': len(val['subassembly']),
        }
        recipes_list.append(recipe_dict.values())

    column_names = recipe_dict.keys()
    return column_names, recipes_list


def output_to_csv(column_names, recipes_list, file_name):
    recipes_df = pd.DataFrame(
        data=recipes_list,
        columns=column_names,
    )
    recipes_df.to_csv(CURRENT_DIR / file_name)


if __name__ == "__main__":
    recipes_json = 'recipes.json'
    recipes_csv = 'recipes.csv'

    recipes_dict = read_json_to_dict(CURRENT_DIR, recipes_json)

    column_names, recipes_list = process_recipes_dict(recipes_dict)

    output_to_csv(column_names, recipes_list, recipes_csv)
