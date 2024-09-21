from rest_framework import serializers, status
from .models import Company, PeopleJobEmailTask, Person, CompanyTriggerSegment, JobSearchResult


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'id',
            'name',
            'description',
            'detailed_descrption',
            'sector',
            'industry',
            'domain',
            'founded_year',
            'logo'
        ]

class PersonSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)

    class Meta:
        model = Person
        fields = [
            'id',
            'full_name',
            'first_name',
            'last_name',
            'title',
            'seniority',
            'email',
            'bio',
            'site',
            'avatar',
            'linkedin_handle',
            'company'
        ]
        depth = 1


class CompanyTriggerSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyTriggerSegment
        fields = "__all__"

class JobSearchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSearchResult
        fields = "__all__"

class PeopleJobEmailTaskSerializer(serializers.ModelSerializer):
    class Meta:

   
        model = PeopleJobEmailTask
        fields = [
            'id',
            'prospect_name',
            'prospect_title',
            'prospect_company_name',
            'trigger_segment',
            'job',
            'company_url',
            'prospect_email',
            'mail_content',
            'generated',
        ]


class CreateTriggerSerializer(serializers.Serializer):
    company = serializers.IntegerField()
    category = serializers.CharField()
    subcategory = serializers.CharField(allow_null=True, required=False, allow_blank=True)