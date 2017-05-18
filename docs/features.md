Features
========

Features marked with a checkbox are supported.

Those without a checkbox aren't guaranteed to be supported.

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

* [x] Path `$ref`s
* [x] Path-level `consumes`/`produces` definitions
* [x] Operation-level `consumes`/`produces` definitions
* [ ] References outside a single OpenAPI file ("Relative Files With Embedded Schema")

### Definitions

* [x] `$ref`s in definitions
* [ ] Model polymorphism (schema `discriminator` field)

### Parameters

* [x] Path-level `parameter` definitions
* [x] Operation-level `parameter` definitions
* [x] Parameters in paths
* [x] Parameters in query string
* [x] Parameters in HTTP headers
* [x] Parameters in HTTP body
* [x] Primitive parameters in HTTP body
* [x] Parameters in HTTP form data
* [x] Body-type parameter schema validation
* [x] Parameter type/format validation
* [ ] Parameter `allowEmptyValue`
* [x] Parameter CSV/SSV/TSV/Pipes collection formats
* [x] Parameter multi collection format
* [x] Parameter defaults
* [x] Parameter extended validation (`maximum`/...)
* [x] Parameter array `items` validation
* [x] Parameter Definitions Objects
* [x] Parameter `$ref`s
* [x] Replacement of entire `parameters` objects with `$ref`s

### Responses

* [ ] Operation response validation
* [ ] Operation response `$ref`s
* [ ] Operation response schema validation
* [ ] `file` as operation response schema type
* [ ] Responses Definitions Objects
* [ ] Headers validation

### Security

* [ ] Operation security declarations
* [ ] Security Definitions Objects
