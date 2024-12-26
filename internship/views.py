from django.http import JsonResponse
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
    parser_classes,
)
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework import status
from .models import InternshipRegistration, Offers, InternshipNotice, InternshipAcceptance
from .serializers import (
    InternshipRegistrationSerializer,
    OffersSerializer,
    InternshipNoticeSerializer,
    InternshipAcceptanceSerializer,
    InternshipApplicationSerializer,
)
from rest_framework.permissions import IsAuthenticated
# from base.models import User
from django.views.decorators.csrf import csrf_exempt
# from student.models import Student
from .models import InternshipApplication
from uuid import uuid4
# from student.serializers import StudentSerializer
from rest_framework.exceptions import NotFound
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from uuid import uuid4


@api_view(["POST"])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def create_company_with_offers(request):
    try:
        data = JSONParser().parse(request)

        # Create CompanyRegistration
        company_data = data.get("company")
        company_serializer = InternshipRegistrationSerializer(data=company_data)
        if company_serializer.is_valid():
            company = company_serializer.save()
        else:
            return JsonResponse(
                company_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        # Create Offers
        offers_data = data.get("offers", [])
        for offer_data in offers_data:
            offer_data["company"] = company
            try:
                Offers.objects.create(**offer_data)
            except:
                pass

        return JsonResponse(
            {"message": "Company and related offers created successfully!"},
            status=status.HTTP_201_CREATED,
        )
    except Exception as e:
        return JsonResponse(
            {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def get_company_with_offers(request, pk=None):
    try:
        if pk:
            # Retrieve a specific company and its offers
            company = InternshipRegistration.objects.get(id=pk)
            company_serializer = InternshipRegistrationSerializer(company)
            offers = Offers.objects.filter(company=company)
            offers_serializer = OffersSerializer(offers, many=True)

            return JsonResponse(
                {
                    "company": company_serializer.data,
                    "offers": offers_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            # Retrieve all companies with their offers
            companies = InternshipRegistration.objects.all()
            response_data = []
            for company in companies:
                company_serializer = InternshipRegistrationSerializer(company)
                offers = Offers.objects.filter(company=company)
                offers_serializer = OffersSerializer(offers, many=True)

                response_data.append(
                    {
                        "company": company_serializer.data,
                        "offers": offers_serializer.data,
                    }
                )

            return JsonResponse(response_data, safe=False, status=status.HTTP_200_OK)
    except InternshipRegistration.DoesNotExist:
        return JsonResponse(
            {"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return JsonResponse(
            {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def get_all_companies(request):
    try:
        companies = InternshipRegistration.objects.all()
        company_data = []
        for company in companies:
            company_serializer = InternshipRegistrationSerializer(company)
            offers = Offers.objects.filter(company=company)
            offers_serializer = OffersSerializer(offers, many=True)
            company_data.append(
                {"company": company_serializer.data, "offers": offers_serializer.data}
            )
        return JsonResponse(company_data, safe=False, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse(
            {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def create_notice(request, pk):
    try:
        company = InternshipRegistration.objects.get(id=pk)
        data = JSONParser().parse(request)
        notice = data.get("notice")
        notice["company"] = company
        InternshipNotice.objects.create(**notice)
        return JsonResponse(
            {"message": "Notice created successfully"}, status=status.HTTP_201_CREATED
        )
    except Exception as e:
        print(e)
        return JsonResponse(
            {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def get_notice(request, pk):
    try:
        notice = InternshipNotice.objects.get(id=pk)
        notice = InternshipNoticeSerializer(notice)
        return JsonResponse({"notice": notice.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse(
            {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def job_application(request, pk):
    try:
        # user = User.objects.get(email=request.user.email)
        # student = Student.objects.get(user=user)
        company = InternshipRegistration.objects.get(pk=pk)
        InternshipApplication.objects.create(company=company, id=uuid4())
        return JsonResponse(
            {"success": "Job application submitted successfully"},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return JsonResponse(
            {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# @api_view(["GET"])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
# def get_student_application(request, uid):
#     try:
#         student = Student.objects.get(uid=uid)
#     except Student.DoesNotExist:
#         raise NotFound("Student not found.")

#     serializer = StudentSerializer(student)
#     return JsonResponse({"student": serializer.data}, safe=False)


@api_view(["GET"])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
def get_all_applied_students(request, pk):
    try:
        company = InternshipApplication(pk=pk)
        students = InternshipApplicationSerializer(company)
        print(students.data)
        return JsonResponse({"students": students.data})
    except Exception as e:
        print(e)
        return JsonResponse(
            {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
# @authentication_classes([SessionAuthentication, BasicAuthentication])
# @permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def create_job_acceptance(request):
    # user = User.objects.get(email=request.user.email)
    # if not user:
    #     return JsonResponse(
    #         {"error": "Failed to find user"}, status=status.HTTP_404_NOT_FOUND
    #     )
    # student = Student.objects.get(user=user)
    print(request.data["company_name"])
    company = None
    required_fields = ["type", "salary", "position"]
    for field in required_fields:
        if field not in request.data:
            return JsonResponse(
                {"error": f"Missing required field: {field}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    if "offer_letter" not in request.FILES:
        return JsonResponse(
            {"error": "Offer letter file is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    job_acceptance = InternshipAcceptance.objects.create(
        id=uuid4(),
        # student=student,
        company=None,
        company_name=request.data["company_name"][
            0
        ],  # Assuming company has company_name field
        offer_letter=request.FILES["offer_letter"],
        type=request.data["type"][0],
        salary=float(request.data["salary"][0]),
        position=request.data["position"][0],
        isVerified=False,  # Default value
    )
    return JsonResponse({"success": "Job application created"})


# @authentication_classes([SessionAuthentication, BasicAuthentication])
@api_view(["GET"])
def get_job_acceptance_by_id(request, pk):
    try:
        job_acceptance = InternshipAcceptance.objects.get(id=pk)
    except InternshipAcceptance.DoesNotExist:
        return JsonResponse(
            {"error": "Job acceptance not found."}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = InternshipAcceptanceSerializer(job_acceptance)
    return JsonResponse(serializer.data)


@api_view(["GET"])
def get_jobs_by_company_name(request, company_name):
    jobs = InternshipAcceptance.objects.filter(company_name=company_name)
    if not jobs.exists():
        return JsonResponse(
            {"error": "No jobs found for this company name."},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = InternshipAcceptanceSerializer(jobs, many=True)
    return JsonResponse(serializer.data)
