from openai import OpenAI
import json
from django_backend.constants import CATEGORIES_MAP, LINKEDIN_INDUSTRY_LABELS_IDS, SUB_CATEGORY_CHOICES
import http.client
from django.conf import settings


client = OpenAI(api_key=settings.OPENAI_API_KEY)


# with open("our_industry_tags.txt", 'r') as file:
#     out_industries = json.load(file)

with open("linkedin_industry_tag.txt", 'r') as file:
    linkedin_industries = json.load(file)


with open("our_industry_tags.txt", 'r') as file:
    our_industries = json.load(file)


def get_search_filters(text):
    initial_filters = get_initial_search_filters(text)

    final_list = []

    for i in initial_filters.get("linkedin-industry-category"):
        temp_list = linkedin_industries.get(i)
        temp_list = [j.get("Label") for j in temp_list]
        final_list += temp_list

    our_industries_list = []

    for i in initial_filters.get("primary-category"):
        temp_list = our_industries.get(i)
        our_industries_list += temp_list

    
    final_industries = get_final_industries("\n".join(final_list),  text)
    top_two_industries = sorted(final_industries['matching_industries'], key=lambda x: x['confidence'], reverse=True)[:2]

    new_industries = get_final_industries("\n".join(our_industries_list), text)
    top_new_industries = sorted(new_industries['matching_industries'], key=lambda x: x['confidence'], reverse=True)[:2]


    industry_ids = [LINKEDIN_INDUSTRY_LABELS_IDS.get(i.get("label")) for i in top_two_industries]

    initial_filters["current_industries"] = [i.get("label") for i in top_two_industries]
    initial_filters["new_industries_tags"] = [i.get("label") for i in top_new_industries]

    return initial_filters, industry_ids



def get_jobs(title_type, title_sub_type, size, final_industries, country):
    conn = http.client.HTTPSConnection("api.theirstack.com")
    headers = {
        'Content-Type': "application/json",
        'Authorization': "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjYxOmFmOjlhOmEzOjE0OjYzOjJlOjE5OmEwOjg1OmNjOmY3OjU2OmU4OjE0OjU2IiwidHlwIjoiSldUIn0.eyJhdWQiOltdLCJhenAiOiJhNGI4MTIwZTY2YmM0ZTc5ODUzMmQyMDk4NWZjY2ViOSIsImVtYWlsIjoiZGhydXZqYWdsYW4yQGdtYWlsLmNvbSIsImV4cCI6MTcyNzIwMzQyNiwiaWF0IjoxNzI2MzM5NDI1LCJpc3MiOiJodHRwczovL2FjY291bnQudGhlaXJzdGFjay5jb20iLCJqdGkiOiJkNGE0OGY1MC1mOWVmLTQ5ZGEtYmFmYy01YzdmMzczNWIxNWYiLCJvcmdfY29kZSI6Im9yZ185MzQ5MTIxZTU1MSIsIm9yZ19uYW1lIjoiRGVmYXVsdCBPcmdhbml6YXRpb24iLCJwZXJtaXNzaW9ucyI6W10sInNjcCI6WyJvcGVuaWQiLCJwcm9maWxlIiwiZW1haWwiLCJvZmZsaW5lIl0sInN1YiI6ImtwXzU4NGIxZmNmMDRjZDQ3OGRhYmE2NmM4NTNmZjdhYWU1In0.HR996XwEsPpIb_CEZTm8jl7_wE7g5bzRZNmp8495iVMAMcxFxcPbXAMsvLwfJ0ng49pS3QZRJ1SVEkrf5N6WN43T54zbeK_dSESIeVqpfnRK706Rvbu8mnFqFLpgpo2iYaUFU2XYG_4OAISvDMOeHSVjIjNkZzRzEn6gkgXg-RJqdNMAhNwD0Ev5ND4eKwLmke32FmcsTtp26xyhXxcNBEBef1FD_rWiw4hqagspREqNW-qZ-BqiE5gNPE9BlpKjQMfjLWi2w0NWSWCn3-VVkMDHOPwhdnuqxuAghnxK2Yd6Eo9m0zD36PP5wi5L6PYneKi3EuLHN2F4pZR-ZxuQ7g"
    }

    data = call_parameters(final_industries, size, title_type, title_sub_type, country)
    conn.request("POST", "/v1/jobs/search", json.dumps(data), headers)

    res = conn.getresponse()
    data = res.read()

    return json.loads(data.decode("utf-8"))["data"]



