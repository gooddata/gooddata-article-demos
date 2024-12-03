# Contributing

Thank you for your interest in contributing to the `gooddata-article-demos` repository! Contributions can fall into two main categories:

1. [New projects for articles.](#new-projects-for-articles)  
2. [Fixes or enhancements to existing article code.](#fixes-or-enhancements-to-existing-article-code)


Please follow the guidelines below to ensure a smooth collaboration.

---

## New projects for articles

If you are proposing a new project for an article, please follow these steps:

1. **Get Approval**  
   If you don’t already have an agreement with one of the maintainers, please contact them before starting.  

2. **Fork the Repository**  
   Create a fork of the `gooddata-article-demos` repository to host your work.

3. **Create a New Branch**  
   Use a separate, dedicated branch for each feature or bugfix.

4. **Develop Your Project**  
   Adhere to the [coding conventions](#coding-conventions) outlined below.  
   Ensure the project includes all required files (see [Project Necessities](#project-necessities)).  

5. **Submit a Pull Request**  
   Once your project is complete, submit a pull request. Be sure to reference the associated article and provide a clear description of your project.  

---


## Fixes or Enhancements to Existing Article Code

We welcome contributions to enhance existing projects! Whether you're fixing bugs, proposing improvements, or adding features, your input is valued.

### Steps to Contribute

1. **Fork the Repository**  
   Create a fork of the repository.  

2. **Create a New Branch**  
   Use a separate, dedicated branch for each feature or bugfix.

3. **Make Changes**  
   Follow the repository’s [coding conventions](#coding-conventions) and best practices.  
   Test your changes locally or using the provided Docker Compose setup (if applicable).  

4. **Submit a Pull Request**  
   Include a clear and concise description of your changes.  
   If your contribution is significant, consider opening an issue first to discuss your proposal with maintainers.  

---

## Coding Conventions

Python projects document code by docstrings in [google-like](https://google.github.io/styleguide/pyguide.html#3-python-style-rules) format.

For any front-end related projects, please follow the best practices of [gooddata-ui-sdk](https://github.com/gooddata/gooddata-ui-sdk/blob/master/dev_docs/contributing.md).

**All applicable files should have copyright header.** This includes, but is not limited to `.py`, `.yaml`, `.sh`, `.toml` and `.ini` files. When unsure whether a file needs a copyright header, please contact the maintainers.

Example of a copyright header:

```
# (C) 2024 GoodData Corporation
```

---

## Project Necessities

Each new project should have their corresponding:

- README
  - Provide instructions on how to run the project.  
  - Serve as a standalone explanation of the project.  
  - Reference the related article with a link.  

- CONTRIBUTING
  - Outline how others can contribute to the project.

- LICENSE
  - Use the MIT license unless explicitly instructed otherwise by the GoodData legal team.  

---

### Final Note  

Your contributions help make this repository better, and we’re grateful for your efforts! If you have any questions, feel free to reach out to a maintainer.