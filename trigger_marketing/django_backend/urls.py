from django.urls import path

from django_backend.views import CompanyAPIView, ProspectEmailListAPIView, TriggersListAPIView, base_mail, create_user_view, create_company_user, create_home_view, create_new_trigger, find_people_gen_email, get_filters, get_just_filters, prompt_update_email, search_jobs, send_email, trigger_detail, trigger_view, update_email, update_prospect_email

urlpatterns = [

    path('get_started/', create_user_view, name='create_user'),
    path('create_user/', create_company_user),
    path('company/<int:pk>/', CompanyAPIView.as_view()), #### TODO
    # path('connect_email/<int:person_id>/', connect_email),

    #### Home Page
    path('home/', create_home_view),
    path('triggers/<int:company_id>/', TriggersListAPIView.as_view()),
    path('new_trigger/', create_new_trigger), ### not used
    
    

    ##### Trigger page base urls
    path('trigger_view/<int:trigger_id>/', trigger_view), ### not used
    path('create_trigger/', get_just_filters),
    path('trigger_detail/<int:trigger_id>/', trigger_detail),
    path('update_filters/<int:trigger_id>/', get_filters),
    path('search/<int:trigger_id>/', search_jobs),

    ##### Trigger page email urls
    path('generate_email/<int:trigger_id>/', base_mail),
    path('update_email/<int:trigger_id>/', update_email),

    
    path('prompt_update/<int:trigger_id>/', prompt_update_email),
    path('find_gen_email/<int:trigger_id>/', find_people_gen_email),  #### TODO

    #### connect and send emails
    path('update_prospect_email/<int:pk>/', update_prospect_email),  #### TODO
    path('get_emails/<int:trigger_id>/', ProspectEmailListAPIView.as_view()),  #### TODO
    path('send_email/<int:pk>/', send_email),  #### TODO
    

]