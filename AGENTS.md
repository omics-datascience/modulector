# Modulector

## Code Style

- Follow PEP 8 style guide for Python code, to maintain consistency and readability.
- Use 4 spaces per indentation level, to improve readability.
- Avoid over-modularization and unnecessary indirection. Do not create pass-through functions that only delegate to another function without adding meaningful behavior, validation, transformation, error handling, or abstraction value. Prefer direct, readable code over layers of wrappers.
- Avoid excessive constants for values that are used once or are clearer inline, especially when splitting simple expressions into multiple named constants adds noise instead of clarity. Constants are appropriate for shared values, domain concepts, repeated literals, or values that benefit from a clear semantic name. For simple configuration defaults, prefer concise and idiomatic code, for example: `A_SETTING_VALUE: Final[str] = os.getenv("A_SETTING_VALUE", "default value")`. The goal is to keep the codebase simple, explicit, and maintainable, with abstractions introduced only when they reduce duplication or clarify intent.

## Functions/Methods

- Always type hint functions/methods, to improve readability and maintainability.
- Use docstrings to explain the purpose and usage of functions/methods, including parameters and return values.
- Docstrings must be in reStructuredText format, to maintain consistency and readability.
- Don't add type hints in docstrings, as they are already provided in the function/method signature.

## Dependencies

- Always use strict version of dependencies, to avoid breaking changes.
