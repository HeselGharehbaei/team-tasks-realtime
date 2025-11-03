from django.urls import path
from .views import TeamCreateView, TeamListView

urlpatterns = [
    path('', TeamListView.as_view(), name='create-team'),
    path('create/', TeamCreateView.as_view(), name='create-team'),
]
