from django.urls import re_path


def get_docs_urls(router, namespace, docs_url='docs/?'):
    from . import views
    json_url_name = 'lepo_doc_%s' % id(router)
    return [
        re_path('swagger\.json$', views.get_swagger_json, kwargs={'router': router}, name=json_url_name),
        re_path('%s$' % docs_url, views.render_docs, kwargs={
            'router': router,
            'json_url_name': '%s:%s' % (namespace, json_url_name),
        }),
    ]
