from openai import OpenAI
import json
from django_backend.prompt_constants import EMAIL_GENERATING
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)



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

def get_emails(company_name, summary, problems, hiring_role, seniority, prospect_company, prospect_company_summary):
    prompt = EMAIL_GENERATING
    prompt = fill_template_general({
        "company_name":  company_name,
        "summary" : summary,
        "problems": problems,
        "hiring_role": hiring_role,
        "seniority":seniority,
        "prospect_company": prospect_company,
        "prospect_company_summary": prospect_company_summary
    }, prompt)


    response = client.chat.completions.create(
    model="gpt-4o",
    messages= prompt,
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



def update_email_using_prompt(mail, comment):
    prompt =[
                {
                "role": "system",
                "content": [
                    {
                    "type": "text",
                    "text": "You are marketing assistant\nImprove the mail based on the update suggested\n\nsuggestion :\n{suggestion} "
                    }
                ]
                },
                {
                "role": "user",
                "content": [
                    {
                    "type": "text",
                    "text": "{mail}"
                    }
                ]
                },
                {
                "role": "user",
                "content": [
                    {
                    "type": "text",
                    "text": "Update the mail and return same json format as the input mail"
                    }
                ]
                }
            ]
    
    prompt = fill_template_general({
            "suggestion":  comment,
            "mail" : str(mail),
        }, prompt)
    
    print(prompt)
    
    response = client.chat.completions.create(
            model="gpt-4o",
            messages= prompt,
            temperature=0,
            max_tokens=2670,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            response_format={
                "type": "json_object"
            }
            )
    return json.loads(response.choices[0].message.content)