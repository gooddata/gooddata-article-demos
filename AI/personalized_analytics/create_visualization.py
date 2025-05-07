import yaml
import os
from pathlib import Path

def create_visualization(visualization, path=Path("analytics/visualisations"), deploy=True):
    visualization = yaml.safe_load(visualization)
    title = visualization.get("title").replace(" ", "_") + ".yaml"

    # Ensure path is a Path object
    if isinstance(path, str):
        path = Path(path)

    output_file_path = path / title

    # Save the content to the file, replacing it if it exists
    with open(output_file_path, "w") as output_file:
        yaml.dump(visualization, output_file, default_flow_style=False)
    if deploy:
        deploy_analytics()
    return visualization.get("id")

def deploy_analytics():
    result = os.system("gd deploy")
    if result != 0:
        raise RuntimeError("gd deploy failed")

def create_dashboard(dashboard, deploy=True):
    dashboard = yaml.safe_load(dashboard)
    title = dashboard.get("title").replace(" ", "_") + ".yaml"

    # Define the output directory and file path
    output_directory = Path("analytics/dashboards")
    output_directory.mkdir(parents=True, exist_ok=True)
    output_file_path = output_directory / title
    print(output_file_path)

    # Save the content to the file, replacing it if it exists
    with open(output_file_path, "w") as output_file:
        yaml.dump(dashboard, output_file, default_flow_style=False)
    if deploy:
        deploy_analytics()
    return dashboard.get("id")

def create_dataset(dataset):
    dataset = yaml.safe_load(dataset)
    title = dataset.get("title").replace(" ", "_") + ".yaml"

    # Define the output directory and file path
    output_directory = Path("analytics/datasets")
    output_directory.mkdir(parents=True, exist_ok=True)
    output_file_path = output_directory / title

    # Save the content to the file, replacing it if it exists
    with open(output_file_path, "w") as output_file:
        yaml.dump(dataset, output_file, default_flow_style=False)
    return dataset.get("id")