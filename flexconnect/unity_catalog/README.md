# FlexConnect: Integrate Unity Catalog with GoodData

This repository demonstrates how to connect Unity Catalog to GoodData using FlexConnect. By leveraging FlexConnect, you can seamlessly bring data from Unity Catalog into your BI reports without the complexity of data pipelines or SQL queries.

This project is built on top of the [GoodData FlexConnect Template](https://github.com/gooddata/gooddata-flexconnect-template).

## Introduction

Integrating data from different sources into your business intelligence (BI) reports is crucial for robust analytics. Unity Catalog is a unified governance solution for all data and AI assets in your lakehouse, making managing and accessing your data a breeze. However, Unity Catalog can be complex and may contain various objects beyond just tables, such as machine learning models.

FlexConnect bridges this gap by allowing you to connect Unity Catalog directly to GoodData using Python. This project demonstrates how to use FlexConnect to integrate tables from Unity Catalog into GoodData.

## What is FlexConnect

FlexConnect is a feature of GoodData that enables you to build custom data sources. It allows you to implement "code as a data source," providing the flexibility to connect GoodData to any data source using arbitrary code.

### Technical Overview

- **FlexConnect Functions**: Implemented as classes inheriting from `FlexConnectFunction`, they compute and return tabular data.
- **Apache Arrow Flight RPC**: Used for communication between GoodData and your FlexConnect server.
- **Server Infrastructure**: Managed by GoodData's `gooddata-flight-server`, handling all technicalities of hosting and exposing your functions.

## Getting Started

### Prerequisites

- **Python 3.12**
- **Unity Catalog Access**: Ensure you have access to Unity Catalog where your CSV and Parquet files are registered.
- **Python Libraries**:
  - `polars`
  - `databricks-sql-connector`
  - `databricks-sdk`
  - `gooddata-flight-server`
  - `gooddata-flexconnect`

All the requirements are in the `requirements.txt` file

### Preparing the Data

We will integrate data from Unity Catalog, specifically:

**Ice Cream Recipes**: Contains various ice cream recipes with ingredients and their amounts (CSV file).
**Ingredient Prices**: Prices per gram for each ingredient used in the recipes (Parquet file).

These files are included in the repository.

### Installation

#### Configure Databricks Connection:

Ensure your Databricks credentials and configurations are accessible to the server. Update your `.env` file with the necessary credentials:


```
echo 'API_TOKEN="your_api_token"' >> .env
echo 'HOST_NAME="your_host_name"' >> .env
echo 'HTTP_PATH="your_http_path"' >> .env
echo 'TABLE_NAME="your_table_name"' >> .env
```

#### Docker Compose
Build and start the services using docker-compose:

```
docker-compose up -d --build gooddata-flexconnect-server
```

#### Adding FlexConnect as Data Source

For your convenience, here is the curl, that will register the FlexConnect as a data source:

```
curl https://<gooddata-domain>/api/v1/entities/dataSources \
-H "Authorization: Bearer <your-gooddata-token>" \
-s -H "Content-Type: application/vnd.gooddata.api+json" \
-X POST \
-d '{
  "data": {
    "id": "flexconnect-server",
    "type": "dataSource",
    "attributes": {
      "url": "grpc://<your-server-host>:17001",
      "name": "flexconnect-server",
      "type": "FLEXCONNECT",
      "token": "<your-secret-token>",
      "schema": "",
      "cacheStrategy": "NEVER"
    }
  }
}'
```

## Contributing

We welcome contributions to enhance this project! Whether you want to report a bug, propose a feature, or submit a pull request, your involvement is highly appreciated.

To contribute:

1. Fork the repository and create a new branch for your feature or bugfix.
2. Make your changes, following the coding standards and best practices outlined in the repository.
3. Test your changes locally or using the provided Docker Compose setup.
4. Submit a pull request, including a clear description of the changes and their purpose.

For larger changes or feature proposals, please open an issue first to discuss your ideas with the maintainers.

---

## License

This project is licensed under the MIT License.

You are free to use, modify, and distribute this software. See the [LICENSE](LICENSE) file for the full text of the license.

By contributing to this project, you agree that your contributions will be licensed under the same MIT License.
