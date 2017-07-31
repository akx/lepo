# Concepts

## Router

The `lepo.router.Router` class is the root class of the API.

It encapsulates the OpenAPI definition document and generates
the URL patterns that are to be mounted in a Django URLconf.

## Handler

Handlers are the functions that do the actual API work.

They are mapped to the OpenAPI definition by way of the `operationId`
field available in Operation objects.

Handler functions are superficially similar to plain Django view functions
aside from a few significant differences:

* `request` is the _only_ positional argument passed to a handler;
  the other arguments are mapped from the OpenAPI operation's parameters
  and passed in as keyword arguments.
