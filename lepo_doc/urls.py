from django.urls import re_path


def get_docs_urls(router, namespace, docs_url='docs/?'):
    from . import views
    json_url_name = f'lepo_doc_{id(router)}'
    return [
        re_path(r'swagger\.json$', views.get_swagger_json, kwargs={'router': router}, name=json_url_name),
        re_path(f'{docs_url}$', views.render_docs, kwargs={
            'router': router,
            'json_url_name': f'{namespace}:{json_url_name}',
        }),
    ]
