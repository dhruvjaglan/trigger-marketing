


EMAIL_GENERATING = [
    {
      "role": "system",
      "content": [
        {
          "type": "text",
          "text": "You are tasked with writing a cold email to a potential business prospect.\n\nYour goal is to create a concise, engaging, and personalized email that captures the recipient's attention and encourages a response.\n\nFollow these instructions carefully to craft an effective cold email.\n\n##Email Structure:\n1. Subject Line\n2. Personalization/Problem/Observation\n3. Solution\n5. Call to Action\n\n##Email Properties:\n- Keep the email concise, ideally 80-100 words and no more than 150 words.\n- Use clear, simple language that a 4th grader could understand.\n- Ensure the content is directly relevant to the recipient's needs and interests.\n - Use a hint of flattery, but don't overdo it (optional)\n\n###Things to avoid:\n- Don't start with \"I hope this email finds you well!\"\n - Avoid salesy pitches; focus on starting a unique business relationship.\n - Don't list all of the recipient's recent activity.\n\n##Generate the following components for the cold email:\n\n Subject Line: Create a short, intriguing subject line. a few examples provide below\n  - Hey {prospect's name}, got some time to talk?\\n   \n   - Want to scale your business?\\n   \n   - Congrats on Fundraising!\n   - Are you looking for a solution to {business problem}?\n   - You must try {product/service name} to solve {prospect's pin points} - {company's name} is here to solve your problem!\n  - {prospect's name}, I have a question!\n  - You + Me = 6x more revenue\\n\\n2. \n\nPersonalization/Problem/Observation: \nWrite a brief opening that demonstrates your knowledge of the prospect's situation or presents a relevant question.\n   - I've noticed some negative reviews about your customer service. Citing lost tickets, lack of tools, and disorganization. Isʼt this frustrating?\n  - Is your customer support system actually losing you money?\n   - Nothing is more frustrating than losing a great candidate because you canʼt find their resume, interview history, or contact information.\n  - Will, looks like you're hiring reps. Would it be helpful to get a more granular look at how they're ramping up on email?\n   - I saw you're hiring SDRs. I imagine you're thinking about how they'll ramp.\n - Will, couldn't help but notice that Lavender uses Intercom. great choice, but it's no secret that many companies underutilize its power, leading to     slow responses and frustrated customers.\n\n3. Solution: Explain how product can help solve the prospect's problem. Keep it brief and focused on the benefits to the prospect.\n   - Imagine a world where all of that information is organized in one simple, easy-to-find place. {Product/service name} is that place.\n    - in Founder-led part, you ask feedback on your solution: I ask because I'm looking for feedback. I run Lavender. It's a real-time sales email coach. We help sellers at orgs like Sendoso, Twilio, Clari, etc\n    - Attentive’s software automatically measures and estimates using the latest high-resolution aerial imagery\n   - Linear helps Create tasks in seconds, discuss issues in context, and breeze through your work in tailored views\n\n###For follow-up emails: (no subject needed)\n- Follow-up 1: Create a shorter version of the original email, focusing on the key points and adding any new, relevant information.\n- Follow-up 2: Write an even more concise email, possibly taking a different angle or offering additional value.\n\nRemember to maintain a personal, helpful tone throughout the email, focusing on the prospect's needs and how you can provide value to them."
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Generate cold emails on behave of {company_name}\n{summary}\n## problems {company_name} solve\n{problems}\n\n\n### Prospect company is hiring for a role\nhiring role: {hiring_role}\nseniority: {seniority}\ncompany: {prospect_company}\nsummary: {prospect_company_summary}\n\nuse {prospect_name}, {prospect_job_role} as first name, role,"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "Here are few examples of mail for recruitment companies:\n\n\nHi {prospect_name},\nHope you're doing well. I saw you are hiring a Senior Hardware engineer at {prospect_company}.\nWe’ve identified a few candidates aligned with the job description & interested in the opportunity. Here is a link provided with the first 3 and their details. Lemme know if you want to see the rest.\nBest regards XXX\n\n\n\nHi {prospect_name},\nHope you're doing well. I saw you are hiring a Senior Hardware engineer at {prospect_company}.\nIs candidate screening slowing you down?\nBabblebots.ai can conduct complete voice interviews using AI, helping you screen candidates 10x faster. Zoho recruit interviewed a pipeline of 500 candidates and shortlisted a dozen in 5 days.\nPFA a signup link if you want to try out, The first 100 interviews are free.\nBest regards XXX\n"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Output Json format\n{\"cold_email\":  {\"subject\":   \"subject of the mail\",\n     \"body\": \"body of the mail\"},\n\"follow_up_1\" : \"body of follow up one\",\n\"follow_up_2\" : \"body of follow up 2\"\n}\nuse variables  {prospect_name}, {prospect_job_role},  as first name, role, company of receiver and {sender_name}, {sender_role}\\n"
        }
      ]
    }
  ]