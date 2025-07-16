# invert_project/invert_project/predictor/views.py

import os
import json
import torch
import timm
import random
from PIL import Image
from django.conf import settings
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from torchvision import transforms
from .forms import ImageUploadForm
import requests
from django.core.files.base import ContentFile
import imghdr
from django.views.decorators.http import require_GET 
from django.http import HttpResponseRedirect
from django.conf import settings
from pathlib import Path
from django.contrib import messages

# --------------------------
# Initialisation du modèle
# --------------------------

model = timm.create_model('vit_base_patch16_224', pretrained=False)
model.head = torch.nn.Linear(model.head.in_features, 137)
model.load_state_dict(torch.load('F:/1234/models/model.pth', map_location=torch.device('cpu')))
model.eval()

# --------------------------
# Chargement des classes
# --------------------------

with open('C:/Users/Christian/Desktop/Classification-des-invertebres-marins/class_index/class_indices.json', 'r') as f:
    class_indices = json.load(f)  # dictionnaire {nom_de_classe: index}

# --------------------------
# Transformation des images
# --------------------------

preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# --------------------------
# Fonction de prédiction
# --------------------------

def predict_image(image_path):
    img = Image.open(image_path).convert('RGB')
    img_tensor = preprocess(img).unsqueeze(0)

    with torch.no_grad():
        outputs = model(img_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)[0]

    max_prob, predicted_idx = torch.max(probabilities, 0)

    if max_prob < 0.7:
        return "Espece inconnue", None, None
    else:
        # Obtenir les 5 classes les plus probables
        top5_probs, top5_indices = torch.topk(probabilities, 5)
        top5 = []
        for prob, idx in zip(top5_probs, top5_indices):
            class_name = next((k for k, v in class_indices.items() if v == idx.item()), "Inconnue")
            top5.append((class_name, prob.item()))
        
        predicted_class = top5[0][0]
        return predicted_class, max_prob.item(), top5

# --------------------------
# Vue Upload
# --------------------------

def upload_view(request):
    if request.method == 'POST':
        uploaded_image = request.FILES.get('image')
        image_url = request.POST.get('image_url')

        if uploaded_image:
            # Cas upload local
            fs = FileSystemStorage()
            filename = fs.save(uploaded_image.name, uploaded_image)
            uploaded_file_url = fs.url(filename)
            return redirect(f'/result/?local_image_url={uploaded_file_url}')
        
        elif image_url:
            # Cas image distante
            try:
                # Télécharger l'image distante
                response = requests.get(image_url)
                if response.status_code == 200:
                    # Vérification du type d'image
                    image_type = imghdr.what(None, response.content)
                    if image_type not in ['jpeg', 'png', 'jpg']:
                        return render(request, 'predictor/upload.html', {'error': "L'URL fournie n'est pas une image valide."})

                    # Crée un nom de fichier simple
                    filename = image_url.split("/")[-1]
                    if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                        filename += ".jpg"  # sécurité

                    # Sauvegarder l'image dans MEDIA
                    fs = FileSystemStorage()
                    saved_path = fs.save(filename, ContentFile(response.content))
                    uploaded_file_url = fs.url(saved_path)
                    
                    return redirect(f'/result/?local_image_url={uploaded_file_url}')
                else:
                    return render(request, 'predictor/upload.html', {'error': "Impossible de télécharger l'image (erreur serveur distant)"})
            except Exception as e:
                return render(request, 'predictor/upload.html', {'error': f"Erreur lors du téléchargement : {str(e)}"})
        
        else:
            return render(request, 'predictor/upload.html', {'error': "Veuillez sélectionner une image ou entrer un lien d'image."})

    return render(request, 'predictor/upload.html')

# --------------------------
# Vue Prédiction directe (non utilisée ici mais correcte)
# --------------------------

def predict_view(request):
    predicted_class = None
    confidence = None

    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(image_file.name, image_file)
        image_path = os.path.join(settings.MEDIA_ROOT, filename)
        predicted_class, confidence = predict_image(image_path)

    return render(request, 'predictor/predict.html', {
        'predicted_class': predicted_class,
        'confidence': confidence,
    })


# --------------------------
# Prédiction depuis image PIL
# --------------------------

