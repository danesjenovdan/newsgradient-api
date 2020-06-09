import marshmallow
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView


class SuperAPIView(APIView):
    qp_schema = None

    def __init__(self):
        super(SuperAPIView, self).__init__()
        self.cleaned_qp = {}

    def initial(self, request, *args, **kwargs):
        super(SuperAPIView, self).initial(request, *args, **kwargs)
        self._check_query_params()

    def _check_query_params(self):
        if not self.qp_schema:
            return
        schema = self.qp_schema()
        try:
            self.cleaned_qp = schema.load(self.request.GET)
        except marshmallow.ValidationError as err:
            raise ValidationError(err.messages)
