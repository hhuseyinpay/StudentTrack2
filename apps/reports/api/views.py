from django.urls import reverse
from django.db.models import Sum
from rest_framework import status
from rest_framework.generics import views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from accounts.api.permissions import IsTeacherExecutiveAdmin
from .serializer import DailyStudyReportGeneratorSerialzier
from daily_study.models import DailyStudy, Study
from accounts.models import Profile, Groups
from .excel_generator import ExcelGenerator


class DailyStudyReportGeneratorAPIView(views.APIView):
    permission_classes = (IsAuthenticated, IsTeacherExecutiveAdmin)

    def post(self, request):
        serializer = DailyStudyReportGeneratorSerialzier(data=request.data)
        serializer.is_valid(raise_exception=True)
        profiles = Profile.objects.filter(related_region=serializer.validated_data['region'],
                                          group=serializer.validated_data['group'],
                                          is_teacher=serializer.validated_data['include_teacher'],
                                          is_student=True)
        # print(profiles)
        excel = ExcelGenerator("daily_study_mountly_universite.xlsx", "PUANLAR", "uni_test.xlsx", 5, 2, 5, 1, 4)
        for p in profiles:
            # bulunduğu sınıf ve username 2, 3 yazılıyor
            excel.write_current_row(2, p.classroom.name)
            excel.write_current_row(3, p.user.username)
            weeks = serializer.validated_data['weeks']

            for i in range(0, 4):
                dailystudies = DailyStudy.objects.filter(user=p.user,
                                                         created_day__gte=weeks[i]['begining'],
                                                         created_day__lte=weeks[i]['end'])

                studies = Study.objects.filter(studies__in=dailystudies)

                # daha dinamik tatlı bişey yapılabilir. id'ye bağımlı olarak yaptım şuanda.
                for course in Groups.objects.get(id=2).courses.all().order_by("id"):
                    # excel'e haftalık derslerin toplamları şeklinde yazılacak.
                    excel.write_current_position(
                        studies.filter(course=course).aggregate(total=Sum('amount'))['total'] or 0
                    )

                excel.next_column_block()
            excel.next_row()
        excel.save()

        url = request.build_absolute_uri(reverse('report_download', kwargs={"report_name": excel.output_filename}))
        return Response({"url": url}, status=status.HTTP_200_OK)
