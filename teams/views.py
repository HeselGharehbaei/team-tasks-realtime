from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_spectacular.utils import extend_schema, OpenApiExample
from .serializers import TeamSerializer
from .models import Team


class TeamCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=TeamSerializer,
        responses={201: TeamSerializer},
        summary="ایجاد تیم جدید",
        description="کاربر می‌تواند تیم جدید بسازد و اعضا را با ID مشخص کند.",
        tags=['Teams'],
        examples=[
            OpenApiExample(
                "نمونه درخواست ایجاد تیم",
                value={
                    "name": "تیم توسعه",
                    "members":["2", "3"]
                },
                request_only=True
            ),
            OpenApiExample(
                "نمونه پاسخ ایجاد تیم",
                value={
                    "id": 1,
                    "name": "تیم توسعه",
                    "members_info": [
                        {"id": 1, "username": "ali"},
                        {"id": 2, "username": "sara"}
                    ]
                },
                response_only=True
            ),
        ]
    )
    def post(self, request):
        serializer = TeamSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        team = serializer.save()
        return Response(TeamSerializer(team).data, status=status.HTTP_201_CREATED)


class TeamListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # فقط تیم‌هایی که کاربر عضو آن‌هاست
        teams = Team.objects.filter(members=request.user)
        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data)