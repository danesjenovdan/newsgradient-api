from threading import Thread

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.management import call_command
from django.shortcuts import redirect
from django.shortcuts import render
# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View

COMMANDS = [
    'clear_cache',
    'sync_events',
    'get_medium_favicons'
]


class BackofficeView(View):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(BackofficeView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        context = {
            'commands': COMMANDS
        }
        return render(request, 'reset_cache.html', context)

    def post(self, request):
        value = request.POST.get('command_name', '')
        if value not in COMMANDS:
            messages.add_message(request, messages.WARNING, 'Wrong data key')
            return redirect(reverse('backoffice.clear_cache'))

        t = Thread(name=f'Command Thread - {value}', target=call_command, args=(value,))
        t.setDaemon(True)
        t.start()
        messages.add_message(request, messages.INFO, f'{value} command run!')
        return redirect(reverse('backoffice.clear_cache'))