def predict_image_from_pil(img):
    img_tensor = preprocess(img).unsqueeze(0)

    with torch.no_grad():
        outputs = model(img_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        max_prob, predicted_idx = torch.max(probabilities, 1)

    if max_prob < 0.7:
        return "Catégorie inconnue", max_prob.item()
    else:
        predicted_class = next((k for k, v in class_indices.items() if v == predicted_idx.item()), "Classe inconnue")
        return predicted_class, max_prob.item()

# --------------------------
# Vue Résultat
# --------------------------

def result_view(request):
    local_image_url = request.GET.get('local_image_url')
    remote_image_url = request.GET.get('remote_image_url')

    if local_image_url:
        # Cas image locale
        image_relative_path = local_image_url.replace('/media/', '')
        image_path = os.path.join(settings.MEDIA_ROOT, image_relative_path)

        if not os.path.exists(image_path):
            return render(request, 'predictor/result.html', {
                'predicted_class': 'Image introuvable',
                'confidence': 0,
                'image_url': local_image_url,
            })

        predicted_class, confidence, top5 = predict_image(image_path)
        image_url = local_image_url

    elif remote_image_url:
        # Cas image distante
        try:
            from io import BytesIO
            import requests
            response = requests.get(remote_image_url)
            img = Image.open(BytesIO(response.content)).convert('RGB')
            predicted_class, confidence = predict_image_from_pil(img)
            image_url = remote_image_url
        except:
            return render(request, 'predictor/result.html', {
                'predicted_class': 'Image inaccessible',
                'confidence': 0,
                'image_url': remote_image_url,
            })

    else:
        # Aucun des deux cas
        return render(request, 'predictor/result.html', {
            'predicted_class': 'Aucune image fournie',
            'confidence': 0,
            'image_url': '',
        })

    return render(request, 'predictor/result.html', {
        'predicted_class': predicted_class,
        'confidence': round(confidence * 100, 2) if confidence else None,
        'image_url': image_url,
        'top5' : top5,
    })

@require_GET
def index(request):
    context = {
        'slider_images': [
            'images/baniere1.jpg',
            'images/baniere2.jpg',
            'images/baniere3.webp',
        ]
    }
    return render(request, 'index.html', context)

def understand_view(request):
    return render(request, 'predictor/understand.html')

def visual_guide_view(request):
    featured_species = [
        {
            'name': 'Actinia Equina',
            'image': 'images/species/actinia.jpg',
            'description': 'Anémone de mer commune en Méditerranée. Corps cylindrique avec des tentacules urticants. Couleur rouge vif caractéristique. Se fixe aux rochers.',
            'detail_url': '/especes/actinia'
        },
        {
            'name': 'Aequorea Victoria',
            'image': 'images/species/aequorea.jpg',
            'description': 'Méduse bioluminescente produisant une protéine fluorescente verte (GFP). Transparente avec des nervures visibles. Diamètre 5-10 cm.',
            'detail_url': '/especes/aequorea'
        },
        {
            'name': 'Charonia Lampas',
            'image': 'images/species/charonia.jpg',
            'description': 'Grand mollusque gastéropode. Coquille spiralée pouvant atteindre 40 cm. Prédateur des étoiles de mer. Espèce protégée en Europe.',
            'detail_url': '/especes/charonia'
        },
        {
            'name': 'Comanthus Wahlbergii',
            'image': 'images/species/comanthus.jpg',
            'description': 'Comatule (crinoïde) avec des bras plumeux. Se déplace en nageant. Filtre le plancton. 10-20 bras de 15 cm de long.',
            'detail_url': '/especes/comanthus'
        },
        {
            'name': 'Pagurus Bernhardus',
            'image': 'images/species/pagurus.jpg',
            'description': 'Bernard-l\'ermite commun. Utilise des coquilles vides pour protéger son abdomen. Vit en symbiose avec des anémones.',
            'detail_url': '/especes/pagurus'
        },
        {
            'name': 'Ophiothrix Fragilis',
            'image': 'images/species/ophiothrix.jpg',
            'description': 'Ophiure aux bras fragiles et épineux. Mouvements rapides. Se régénère facilement. Vit en colonies denses sur les fonds rocheux.',
            'detail_url': '/especes/ophiothrix'
        }
    ]
    return render(request, 'your_template.html', {'featured_species': featured_species})

def all_species_view(request):
    # Chemin ABSOLU vers votre fichier JSON
    json_path = Path(r"C:\Users\Christian\Desktop\ClassificationInvertebresMarrins\class_indices.json")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            class_data = json.load(f)
        
        species_list = [{'name': name, 'id': idx} for name, idx in class_data.items()]
        
        return render(request, 'predictor/all_species.html', {
            'species_list': species_list[:137],
            'total_species': len(species_list)
        })
        
    except FileNotFoundError:
        return render(request, 'predictor/error.html', {
            'message': "Fichier des espèces introuvable"
        })

# --------------------------
# Vue Participer
# --------------------------

def participer_view(request):
    return render(request, 'predictor/participer.html')

# --------------------------
# Vue Ressources
# --------------------------

def ressources_view(request):
    return render(request, 'predictor/ressources.html')

# --------------------------
# Vue Recherche
# --------------------------

def recherche_view(request):
    return render(request, 'predictor/recherche.html')

# --------------------------
# Vue Contact
# --------------------------

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        category = request.POST.get('category')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Affichage console pour développement
        print(f"""
        Nouveau message reçu:
        De: {name} ({email})
        Catégorie: {category}
        Sujet: {subject}
        Message:
        {message}
        """)
        
        messages.success(request, 'Votre message a bien été envoyé !')
        return redirect('contact')
    
    return render(request, 'predictor/contact.html')

# --------------------------
# Vue Comming soon
# --------------------------

def coming_soon_view(request):
    return render(request, 'predictor/coming_soon.html')

# --------------------------
# Vue Conditions
# --------------------------

def conditions_view(request):
    return render(request, 'predictor/conditions.html')

# --------------------------
# Vue Mentions
# --------------------------

def mentions_view(request):
    return render(request, 'predictor/mentions.html')

# --------------------------
# Vue Equipe
# --------------------------

def equipe_view(request):
    return render(request, 'predictor/equipe.html')

# --------------------------
# Vue Blog
# --------------------------

def blog_view(request):
    return render(request, 'predictor/blog.html')


def all_species_view(request):
    dataset_path = settings.EXTERNAL_DATASET_PATH
    species_list = []

    if os.path.exists(dataset_path):
        for species_name in os.listdir(dataset_path):
            species_dir = os.path.join(dataset_path, species_name)
            if os.path.isdir(species_dir):
                images = [f for f in os.listdir(species_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                if images:
                    random_image = random.choice(images)
                    image_path = os.path.join('dataset', species_name, random_image)
                    species_list.append({
                        'name': species_name,
                        'image': image_path.replace('\\', '/') 
                    })

    context = {
        'species_list': species_list,
        'total_species': len(species_list),
    }
    return render(request, 'predictor/all_species.html', context)
