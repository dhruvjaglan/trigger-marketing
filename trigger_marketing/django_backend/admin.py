from django.contrib import admin
from .models import Company, Person, CompanyTriggerSegment, JobSearchResult, PeopleJobEmailTask

# Register your models here.


admin.site.register(Company)
admin.site.register(Person)
admin.site.register(CompanyTriggerSegment)
admin.site.register(JobSearchResult)
admin.site.register(PeopleJobEmailTask)
