# invert_project/invert_project/predictor/urls.py
from django.urls import path
from . import views
from .views import equipe_view, blog_view, mentions_view, conditions_view, coming_soon_view, understand_view, all_species_view, participer_view, ressources_view, recherche_view, contact_view
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    # On ajoutera les vues bientôt
    path('upload/', views.upload_view, name='upload'),  
    path('result/', views.result_view, name='result'),
    path('', views.index, name='index'), 
    path('comprendre/', understand_view, name='understand'),
    path('especes/', all_species_view, name='all_species'),
    path('participer/', participer_view, name='participer'),
    path('ressources/', ressources_view, name='ressources'),
    path('recherche/', recherche_view, name='recherche'),
    path('contact/', contact_view, name='contact'),
    path('coming-soon/', coming_soon_view, name='coming_soon'),
    path('equipe/', equipe_view, name='equipe'),
    path('blog/', blog_view, name='blog'),
    path('mentions/', mentions_view, name='mentions'),
    path('conditions/', conditions_view, name='conditions'),

]

urlpatterns += static('/dataset/', document_root=settings.EXTERNAL_DATASET_PATH)
