import json
from rest_framework.renderers import JSONRenderer


class ProfileJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        response = json.dumps({"profile": data})
        if isinstance(data, list):
            return json.dumps({'profiles': data})
        errors = data.get('errors', None)
        if errors is not None:
            return super(ProfileJSONRenderer, self).render(data)

        return response

