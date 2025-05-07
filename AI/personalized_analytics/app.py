from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # Import CORS
import os
from ai import ask_ai_to_suggest_personas, ask_ai_to_create_visualizations, ask_ai_to_create_dashboards, ask_ai_to_create_model
from create_visualization import create_visualization, create_dashboard, deploy_analytics, create_dataset
import shutil
from gooddata_sdk import GoodDataSdk

app = Flask(__name__)
CORS(app, resources={r"/upload": {"origins": "*"}, r"/uploadDashboard": {"origins": "*"}})

global proposed_personas

host = os.environ.get("GOODDATA_HOST")
token = os.environ.get("GOODDATA_API_TOKEN")
sdk = GoodDataSdk.create(host, token)

@app.route('/')
def home():
    data_sources = sdk.catalog_data_source.list_data_sources()
    data = [{"name": data_source.name, "id": data_source.id} for data_source in data_sources]
    return render_template('index.html', data=data)

@app.route('/personas')
def personas():
    data_source = request.args.get('data_source')
    tables = sdk.catalog_data_source.scan_data_source(data_source_id=data_source)
    proposed_personas = ask_ai_to_suggest_personas(tables)
    datasets = ask_ai_to_create_model(tables, personas)

    datasets_directory = os.path.join('analytics', 'datasets')
    if os.path.exists(datasets_directory):
        shutil.rmtree(datasets_directory)
    os.makedirs(datasets_directory, exist_ok=True)

    for dataset in datasets:
        create_dataset(str(dataset))

    persona_names = [persona['name'] for persona in proposed_personas]
    print(persona_names)
    return render_template('personas.html', data=persona_names)

@app.route('/dashboards')
def scan_db():
    names = ", ".join(request.args.getlist('personas')) + ", " + request.args.get('additional_text')

    visualisations_directory = os.path.join('analytics', 'visualisations')
    dashboards_directory = os.path.join('analytics', 'dashboards')
    for directory in [visualisations_directory, dashboards_directory]:
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory, exist_ok=True)

    personas = ask_ai_to_create_visualizations(names)

    for persona in personas:
        # Create a directory for each persona's title
        directory = os.path.join(visualisations_directory, persona['title'])
        os.makedirs(directory, exist_ok=True)
        
        # Iterate over the visualizations for each persona
        for viz in persona['visualisations']:
            create_visualization(str(viz), directory, False)

    dashboards = ask_ai_to_create_dashboards(personas)
    for dashboard in dashboards:
        create_dashboard(str(dashboard), False)
    deploy_analytics()
    
    return render_template('dashboards.html')


if __name__ == "__main__":
    app.run(port=8000, debug=True)
