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

### Exception Handling

You can raise a `lepo.excs.ExceptionalResponse` (which wraps a Django `response`)
anywhere within a handler invocation. These exceptions will be caught by the internal
`PathView` class and the wrapped response used as the handler's response.

This is a pragmatic way to refactor behavior common to multiple handlers, e.g.

```python
def _get_some_object(request, id):
    if not request.user.is_authenticated():
        raise ExceptionalResponse(JsonResponse({'error': 'not authenticated'}, status=401))
    try:
        return Object.objects.get(pk=id)
    except ObjectDoesNotExist:
        raise ExceptionalResponse(JsonResponse({'error': 'no such object'}, status=404))


def get_object_detail(request, id):
    object = _get_some_object(request, id)
    return {'id': object.id}


def delete_object(request, id):
    object = _get_some_object(request, id)
    object.delete()
    return {'id': object.id, 'deleted': True}
```
