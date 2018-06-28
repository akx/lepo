Features
========

* Features marked with "Yes" are supported.
* Features marked with "Planned" are planned.
* Features marked with "No" are not supported, either not yet or ever.
* Features marked with "Maybe" might be supported, but they haven't been tested.
* Features marked with "-" do not apply to the given API version.

The absence or presence of a feature here does not directly mean it will or won't be implemented,
so this document also serves as a TODO list of sorts.

Platform features
-----------------

* [ ] DRY API error handling
* [ ] DRY authentication and authorization
* [ ] DRY pagination

OpenAPI Features
----------------

This list was built by manually scanning down the OpenAPI specification, so omissions are entirely possible.

| Feature | Swagger 2 | OpenAPI 3 |
| ------- | --------- | --------- |
| General: Path `$ref`s | Yes | Yes |
| General: Path-level `consumes`/`produces` definitions | Yes | Yes |
| General: Operation-level `consumes`/`produces` definitions | Yes | Yes |
| General: References outside a single OpenAPI file ("Relative Files With Embedded Schema") | No | No |
| Definitions: `$ref`s in definitions | Yes | |
| Definitions: Model polymorphism (schema `discriminator` field) | Yes | Yes |
| Definitions: Population of default values within models | No | No |
| Parameters: Path-level `parameter` definitions | Yes | Maybe |
| Parameters: Operation-level `parameter` definitions | Yes | Yes |
| Parameters: in paths | Yes | Yes |
| Parameters: in query string | Yes | Yes |
| Parameters: in HTTP headers | Yes | Yes |
| Parameters: in HTTP body | Yes | Yes |
| Parameters: in HTTP cookies | - | Maybe |
| Parameters: Primitive parameters in HTTP body | Yes | Yes |
| Parameters: Parameters in HTTP form data | Yes | Yes |
| Parameters: Body-type parameter schema validation | Yes | Yes |
| Parameters: type/format validation | Yes | Yes |
| Parameters: `allowEmptyValue` | No | No |
| Parameters: CSV/SSV/TSV/Pipes collection formats | Yes | Yes |
| Parameters: multi collection format | Yes | - |
| Parameters: `label` style path components | - | Planned |
| Parameters: `matrix` style path components | - | Planned |
| Parameters: `deepObject` style | - | No |
| Parameters: list parameters becoming objects | - | Maybe |
| Parameters: defaults | Yes | Yes |
| Parameters: extended validation (`maximum`/...) | Yes | Yes |
| Parameters: array `items` validation | Yes | Yes |
| Parameters: Definitions Objects | Yes | Yes |
| Parameters: `$ref`s | Yes | Yes |
| Parameters: Replacement of entire `parameters` objects with `$ref`s | Yes | Maybe |
| Operations: Operation response validation | No | No |
| Operations: Operation response `$ref`s | No | No |
| Operations: Operation response schema validation | No | No |
| Operations: Operation response `file` schema type | No | No |
| Operations: Responses Definitions Objects | No | No |
| Operations: Headers validation | No | No |
| Security: Operation security declarations | No | No |
| Security: Security Definitions Objects | No | No |
| UI: Swagger UI | Yes | Maybe |
