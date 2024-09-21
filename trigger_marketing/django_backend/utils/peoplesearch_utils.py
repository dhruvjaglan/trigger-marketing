from peopledatalabs import PDLPY
from django.conf import settings
from django_backend.models import JobSearchResult, PeopleJobEmailTask
from django_backend.tasks import generate_email



def create_people_task_objects(person_job_role, person_job_level, company_urls):

    response = get_search_results(person_job_role, person_job_level, company_urls)

    for person in response.get("data", []):
        print(person)
        print(person.get("job_company_website"))
        print(person.get("job_company_website").replace("https://", "").replace("www.", ""))
        job_result = JobSearchResult.objects.filter(company_url__icontains=person.get("job_company_website"))

        email = person.get("work_email") if person.get("work_email") else person.get("recommended_personal_email")

        
        if job_result.exists() and email:
            task = PeopleJobEmailTask.objects.create(
                prospect_name=person.get("full_name"),
                prospect_email=email,
                prospect_details=person,
                prospect_title=person.get("job_title"),
                prospect_company_name=person.get("job_company_name"),
                company_url=person.get("job_company_website").replace("https://", "").replace("www.", ""),
                job=job_result.first(),
                trigger_segment=job_result.first().trigger_segment,
            )
            try:
                # generate_email.delay(task.id)
                print("Generated email for ", task.prospect_name)
            except Exception as e:
                print(e)
        else:
            print("No job result or email found for ", person.get("full_name"), person.get("job_company_website"))

def get_search_results(person_job_role, person_job_level, company_urls):
    client = PDLPY(
        api_key=settings.PEOPLE_DATA_LABS_API_KEY,
    )

    filters, query = get_formatted_query(person_job_role, person_job_level, company_urls)

    print(query)

    PARAMS = {
        'dataset': 'email',
        'sql': query,
        'size': 3,
        'pretty': True
    }
    
    response = client.person.search(**PARAMS).json()

    print(response)

    return response

def get_formatted_query(person_job_role, person_job_level, company_urls):
    sql_query = "SELECT * FROM person WHERE "
    filters = {}
    queries = []
    level_mapping = {'x': ['cxo', 'director', 'manager', 'owner', 'partner'],
    'm': ['manager', 'senior', 'vp'],
    'e': ['entry']
    }
    role_mapping = {'c': ['support'],
                    'd': ['creative', 'product'],
                    'e': ['engineering', 'analyst'],
                    'f': ['finance'],
                    'h': ['human_resources'],
                    'l': ['legal'],
                    'm': ['marketing'],
                    'o': ['operations', 'fulfillment'],
                    'p': ['partnerships'],
                    's': ['sales', 'sales_engineering']
    }
    if person_job_role and person_job_role.lower() != 'a':
        formatted_roles = role_mapping.get(person_job_role.lower(), [])
        filters['job_title_role'] = formatted_roles
        formatted_roles = ', '.join("'" + role.lower() + "'" for role in formatted_roles)
        if formatted_roles:
            queries.append("job_title_role IN ("+ formatted_roles + ")")
    if person_job_level:
        formatted_levels = level_mapping.get(person_job_level.lower(), [])
        filters['job_title_levels'] = formatted_levels
        formatted_levels = ', '.join("'" + level.lower() + "'" for level in formatted_levels)
        if formatted_levels:
            queries.append("job_title_levels IN ("+ formatted_levels + ")")
    if company_urls:
        # remove None
        company_urls = [company for company in company_urls if company is not None]
        filters['job_company_website'] = company_urls
        formatted_companies = ', '.join("'" + company.lower().replace("https://", "").replace("www.", "") + "'" for company in company_urls)
        if formatted_companies:
            queries.append("job_company_website IN ("+ formatted_companies + ")")
    joined_queries= " AND ".join(queries)
    sql_query += joined_queries + ";"
    return filters, sql_query