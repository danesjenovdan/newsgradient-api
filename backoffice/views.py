from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.management import call_command
from django.shortcuts import redirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View


class ClearCacheView(View):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ClearCacheView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, 'reset_cache.html')

    def post(self, request):
        call_command('clear_cache')
        messages.add_message(request, messages.INFO, 'Cache cleared')
        return redirect(reverse('backoffice.clear_cache'))
