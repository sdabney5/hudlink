\# Contributing to hudlink



Thank you for considering contributing to hudlink! This document provides guidelines and instructions for contributing to the project.



\## Table of Contents

\- \[Code of Conduct](#code-of-conduct)

\- \[How Can I Contribute?](#how-can-i-contribute)

\- \[Development Setup](#development-setup)

\- \[Making Changes](#making-changes)

\- \[Testing](#testing)

\- \[Submitting Changes](#submitting-changes)

\- \[Style Guidelines](#style-guidelines)

\- \[Reporting Issues](#reporting-issues)



\## Code of Conduct



By participating in this project, you agree to abide by our principles of respectful and constructive collaboration. We are committed to providing a welcoming and harassment-free experience for everyone.



\## How Can I Contribute?



\### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:



\- A clear and descriptive title

\- Detailed steps to reproduce the issue

\- Expected behavior vs actual behavior

\- Your environment details (OS, Python version, hudlink version)

\- Any relevant error messages or logs



\### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:



\- A clear description of the proposed feature

\- Use cases and examples

\- Why this enhancement would be useful to most users

\- Possible implementation approaches (if you have ideas)



\### Contributing Code

We welcome code contributions for:



\- Bug fixes

\- New features

\- Performance improvements

\- Documentation improvements

\- Test coverage expansion



\## Development Setup



1\. \*\*Fork and clone the repository\*\*

&nbsp;  `git clone https://github.com/yourusername/hudlink.git`

&nbsp;  `cd hudlink`



2\. \*\*Create a virtual environment\*\*

&nbsp;  `python -m venv venv`

&nbsp;  `source venv/bin/activate  # On Windows: venv\\Scripts\\activate`



3\. \*\*Install in development mode\*\*

&nbsp;  `pip install -e .`

&nbsp;  `pip install -e .\[test]  # For testing dependencies`



4\. \*\*Set up your IPUMS API token\*\*

&nbsp;  `# Add your token to secrets/ipums\_token.txt`

&nbsp;  `echo "YOUR\_TOKEN\_HERE" > secrets/ipums\_token.txt`



\## Making Changes



1\. \*\*Create a feature branch\*\*

&nbsp;  `git checkout -b feature/your-feature-name`



2\. \*\*Make your changes\*\*

&nbsp;  - Write clear, self-documenting code

&nbsp;  - Add docstrings to all functions and classes

&nbsp;  - Update relevant documentation

&nbsp;  - Add tests for new functionality



3\. \*\*Run tests\*\*

&nbsp;  `pytest tests/`



4\. \*\*Check code style\*\*

&nbsp;  `# I recommend using black for formatting`

&nbsp;  `black src/hudlink/`



\## Testing



\- All new features must include appropriate tests

\- Ensure all tests pass before submitting PR

\- Aim for test coverage of new code

\- Test files should be placed in the `tests/` directory



Run the test suite:

`pytest tests/test\_hudlink.py -v`



\## Submitting Changes



1\. \*\*Commit your changes\*\*

&nbsp;  `git add .`

&nbsp;  `git commit -m "Brief description of changes"`



&nbsp;  Write meaningful commit messages:

&nbsp;  - Use present tense ("Add feature" not "Added feature")

&nbsp;  - Keep the first line under 50 characters

&nbsp;  - Reference issues and pull requests when relevant



2\. \*\*Push to your fork\*\*

&nbsp;  `git push origin feature/your-feature-name`



3\. \*\*Submit a Pull Request\*\*

&nbsp;  - Go to the original repository

&nbsp;  - Click "New Pull Request"

&nbsp;  - Provide a clear title and description

&nbsp;  - Reference any related issues

&nbsp;  - Wait for review and address feedback



\## Style Guidelines



\### Python Code Style

\- Follow PEP 8 guidelines

\- Use meaningful variable and function names

\- Maximum line length of 88 characters (Black default)

\- Use type hints where appropriate



\### Documentation

\- All public functions must have docstrings

\- Use Google-style docstrings format

\- Include examples in docstrings where helpful

\- Keep documentation up-to-date with code changes



\### Example Docstring



def calculate\_eligibility(household\_data, income\_limit, threshold=0.5):

&nbsp;  """

&nbsp;  Calculate housing program eligibility for households.

&nbsp;  

&nbsp;  Args:

&nbsp;      household\_data (pd.DataFrame): DataFrame containing household information

&nbsp;      income\_limit (float): Area median income limit

&nbsp;      threshold (float, optional): Income threshold percentage. Defaults to 0.5.

&nbsp;  

&nbsp;  Returns:

&nbsp;      pd.DataFrame: DataFrame with eligibility flags added

&nbsp;      

&nbsp;  Example:

&nbsp;      >>> df = calculate\_eligibility(households, 50000, threshold=0.8)

&nbsp;  """



\## Questions?



If you have questions about contributing, please open an issue with the "question" label or contact the maintainer at sdabney@fsu.edu.



Thank you for contributing to hudlink and helping make housing analysis more accessible!







