"""
ASSUMES YOUR WORKING DIRECTORY IS scripts/

builds new recipes from the submitted google sheet.

Each new recipe should be its own separate PR. Therefore, it should be ran with
a script that can do said checkout and PR.

**Required**: a text file, `add_new_recipes_since`, containing one line--the iso
date of the last recipe to be added. This script will 
"""
import sys
import os
import csv
import json
import typing as t
from collections import namedtuple
from recibundler.schema.hugodata import Recipe, Ingredient
from datetime import datetime
from recibundler import reciparcer
from recibundler.schema.reciperow import reciperow
from .util import get_recipe_filename
import logging
from os import path

T = t.TypeVar("T")

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


def add_new_recipes(filepath):
    logging.debug(f"filepath is {filepath}")

    with open(filepath, newline="") as fh:
        reader = csv.reader(fh)

        with open("add_new_recipes_since") as datefh:
            try:
                last_date = datetime.fromisoformat(datefh.read().strip())
            except ValueError:
                logging.warn("starting from beginning of time")
                last_date = datetime(year=2022, month=1, day=28)

        # skip the header
        next(reader)

        for recipe in reader:
            recipe = reciperow(*recipe)
            if is_recipe_old(recipe, last_date):
                continue
            logging.info(f"the next recipe is {recipe.name}")
            write_recipe_to_json(recipe)

            with open("add_new_recipes_since", mode="w") as datefh:
                datefh.write(str(isodate_from_recipe(recipe)))
            return

        logging.error("no new recipes")
        sys.exit(1)


def isodate_from_recipe(recipe: reciperow) -> datetime:
    return datetime.strptime(recipe.timestamp, "%m/%d/%Y %H:%M:%S")


def is_recipe_old(recipe: reciperow, since) -> bool:
    """
    Parses the date from the "google" submission date and
    simply compares the date delta with `since`. If True, this is
    the next recipe to use
    """
    recipe_date = datetime.strptime(recipe.timestamp, "%m/%d/%Y %H:%M:%S")
    return recipe_date <= since

def write_recipe_to_json(recipe: dict, additional_keys=None):
    if additional_keys is None:
        additional_keys = {}
    attrs = {
        "version": "1",
        "name": recipe['name'],
        "summary": recipe['summary'],
        "steps": recipe['steps'],
        "ingredients": recipe['ingredients'],
        "timestamp": recipe['timestamp'],
        "categories": recipe.get('categories', []),
        "difficulty": (int(recipe.get('difficulty'))) if 'difficulty' in recipe else 0,
        "attribution": recipe.get('attribution', {}),
    }
    if 'photoAttribution' in recipe:
        attrs['photoAttribution'] = recipe['photoAttribution']

    optional_attrs = {
        "yields": recipe.get('yields'),
        "yieldsUnit": recipe.get('yieldsUnit'),
        "prepTimeMinutes": int(recipe['prepTimeMinutes']) if 'prepTimeMinutes' in recipe else None,
        "cookTimeMinutes": int(recipe['cookTimeMinutes']) if 'cookTimeMinutes' in recipe else None,
        "cuisines": recipe.get('cuisines'),
        "diets": recipe.get('diets')
    }

    for key, value in optional_attrs.items():
        if value:
            attrs[key] = value

    logging.debug("parsing")
    logging.debug(f"csv row: {recipe}")
    logging.info("Successfully imported recipe")
    recipe = Recipe(**attrs)

    filename = get_recipe_filename(recipe)
    logging.info(f"Recipe will be named {filename}")
    with open(path.join("..", "..", "data", "recipes", filename), "w") as fh:
        fh.write(json.dumps({**recipe, **additional_keys}, indent=2))  # type: ignore
    
    return filename


def optional(value) -> t.Optional[t.Any]:
    return value if value else None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("please pass the path to the file to build recipes from.")
        sys.exit(1)
    add_new_recipes(sys.argv[1])
