from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import json
import os


def load_directory_into_string(directory_path):
    # Convert directory_path to a Path object
    directory = Path(directory_path)
    
    # Initialize an empty string to hold the contents
    all_contents = ""

    # Iterate through each file in the directory
    for file_path in directory.iterdir():
        if file_path.is_file():  # Make sure it's a file
            all_contents += file_path.read_text() + "\n"

    # Return the combined contents of all files
    return all_contents

def ask_ai_to_suggest_personas(tables):
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    schema = json.loads(Path('prompts/personas_schema.json').read_text())
    persona = Path('prompts/persona.txt').read_text()

    outcome = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": persona},
            {"role": "system", "content": f"Here are the tables from which are available for use in analytics: \n###\n {tables} \n###\n" },
            {"role": "user", "content": f"Based on the data, propose me 5 new personas that would benefit from the data consumption."},
        ],
        response_format = schema
    )
    return json.loads(outcome.choices[0].message.content).get('personas')

def ask_ai_to_create_visualizations(personas):
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    INSTRUCTIONS = Path('prompts/visualization_builder.txt').read_text()
    PROMPT_DATASETS = load_directory_into_string('analytics/datasets')
    REFERENCES_GUIDELINES = Path('prompts/references.txt').read_text()
    PROMPT_EXAMPLES_OF_VISUALIZATION = load_directory_into_string('examples/visualisations')
    schema = json.loads(Path('prompts/visualizations_schema.json').read_text())

    outcome = client.chat.completions.create(
        model="o3-mini",
        messages=[
            {"role": "system", "content": INSTRUCTIONS},
            {"role": "system", "content": f"Here are the guidelines related to how to reference across files: \n###\n {REFERENCES_GUIDELINES} \n###\n"},
            {"role": "system", "content": f"Here are the fields from which you can build visualizations. Use only available identifiers of the existing fields here: \n###\n {PROMPT_DATASETS} \n###\n" },
            {"role": "system", "content": f"Here are examples of visualizations: \n###\n {PROMPT_EXAMPLES_OF_VISUALIZATION} \n###\n"},
            {"role": "user", "content": f"For each persona, propose at least 5 visualizations that would be useful when building a dashboard for the given persona. Personas: \n###\n {personas} \n###\n"},
        ], 
        response_format = schema
    )
    return json.loads(outcome.choices[0].message.content).get('personas')

def ask_ai_to_create_dashboards(personas):
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    INSTRUCTIONS = Path('prompts/dashboard_builder.txt').read_text()
    PROMPT_DATASETS = load_directory_into_string('analytics/datasets')
    REFERENCES_GUIDELINES = Path('prompts/references.txt').read_text()
    PROMPT_EXAMPLES_OF_DASHBOARDS = load_directory_into_string('examples/dashboards')
    schema = json.loads(Path('prompts/dashboard_schema.json').read_text())

    outcome = client.chat.completions.create(
        model="o3-mini",
        messages=[
            {"role": "system", "content": INSTRUCTIONS},
            {"role": "system", "content": f"Here are the guidelines related to how to reference across files: \n###\n {REFERENCES_GUIDELINES} \n###\n"},
            {"role": "system", "content": f"Here are the fields from which you can build dashboard filters: \n###\n {PROMPT_DATASETS} \n###\n"},
            {"role": "system", "content": f"Here are already existing dashboards to learn from: \n###\n {PROMPT_EXAMPLES_OF_DASHBOARDS} \n###\n"},
            {"role": "user", "content": f"For each persona, generate a dashboard. Name it according to the persona and fill it with widgets that reference visualisation by using the IDs of visualisations used by each persona: \n###\n {personas} \n###\n"}
            
        ], 
        response_format = schema
    )
    return json.loads(outcome.choices[0].message.content).get('dashboards')

def ask_ai_to_create_model(tables, topics):
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    INSTRUCTIONS = Path('prompts/model_builder.txt').read_text()
    REFERENCES_GUIDELINES = Path('prompts/references.txt').read_text()
    PROMPT_EXAMPLES_OF_DATASETS = load_directory_into_string('examples/datasets')
    schema = json.loads(Path('prompts/model_schema.json').read_text())

    outcome = client.chat.completions.create(
        model="o3-mini",
        messages=[
            {"role": "system", "content": INSTRUCTIONS},
            {"role": "system", "content": f"Here are the guidelines related to how to reference across files: \n###\n {REFERENCES_GUIDELINES} \n###\n"},
            {"role": "system", "content": f"Here are examples of existing datasets: \n###\n {PROMPT_EXAMPLES_OF_DATASETS} \n###\n"},
            {"role": "user", "content": f"Generate a logical data model based on the following tables: \n###\n {tables} \n###\n. The model should support these topics: \n###\n {topics} \n###\n" }
        ], 
        response_format = schema
    )
    return json.loads(outcome.choices[0].message.content).get('datasets')