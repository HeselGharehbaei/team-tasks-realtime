from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import TaskSerializer
from .models import Task
from django.contrib.auth.models import User
import re
from .permissions import IsTeamMember

class TaskCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTeamMember]

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save(creator=request.user)

        # استخراج @mention ها
        mentions = re.findall(r'@(\w+)', task.description)
        tagged_users = []
        for username in mentions:
            try:
                user = User.objects.get(username=username)
                tagged_users.append(user)
            except User.DoesNotExist:
                continue
        if tagged_users:
            task.tagged_users.add(*tagged_users)
            # TODO: ارسال نوتیفیکیشن بلادرنگ

        return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)


class TaskListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(team__members=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class TaskDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTeamMember]

    def get_object(self, pk):
        try:
            return Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return None

    def get(self, request, pk):
        task = self.get_object(pk)
        if not task:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, task)
        serializer = TaskSerializer(task)
        return Response(serializer.data)
