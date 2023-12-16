from openai import OpenAI
import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))


with open(os.path.join(script_dir, "../../../../secrets.json")) as fh:
    secrets = json.loads(fh.read())

def main():
    client = OpenAI(api_key=secrets["OPENAPI_SECRET_KEY"])

    with open(os.path.join(script_dir, "../../../../data/schemas/recipes.json")) as fh:
        recipe_schema = fh.read()
    
    with open('tmp/recipe.txt') as fh:
        recipe_text = fh.read()

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"This is a JSON Schema that expresses a cooking recipe. Do you understand it?\n{recipe_schema}",
            },
            {
                "role": "system",
                "content": "Yes, I understand the JSON schema. It defines the structure and constraints for a cooking recipe. It includes properties for the recipe name, summary, cuisine, diet, difficulty level, cooking time, ingredients, steps, and more.The schema also defines the required properties for a valid recipe. If you have any specific questions or need help with anything related to this JSON schema, feel free to ask!",
            },
            {
                "role": "user",
                "content": "Do you think you can translate a written english recipe into this json schema?"
            },
            {
                "role": "system",
                "content": "Yes, I can certainly help with that. If you provide the written English recipe, I can assist in translating it into the JSON schema format. Just let me know the details, and I'll guide you through the translation process"
            },
            {
                "role": "user",
                "content": """Great! But first, let me tell you a bit more about how to interpret the schema.
                
                PLEASE Take care to note the enum choices for the "unit" property, they are abbreviated versions of standard measuring units. If there is a unit in the recipe that doesn't match up to any of them, use "customUnit" instead. Sometimes the unit is the ingredient itself, like "1 apple". In those cases, use "customUnit" set as an empty string. Use this guide to translate the units you see:

                ```
                pound(s) -> "lb",
                ounce(s) -> "oz",
                gram(s) -> "g",
                cup(s) -> "cup",
                fluid ounce(s) -> "fl oz",
                milliliter(s) -> "ml",
                pint(s) -> "pint",
                teaspoon(s) -> "tsp",
                tablespoon(s) ->"tbsp",
                pinch/pinch of -> "pinch",
                kilogram(s) -> "kg",
                gallon(s) -> "gal",
                liter(s) -> "liter"

                A "modifier" is a way to prepare an ingredient. In the list of ingredients, this is usually the verbs, which follows a comma after the ingredient. It can sometimes be in parentheses. Something like "10 pounds shrimp, peeled and deveined" would be \{"amount": [10], "ingredient": "shrimp", "customUnit": "", "modifier": "peeled and deveined" }.

                The "amount" property in the ingredient can be an array of 1 number for a static amount, or 2 number for a range. For example, if the recipe called for "1-3" apples, the amount would be [1, 3].

                Finally, don't put anything for "imageUrl", "originalSource", "media", "photoAttribution", or "attribution" fields. Does this all make sense?
                """
            },
            {
                "role": "system",
                "content": "Yes, I've noted the details and guidelines for translating the recipe into the JSON schema format. I understand the conventions for units, modifiers, and the structure of the recipe. When you're ready to provide the English recipe, I can help you convert it into the JSON schema using the information you've provided. Let me know if you have the recipe or if there's anything else you need assistance with!"
            },
            {
                "role": "user",
                "content": f"Great! The recipe is below. Please respond with just the raw json representation, so that it can be parsed:\n\n${recipe_text}"
            }
        ],
    )
    print(response.choices[0].message.content)
    return json.loads(response.choices[0].message.content)


if __name__ == "__main__":
    main()
