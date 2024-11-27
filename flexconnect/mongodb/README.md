# FlexConnect: Integrate MongoDB with GoodData

This repository demonstrates how to connect a MongoDB collection to GoodData using FlexConnect. By leveraging the Apache Arrow format and GoodData's FlexConnect, you can efficiently integrate semi-structured NoSQL data into GoodData's BI platform.

This project is built on top of the [GoodData FlexConnect Template](https://github.com/gooddata/gooddata-flexconnect-template).

## Introduction

NoSQL databases like MongoDB have gained significant traction due to their flexibility and scalability. However, integrating these semi-structured data sources with BI platforms can be challenging.

FlexConnect bridges this gap by allowing you to connect virtually any data source to GoodData. This project demonstrates how to use FlexConnect to integrate MongoDB's Sample Mflix dataset with GoodData using Python.

## What is FlexConnect

FlexConnect is a feature of GoodData that enables you to build custom data sources. It allows you to implement "code as a data source," providing the flexibility to connect GoodData to any data source using arbitrary code.

### Technical Overview

- **FlexConnect Functions**: Implemented as classes inheriting from `FlexConnectFunction`, they compute and return tabular data.
- **Apache Arrow Flight RPC**: Used for communication between GoodData and your FlexConnect server.
- **Server Infrastructure**: Managed by GoodData's `gooddata-flight-server`, handling all technicalities of hosting and exposing your functions.

## Getting Started

### Prerequisites

- **Python 3.12**
- **MongoDB**: An instance with the Sample Mflix dataset ([Setup Guide](https://www.mongodb.com/docs/manual/tutorial/sample-databases/#load-sample-datasets))
- **Python Libraries**:
  - `pymongo`
  - `pymongoarrow`
  - `gooddata-flight-server`
  - `gooddata-flexconnect`

All the requirements are in the `requirements.txt` file

### Installation

#### Configure MongoDB Connection:

Ensure your MongoDB connection string is accessible to the server. Update the MONGO_CONN_STRING in your .env file:


```
echo 'MONGO_CONN_STRING="your_mongodb_connection_string"' >> .env
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