####### Sub - Helpers NOT TO BE CALLED FROM ANY OTHER FILE


def get_initial_search_filters(text):
    response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
        "role": "system",
        "content": [
            {
            "type": "text",
            "text": "You have to provide people search filters based on what person has said in JSON format.\n\n\n{\n\"linkedin-industry-category\" : ### give a list of all  linkedin category that might fit the description list [ \"accommodation_services\", \"administrative_and_support_services\", \"construction\", \"consumer_services\", \"education\", \"entertainment_providers\", \"farming_ranching_forestry\", \"financial_services\", \"government_administration\", \"holding_companies\", \"hospitals_and_health_care\", \"manufacturing\", \"oil_gas_and_mining\", \"professional_services\", \"real_estate_and_equipment_rental_services\", \"retail\", \"technology_information_and_media\", \"transportation_logistics_supply_chain_and_storage\", \"utilities\", \"wholesale\" ],\n\"primary-category\": give a list of all  primary category that might fit the description   ['aerospace-&-defense', 'automotive', 'transportation-&-logistic', 'business-services', 'construction-and-real-estate', 'consumer-products-&-services', 'education', 'energy-&-utilities', 'financial-services-&-insurance', 'government', 'healthcare', 'hospitality', 'industrial-&-manufacturing', 'media-&-entertainment', 'advertising-&-marketing', 'primary-industries', 'retail-&-e-commerce', 'hardware-and-robotics', 'software-or-ai-technology', 'telecommunications', 'other-services']\n\"country\":  ###  return the 2 digit country code this hsould always be present,\n\"location\": ## city name if mentioned,\n\"company_size\": ## Array of type (don't return size in number just give the tag) i.e emerging (<50), small (50-200), mid (201-1000), large (1001-5000), enterprise (5000+), \n\"company_funding_stage\": ## array of type (pre-seed, seed, series-a, series-b, series-c, series-d+)\n} \n\nAdd everything as null which is not mentioned, Just return Json"
            }
        ]
        },
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": text
            }
        ]
        }
    ],
    temperature=1,
    max_tokens=2048,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    response_format={
        "type": "json_object"
    }
    )

    return json.loads(response.choices[0].message.content)


def get_final_industries(tags, text):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
            "role": "system",
            "content": [
                {
                "type": "text",
                "text": "Please provide industry tags that fit the company description from the list of categories \n\ncategories:\n"+ tags + "\n\n\n\nreturn Json format\n{\n\"matching_industries\": [] array of industries matching with each object {\"label\" and \"confidence\"}\n}\n\n"
                }
            ]
            },
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": text
                }
            ]
            }
        ],
        temperature=1,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={
            "type": "json_object"
        }
        )
    
    return json.loads(response.choices[0].message.content)


def get_min_max_size(target_categories):
    size_mapping = {
        "emerging": (0, 49),
        "small": (50, 200),
        "mid": (201, 1000),
        "large": (1001, 5000),
        "enterprise": (5001, 100000)
    }
    
    min_size = 100000
    max_size = 0
    
    for category in target_categories:
        if category.lower() in size_mapping:
            min_size = min(min_size, size_mapping[category][0])
            max_size = max(max_size, size_mapping[category][1])
    
    if min_size == float('inf') and max_size == 0:
        return None  # No valid categories found
    else:
        return min_size, max_size


def get_job_title_list(title_type, title_sub_type):
    if title_sub_type:
        return SUB_CATEGORY_CHOICES.get(title_sub_type)
    elif title_type:
        final_roles = []
        for i in CATEGORIES_MAP.get(title_type):
            final_roles += SUB_CATEGORY_CHOICES.get(i, [])
        return final_roles
    
    return []


def call_parameters(ids, size, title_type, title_sub_type, country):
    data = {"order_by": [
    {
      "desc": True,
      "field": "date_posted"
    }],
    "page": 0,
    "limit": 10,
    "job_country_code_or" : ["US"],
    "posted_at_max_age_days": 2,
    "industry_id_or": ids
    }
    if country and country != "US":
        data["job_country_code_or"] = ['IN']
    if size:
        min, max = get_min_max_size(size)
        data["min_employee_count"] = min
        data["max_employee_count"] = max
    if title_type != "AL":
        data["job_title_or"] = get_job_title_list(title_type, title_sub_type)

    return data