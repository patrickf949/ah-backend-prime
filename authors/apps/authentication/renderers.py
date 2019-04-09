import json

from rest_framework.renderers import JSONRenderer


class UserJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        response = json.dumps({'user': data})
        if isinstance(data, list):
            return json.dumps({'Users-list': data})
        errors = data.get('errors', None)
        if errors is not None:
            return super(UserJSONRenderer, self).render(data)
        return response
