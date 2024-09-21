from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Company(models.Model):
    name = models.CharField(max_length=100)
    legal_name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    detailed_descrption = models.TextField(blank=True, null=True)
    problem_statement = models.JSONField(blank=True, null=True)
    customer_list =  models.JSONField(blank=True, null=True)
    links = models.JSONField(blank=True, null=True)
    details_fetched= models.BooleanField(default=False)
    sector = models.CharField(max_length=100)
    industry = models.CharField(max_length=100, blank=True, null=True)
    domain = models.CharField(max_length=100, unique=True)
    tags = models.JSONField(default=list, blank=True)
    founded_year = models.IntegerField(blank=True, null=True)
    timezone = models.CharField(max_length=50, blank=True, null=True)
    logo = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    raw_data = models.JSONField(blank=True, null=True)

class Person(models.Model):
    full_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name =  models.CharField(max_length=100, blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    seniority = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, null=True)
    site = models.URLField(blank=True, null=True)
    avatar = models.URLField(blank=True, null=True)
    linkedin_handle=models.CharField(max_length=100, blank=True, null=True)
    raw_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT, null=True, blank=True)
    auth_user = models.ForeignKey(User,
                                    on_delete=models.PROTECT, null=True, blank=True)

class CompanyTriggerSegment(models.Model):
    SALES = "SA"
    MARKETING = "MA"
    OPERATIONS_ADMIN = "OA"
    TECH = "TE"
    PRODUCT_DESIGN = "PD"
    ALL = "AL"
    
    # Subcategories short codes
    ACCOUNT_EXECUTIVE = "AE"
    SALES_MANAGER = "SM"
    SDR_BDR = "SB"
    FIELD_SALES = "FS"
    DIGITAL_MARKETING = "DM"
    CONTENT_SPECIALIST = "CS"
    EMAIL_MARKETING = "EM"
    EVENT_MARKETING = "EV"
    CUSTOMER_SUCCESS = "CSM"
    CUSTOMER_SUPPORT = "CSP"
    FIELD_SUPPORT = "FSP"
    LOGISTICS = "LO"
    LEGAL_COMPLIANCE = "LC"
    RECRUITING_OPERATIONS = "RO"
    SOFTWARE_ENGINEERING = "SE"
    ARTIFICIAL_INTELLIGENCE = "AI"
    DEV_OPS = "DO"
    QA = "QA"
    PRODUCT_MANAGEMENT = "PM"
    PROGRAM_MANAGEMENT = "PGM"
    GRAPHIC_DESIGNER = "GD"
    UI_DESIGN = "UID"

    TRIGGER_CATEGORY_CHOICES = [
        (SALES, "Sales"),
        (MARKETING, "Marketing"),
        (OPERATIONS_ADMIN, "Operations / Admin"),
        (TECH, "Tech"),
        (PRODUCT_DESIGN, "Product / Design"),
        (ALL, "All Roles"),
    ]

    SUB_CATEGORY_CHOICES = [
        (ACCOUNT_EXECUTIVE, "Account Executive/Account Manager (AE/AM)"),
        (SALES_MANAGER, "Sales Manager"),
        (SDR_BDR, "SDR/BDR"),
        (FIELD_SALES, "Field Sales"),
        (DIGITAL_MARKETING, "Digital Marketing"),
        (CONTENT_SPECIALIST, "Content Specialist"),
        (EMAIL_MARKETING, "Email Marketing Specialist"),
        (EVENT_MARKETING, "Event Marketing"),
        (CUSTOMER_SUCCESS, "Customer Success Manager"),
        (CUSTOMER_SUPPORT, "Customer Support"),
        (FIELD_SUPPORT, "Field Support"),
        (LOGISTICS, "Logistics"),
        (LEGAL_COMPLIANCE, "Legal and Compliance"),
        (RECRUITING_OPERATIONS, "Recruiting Operations"),
        (SOFTWARE_ENGINEERING, "Software Engineering"),
        (ARTIFICIAL_INTELLIGENCE, "Artificial Intelligence"),
        (DEV_OPS, "Dev Ops"),
        (QA, "QA (Quality Assurance)"),
        (PRODUCT_MANAGEMENT, "Product Management"),
        (PROGRAM_MANAGEMENT, "Program Management"),
        (GRAPHIC_DESIGNER, "Graphic Designer"),
        (UI_DESIGN, "UI Design"),
    ]

    role_category = models.CharField(max_length=2, choices=TRIGGER_CATEGORY_CHOICES, default=ALL)
    sub_category = models.CharField(max_length=3, choices=SUB_CATEGORY_CHOICES, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    raw_filters = models.JSONField(null=True, blank=True)
    industry_ids = models.JSONField(null=True, blank=True)
    person_job_role = models.CharField(max_length=2, null=True, blank=True)
    additional_selling_point = models.TextField(null=True, blank=True)
    person_job_level= models.CharField(max_length=2, null=True, blank=True)
    default_mail = models.JSONField(null=True, blank=True)
    last_job_fetch = models.DateTimeField(null=True, blank=True)

class JobSearchResult(models.Model):
    trigger_segment = models.ForeignKey(CompanyTriggerSegment, on_delete=models.PROTECT)
    raw_data = models.JSONField(null=True, blank=True)
    company_url = models.TextField(null=True, blank=True)
    mail = models.JSONField(null=True, blank=True)
    people_results =  models.JSONField(null=True, blank=True)

class PeopleJobEmailTask(models.Model):
    prospect_name = models.CharField(max_length=100, null=True, blank=True)
    prospect_title = models.CharField(max_length=100, null=True, blank=True)
    prospect_company_name = models.CharField(max_length=100, null=True, blank=True)
    trigger_segment = models.ForeignKey(CompanyTriggerSegment, on_delete=models.PROTECT)
    job = models.ForeignKey(JobSearchResult, on_delete=models.PROTECT)
    company_url = models.TextField(null=True, blank=True)
    prospect_details = models.JSONField()
    prospect_email = models.EmailField()
    mail_content = models.JSONField(null=True, blank=True)
    generated = models.BooleanField(default=False)
    send = models.BooleanField(default=False)
    send_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    





