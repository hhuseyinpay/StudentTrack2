from django.urls import reverse
from rest_framework import status
from rest_framework.generics import views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from accounts.api.permissions import IsTeExAd
from .serializer import DailyStudyReportGeneratorSerialzier


class DailyStudyReportGeneratorAPIView(views.APIView):
    permission_classes = (IsAuthenticated, IsTeExAd)
    serializer_class = DailyStudyReportGeneratorSerialzier

    def post(self, request):
        serializer = DailyStudyReportGeneratorSerialzier(data=request.data)
        serializer.is_valid(raise_exception=True)

        file_name = "test.xlsx"

        url = request.build_absolute_uri(reverse('report_download', kwargs={"report_name": file_name}))
        return Response({"url": url}, status=status.HTTP_200_OK)
