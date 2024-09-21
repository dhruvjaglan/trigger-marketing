import requests
from django.conf import settings
import json
import logging
from django_backend.models import Company, Person

logger = logging.getLogger(__name__)


def get_company_person_info(email):
    url="https://person-stream.clearbit.com/v2/combined/find?email="+email

    payload={}
    auth_token='Bearer ' + settings.CLEARBIT_API_KEY
    headers={
    'Authorization': auth_token
    }

    response=requests.request("GET", url, headers=headers, data=payload)

    company=None
    person=None
    
    if response.json()['company']:
        data=response.json()['company']
        try:
            companies = Company.objects.filter(domain=data['domain'])
            if companies.exists():
                company = companies[0]
            else:
                company=Company(
                        name=data.get('name', 'NA'),
                        legal_name=data.get('legalName', 'NA'),
                        description=data.get('description', 'NA'),
                        raw_data=data,
                        sector=data.get('category', {}).get("sector"),
                        industry=data.get('category', {}).get("industry"),
                        domain=data['domain'],
                        tags=data['tags'],
                        founded_year=data['foundedYear'],
                        timezone=data['timeZone'],
                        logo=data['logo']
                    )
                company.save()
        except Exception as e:
            logger.error(e)


    if response.json()['person']:
        data=response.json()['person']
        person=Person(
            full_name=data.get('name', {}).get("fullName", 'NA'),
            first_name=data.get('name', {}).get("givenName", 'NA'),
            last_name=data.get('name', {}).get("familyName", 'NA'),
            title=data.get('employment', {}).get("title", 'NA'),
            seniority=data.get('employment', {}).get("seniority", 'NA'),
            email=email,
            bio=data.get('bio'),
            site=data.get('site', None),
            avatar=data.get('avatar', None),
            linkedin_handle=data.get('linkedin', {}).get('handle', None),
            raw_data=data,
            company=company
        )
        person.save()
    else:
        person=Person(email=email,company=company,raw_data=response.json())
        person.save()

    return person
