import base64
from datetime import datetime, timezone
from email.mime.text import MIMEText
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework.decorators import api_view
from django_backend.constants import CATEGORY_MAPPING, SUB_CATEGORIES_MAPPING
from django_backend.tasks import add, add_company_details
from django_backend.utils.base import get_company_person_info
from django_backend.models import Company, CompanyTriggerSegment, JobSearchResult, PeopleJobEmailTask, Person
from django_backend.serializers import CompanySerializer, CompanyTriggerSegmentSerializer, CreateTriggerSerializer, EmailSerializer, JobSearchResultSerializer, PeopleJobEmailTaskSerializer, PersonSerializer
from rest_framework.response import Response
from rest_framework import generics
from django.db import transaction
from django.conf import settings
from rest_framework import status
from django_backend.utils.email_utils import get_emails, update_email_using_prompt
from django_backend.utils.trigger_utils import get_jobs, get_search_filters
from django_backend.utils.peoplesearch_utils import create_people_task_objects, get_search_results
import google_auth_oauthlib.flow
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


# Create your views here.

##### Getting Started Page

@api_view(['POST'])
def create_company_user(request):
    data= request.data
    serializer = EmailSerializer(data=data)
    if (serializer.is_valid()):
        email= serializer.validated_data.get("email")
        person=Person.objects.filter(email=email)
        if person.exists():
            person=person[0]
        else:
            person = get_company_person_info(email)
        
        if (person.company and person.company.domain and not person.company.details_fetched):
                url = "https://" + person.company.domain
                add_company_details.delay(url, person.company.id)

        return Response(PersonSerializer(person).data)

    return Response(status=400, data=serializer.errors)

def create_user_view(request):
    # Render the create_user.html template
    return render(request, 'create_user.html')

####### Home Page
def create_home_view(request):
    # Render the create_user.html template
    return render(request, 'home.html')

class TriggersListAPIView(generics.ListAPIView):
    serializer_class = CompanyTriggerSegmentSerializer

    def get_queryset(self):
        company_id = self.kwargs['company_id']
        return CompanyTriggerSegment.objects.filter(company_id=company_id)
    
class CompanyAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = CompanySerializer
    queryset = Company

@api_view(['POST'])
def create_new_trigger(request):
    data= request.data
    serializer = CreateTriggerSerializer(data=data)
    if (serializer.is_valid()):
        category = CATEGORY_MAPPING.get(serializer.validated_data.get("category"))
        sub_category=None

        if serializer.validated_data.get("subcategory"):
            sub_category = SUB_CATEGORIES_MAPPING.get(serializer.validated_data.get("subcategory"))
        
        trigger = CompanyTriggerSegment.objects.create(company_id=serializer.validated_data.get("company"), role_category=category, sub_category=sub_category)

        return Response(data={
            "id": trigger.id
        })

    return Response(status=400, data=serializer.errors)

##### TRIGGER Page


@api_view(['GET'])
def trigger_detail(request, trigger_id):
    trigger = CompanyTriggerSegment.objects.get(id=trigger_id)

    filters = trigger.raw_filters if trigger.raw_filters else {}

    data = {
        "id": trigger.id,
        "message": trigger.message,
        "role_category": trigger.role_category,
        "sub_category": trigger.sub_category,
        "industry": filters.get("current_industries"),
        "company_size": filters.get("company_size"),
        "country": filters.get("country"),
        "person_job_role": trigger.person_job_role,
        "person_job_level": trigger.person_job_level
    }


    return Response(status=200, data=data)

def trigger_view(request, trigger_id):
    trigger = CompanyTriggerSegment.objects.get(id=trigger_id)
    filters = None
    context = {
    'id': trigger.id,
    'message': trigger.message,
    'role_category': trigger.get_role_category_display(),
    'sub_category':trigger.get_sub_category_display,
    'search_filters': filters,
    }

    return render(request, 'trigger_view.html', context)

@api_view(['POST'])
def get_just_filters(request):

    print("get_just_filters")
    data= request.data
    message = data.get("message")
    company_id = data.get("company_id")
    filters, industry_ids = get_search_filters(message)

    if filters:
        trigger = CompanyTriggerSegment.objects.create(message=message, raw_filters=filters, industry_ids=industry_ids, company_id=company_id)
        return Response(status=200, data={
                "id": trigger.id,
                "industry": filters.get("current_industries"),
                "company_size": filters.get("company_size"),
                "country": filters.get("country")
            })
    else:
        return Response(status=400)



@api_view(['POST'])
def get_filters(request, trigger_id):
    trigger = CompanyTriggerSegment.objects.get(id=trigger_id)
    data= request.data
    message = data.get("message")
    role_category = data.get("role_category")
    sub_category = data.get("sub_category")
    person_job_role = data.get("person_job_role")
    person_job_level = data.get("person_job_level")

    
    if role_category:
        trigger.role_category = role_category
    
    if sub_category:
        trigger.sub_category = sub_category
    
    if person_job_role:
        trigger.person_job_role = person_job_role
    
    if person_job_level:
        trigger.person_job_level = person_job_level
    
    if message:
        trigger.message=message
        filters, industry_ids = get_search_filters(message)
        trigger.raw_filters = filters
        trigger.industry_ids = industry_ids
    else:
        filters = trigger.raw_filters
    

    if filters:
        trigger.save()

        return Response(status=200, data={
                "id": trigger.id,
                "message": trigger.message,
                "role_category": trigger.role_category,
                "sub_category": trigger.sub_category,
                "industry": filters.get("current_industries"),
                "company_size": filters.get("company_size"),
                "country": filters.get("country"),
                "person_job_role": trigger.person_job_role,
                "person_job_level": trigger.person_job_level
            })
    else:
        return Response(status=400)

