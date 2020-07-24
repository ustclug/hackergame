from rest_framework.views import APIView
from rest_framework.response import Response

from contest.models import Stage, Pause
from contest.serializer import StageSerializer, PauseSerializer


class StageAPI(APIView):
    def get(self, request):
        stage = Stage.objects.get()
        stage_serializer = StageSerializer(stage)
        pause_serializer = PauseSerializer(Pause.objects.all(), many=True)
        data = stage_serializer.data
        data['pause'] = pause_serializer.data
        return Response(data)


class CurrentStageAPI(APIView):
    def get(self, request):
        return Response({"status": Stage.objects.current_status})
