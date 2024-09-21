import json
import logging
from celery import shared_task
from django.conf import settings
from openai import OpenAI

from django_backend.models import Company, PeopleJobEmailTask

logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=settings.OPENAI_AI_KEY,
)

def fill_template_general(variables, template):
    filled_template = []
    for entry in template:
        filled_entry = entry.copy()
        filled_entry['content'] = []
        for item in entry['content']:
            if isinstance(item, dict) and 'text' in item:
                filled_text = item['text']
                for placeholder, value in variables.items():
                    if value:
                        filled_text = filled_text.replace(f"{{{placeholder}}}", value)
                filled_entry['content'].append({
                    "type": item["type"],
                    "text": filled_text
                })
            else:
                filled_entry['content'].append(item)
        filled_template.append(filled_entry)
    return filled_template

@shared_task
def add(x, y):
    print("Adding ", x, y)
    return x + y

@shared_task
def add_company_details(company_link, company_id):
    company = Company.objects.get(id=company_id)
    # links = get_all_links(company_link, company.domain, 3)
    # formatted_links = format_links(str(links))
    # company.links = formatted_links
    # if formatted_links and formatted_links.get("customer_case_study"):
    #     for link in formatted_links.get("customer_case_study"):
    #         get_case_study(link, company)
    
    company_details = get_company_details(company_link)
    if company_details:
        format_company_details(company_details, company)
    company.details_fetched = True
    company.save()

@shared_task
def generate_email(id):
    ### Todo find person
    task = PeopleJobEmailTask.objects.get(id=id)

    prospect_name = task.prospect_name
    prospect_title = task.prospect_title
    prospect_company = task.prospect_company_name
    base_email = task.trigger_segment.default_mail

    prompt =[
        {
        "role": "system",
        "content": [
            {
            "type": "text",
            "text": "Update the base mail for the client\nDon't change the objective of the mail, just update the prospect company, user related things\n\nprospect name: {prospect_name}\n\nprospect title: {prospect_title}\n\nprospect company: {prospect_company}\n\n\nbase email: {base_email}"
            }
        ]
        },
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": "Return Json in the same format as base emails"
            }
        ]
        }
    ]
    
    prompt = fill_template_general({
            "prospect_name": prospect_name,
            "prospect_title": prospect_title,
            "prospect_company": prospect_company,
            "base_email": str(base_email)
        }, prompt)



    response = client.chat.completions.create(
    model="gpt-4o",
    messages=prompt,
    temperature=1,
    max_tokens=2048,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    response_format={
        "type": "json_object"
    }
    )

    task.mail_content = response.choices[0].message.content
    task.generated = True
    task.save()
    ### todo update_email
    pass

def format_company_details(company_details, company):
    for i in range(2):
        try:
            response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                "role": "system",
                "content": [
                    {
                    "type": "text",
                    "text": "Format the following details about the company from details provided and return json structure\n\n{\n\"summary\": ### companies quick description,\n\"problem_statement\": #### array of problem statement/customer challenges,\n\"customer_list\": ### array of customer names\n}"
                    }
                ]
                },
                {
                "role": "user",
                "content": [
                    {
                    "type": "text",
                    "text": company_details
                    }
                ]
                }
            ],
            temperature=1,
            max_tokens=1169,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )
            if len(response.choices)>0 and response.choices[0].message:
                model_output = response.choices[0].message.content
                start_index = model_output.find('{')
                end_index = model_output.rfind('}') + 1
                if start_index != -1 and end_index != -1 and start_index < end_index:
                    json_string = model_output[start_index:end_index]
                    parsed_json = json.loads(json_string)
                    if parsed_json.get("summary"):
                        company.detailed_descrption = parsed_json.get("summary")
                    if parsed_json.get("problem_statement"):
                        company.problem_statement = parsed_json.get("problem_statement")
                    if parsed_json.get("customer_list"):
                        company.customer_list = parsed_json.get("customer_list")

                    company.save()
                    break
        except Exception as e:
            logger.error(e)


def get_company_details(domain):
    messages = [
    {
        "role": "system",
        "content": ("You are Marketing expert, research and provide useful detailed information about the company, what they do, Problem they are solving, Customer list/type"),
    },
    {
        "role": "user",
        "content": "Go through " +domain + "and tell me more about the company, including what problem they solve, their customer's biggest challenges and customer list ",
    },
    ]

    perplexity_client = OpenAI(api_key="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", base_url="https://api.perplexity.ai")

    # chat completion without streaming
    response = perplexity_client.chat.completions.create(
        model="llama-3.1-sonar-large-128k-online",
        messages=messages,
    )

    return response.choices[0].message.content