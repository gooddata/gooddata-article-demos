# GoodData Personalized Analytics Demo

This demo shows how to generate personalized analytics for different user personas.

## How it works

The demo is split into three parts:

1. **Data selection**

The user selects the data sources they want to use to generate the analytics.

2. **Persona selection**

The user selects the personas that should use the analytics.

3. **Dashboard generation**

The analytics are generated and displayed in a dashboard.


## How to run the demo


1. Create venv and install the dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Update .env and gooddata.yaml

Based on `.env.example` create `.env`. It should include:
```
GOODDATA_HOST="" # E.g., example.gooddata.com/
GOODDATA_API_TOKEN="" # Create an API token through GoodData UI
OPENAI_TOKEN="" # OpenAI API token
```

Then update the `gooddata.yaml`, so it complies with your environment. For more information, check out the [documentation](https://www.gooddata.com/docs/cloud/api-and-sdk/vs-code-extension/structures/#gooddatayaml).

3. Update Iframe source in [/templates/dashboards.html](./templates/dashboards.html)

In the GoodData UI get the Iframe for the dashboard, so this demo can work on top of it.

4. Run the demo

```bash
python app.py
```

5. Open the dashboard in your browser

```bash
open http://localhost:8000 # Flask
```

## Disclaimer

The prompts have been shortened and refactored, due to copyright and IP reasons. This may greatly affect performance.