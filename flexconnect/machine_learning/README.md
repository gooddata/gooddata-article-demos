# FlexConnect: Integrate Machine Learning with GoodData

This repository demonstrates how to integrate pre-trained machine learning models into GoodData using FlexConnect. By leveraging the power of FlexConnect, you can easily connect ML models to your BI reports, enabling dynamic and interactive data-driven insights.

This project is built on top of the [GoodData FlexConnect Template](https://github.com/gooddata/gooddata-flexconnect-template).

## Introduction

Integrating machine learning (ML) models into business intelligence (BI) reports can significantly enhance forecasting and decision-making capabilities. FlexConnect bridges this gap by allowing you to connect virtually any data source, including ML models, to GoodData. This project demonstrates how to use FlexConnect to integrate a pre-trained ML model into GoodData using Python.

## What is FlexConnect

FlexConnect is a feature of GoodData that enables you to build custom data sources. It allows you to implement "code as a data source," providing the flexibility to connect GoodData to any data source using arbitrary code.

### Technical Overview

- **FlexConnect Functions**: Implemented as classes inheriting from `FlexConnectFunction`, they compute and return tabular data.
- **Apache Arrow Flight RPC**: Used for communication between GoodData and your FlexConnect server.
- **Server Infrastructure**: Managed by GoodData's `gooddata-flight-server`, handling all technicalities of hosting and exposing your functions.

## Getting Started

### Prerequisites

- **Python 3.12**
- **Python Libraries**:
  - `pickle`
  - `gooddata-flight-server`
  - `gooddata-flexconnect`

All the requirements are in the `requirements.txt` file

### Installation

#### Configure MongoDB Connection:

Ensure you have your pre-trained ML model saved (e.g., revenue_model.pkl) and place it in the project directory.


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