@api_view(['GET'])
def search_jobs(request, trigger_id):
    trigger = get_object_or_404(CompanyTriggerSegment, id=trigger_id)

    job_objects = JobSearchResult.objects.filter(trigger_segment=trigger)

    # If no jobs are found for the trigger segment, fetch and store them
    if not job_objects.exists() or (trigger.last_job_fetch and (datetime.now() - trigger.last_job_fetch).days > 2):
        trigger.last_job_fetch = datetime.now()
        trigger.save()
        try:
            jobs = get_jobs(
                trigger.role_category, 
                trigger.sub_category, 
                trigger.raw_filters.get("company_size"), 
                trigger.industry_ids,
                trigger.raw_filters.get("country")
            )

            # Create JobSearchResult objects in bulk
            job_results = [
                JobSearchResult(trigger_segment=trigger, raw_data=job, company_url=job.get("company_object", {}).get("url", "").replace("https://", ""))
                if job.get("company_object", {}).get("url", "") else None for job in jobs
            ]
            job_results = [job for job in job_results if job is not None]

            with transaction.atomic():
                JobSearchResult.objects.bulk_create(job_results)

            # Fetch the newly created job objects
            job_objects = JobSearchResult.objects.filter(trigger_segment=trigger)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    serializer = JobSearchResultSerializer(job_objects, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def base_mail(request, trigger_id):
    trigger = get_object_or_404(CompanyTriggerSegment, id=trigger_id)
    job_search_result = JobSearchResult.objects.filter(trigger_segment=trigger).order_by('id').first()

    data = job_search_result.raw_data
    add.delay(1, 2)

    if trigger.default_mail:
        return Response(status=200, data=trigger.default_mail)

    emails = get_emails(trigger.company.name, trigger.company.detailed_descrption,
                        "\n".join(trigger.company.problem_statement),
                        data.get("job_title"), data.get("seniority"), data.get("company"), data.get("company_object", {}).get("long_description"))
    
    if emails:
        trigger.default_mail = emails
        job_search_result.mail = emails
        trigger.save()
        job_search_result.save()
    
    return Response(status=200, data=emails)





@api_view(['POST'])
def update_email(request, trigger_id):
    trigger = get_object_or_404(CompanyTriggerSegment, id=trigger_id)
    job_search_result = JobSearchResult.objects.filter(trigger_segment=trigger).order_by('id').first()

    data = request.data
    trigger.default_mail = data
    job_search_result.mail = data
    trigger.save()
    job_search_result.save()

    return Response(status=200, data=data)


@api_view(['POST'])
def prompt_update_email(request, trigger_id):
    trigger = get_object_or_404(CompanyTriggerSegment, id=trigger_id)
    data = request.data
    prompt = data.get("prompt")
    new_email = update_email_using_prompt(trigger.default_mail, prompt)
    trigger.default_mail = new_email
    trigger.save()

    return Response(status=200, data=new_email)

@api_view(['POST'])
def find_people_gen_email(request, trigger_id):
    trigger = get_object_or_404(CompanyTriggerSegment, id=trigger_id)
    urls = list(set(list(JobSearchResult.objects.filter(trigger_segment=trigger).values_list("company_url", flat=True))))
    people = create_people_task_objects(trigger.person_job_role, trigger.person_job_level, urls)
    return Response(status=200)
    

@api_view(['POST'])
def update_prospect_email(request, pk):
    email_task = get_object_or_404(PeopleJobEmailTask, id=pk)
    data = request.data


    email_task.mail_content=eval(data.get("mail_content"))
    email_task.save()
    
    return Response(status=200, data=email_task)


class ProspectEmailListAPIView(generics.ListAPIView):
    serializer_class = PeopleJobEmailTaskSerializer

    def get_queryset(self):
        trigger_id = self.kwargs['trigger_id']
        return PeopleJobEmailTask.objects.filter(trigger_segment_id=trigger_id).order_by('-created_at')
    

#### update this to send email
@api_view(['POST'])
def send_email(request, pk):
    email_task = get_object_or_404(PeopleJobEmailTask, id=pk)

    if 'google_credentials' not in request.session:
        return redirect('google_auth_for_email')

    # Load user's credentials from the session
    creds_data = request.session['google_credentials']
    creds = Credentials(
        creds_data['token'],
        refresh_token=creds_data['refresh_token'],
        token_uri=creds_data['token_uri'],
        client_id=creds_data['client_id'],
        client_secret=creds_data['client_secret'],
        scopes=creds_data['scopes']
    )

    # Build Gmail API service
    service = build('gmail', 'v1', credentials=creds)

    # Create email message
    message = MIMEText('This is a test email sent via Gmail API.')
    message['to'] = 'recipient@example.com'
    message['from'] = 'your_user_email@example.com'
    message['subject'] = 'Test Subject'

    # Encode the message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    body = {'raw': raw_message}

    # Send email
    try:
        message = service.users().messages().send(userId='me', body=body).execute()
    except Exception as e:
        pass


    email_task.send=True
    email_task.save()
    
    return Response(status=200)


def google_oauth2callback(request):
    state = request.session['state']

    flow = Flow.from_client_secrets_file(
        'path_to_your_credentials.json',
        scopes=['https://www.googleapis.com/auth/gmail.send'],
        state=state
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

    # Save the credentials in the session
    creds = flow.credentials
    request.session['google_credentials'] = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

    return redirect('send_email')


def google_auth_for_email(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'path_to_your_credentials.json',
        scopes=['https://www.googleapis.com/auth/gmail.send']
    )
    
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

    authorization_url, state = flow.authorization_url(
        access_type='offline',  # Ensures you get a refresh token
        include_granted_scopes='true'
    )

    # Store the state in session for callback
    request.session['state'] = state
    return HttpResponseRedirect(authorization_url)