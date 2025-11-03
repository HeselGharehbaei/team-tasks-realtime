from django.urls import path
from .views import TeamCreateView

urlpatterns = [
    path('', TeamCreateView.as_view(), name='create-team'),
]
