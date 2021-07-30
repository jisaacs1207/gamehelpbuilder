from django.urls import path, reverse_lazy
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    path('', RedirectView.as_view(url=reverse_lazy('admin:index'))),
    path('search/<query>', views.search, name='search'),
    path('lookup/<query>', views.lookup, name='lookup'),
]