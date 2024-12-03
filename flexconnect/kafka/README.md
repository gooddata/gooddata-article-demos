# FlexConnect: Bridging Kafka and BI

This repository demonstrates how to connect a Kafka topic to GoodData using FlexConnect. By leveraging the Apache Arrow format and GoodData's FlexConnect, you can efficiently integrate streaming data into GoodData's BI platform.

This project is built on top of the [GoodData FlexConnect Template](https://github.com/gooddata/gooddata-flexconnect-template).

## What is FlexConnect

FlexConnect is a feature of GoodData that enables you to build custom data sources. It allows you to implement "code as a data source," providing the flexibility to connect GoodData to any data source using arbitrary code.

### Technical Overview

- **FlexConnect Functions**: Implemented as classes inheriting from `FlexConnectFunction`, they compute and return tabular data.
- **Apache Arrow Flight RPC**: Used for communication between GoodData and your FlexConnect server.
- **Server Infrastructure**: Managed by GoodData's `gooddata-flight-server`, handling all technicalities of hosting and exposing your functions.

## Getting Started

The directory contains docker-compose.yaml file to bootstrap everything you need for evaluation.

```bash
docker compose up --profile all up -d
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

You are free to use, modify, and distribute this software. See the [LICENSE](LICENSE.txt) file for the full text of the license.

By contributing to this project, you agree that your contributions will be licensed under the same MIT License.
