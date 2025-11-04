from django.urls import path
from .views import TaskCreateView, TaskListView, TaskDetailView, TaskAssignView, TaskMentionView

urlpatterns = [
    path('', TaskListView.as_view(), name='task-list'),
    path('create/', TaskCreateView.as_view(), name='task-create'),
    path('<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('<int:pk>/assign/', TaskAssignView.as_view(), name='task-assign'),
    path('<int:pk>/mention/', TaskMentionView.as_view(), name='task-mention'),
]
