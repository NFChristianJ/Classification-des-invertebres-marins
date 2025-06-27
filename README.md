# 🐚 Application mobile pour la classification des invertébrés marins


## Application mobile pour la classification des invertébrés marins a partir des photos

Projet devellopé dans le cadre de l'ue projet inf4258 année 2024-2025
## Auteur 
- Noubissi Fopa christian junior
- essuthi mbangue ange armel

## Superviseur 
Prof tsopze nobert

---

## Sommaire
Probleme
Presentation generale
Solutions existantes
Solution proposée
Processus de developpement
Implementation
Entrainement
Evaluation


## Informations générales
Pour la résolution de ce problème, les données nous ont été fourni. Il s’agit d’un dataset disponible sur Kaggle a l’adresse suivante: https://www.kaggle.com/datasets/noubissichristian/invertebresmarrins
Il s’agit d’un dataset contenant deux ensemble de données dénommées train_small qui représente l’ensemble d’entrainement contenant des images étiquetés, de test_small qui représente des images de test non étiqueté et des métadonnées.

---


## Presentation de train_small
134 classes correspondants aux 134 espèces différentes d’invertébrés marins disponible dans la base de données
Présence d’un déséquilibre entre les classes
Classes majoritaires 
	- Actinostola_capensis 99  images 
	- Aequorea_spp  88 images 
	- Africolaria_rutila   83 images. 
16 classes minoritaires avec seuleument 10 images. Il s’agit entre autres des classes Synallactes_viridilimus, Seafan, Toraster_tuberculatus etc.

---


## Solution proposée
Nos principaux atouts reposent sur une application web en ligne et un application mobile fonctionnant hors-ligne, une spécialisation sur les invertébrés marins, des algorithmes optimisés et un temps de réponse relativement bas.
Notre model et notre application mobile sont disponible en telechargement a l'adresse:
https://drive.google.com/drive/folders/1vyNfWwcbszXT0pkpOazyXGaOeBMkt9v3?usp=sharing

---

vous pouvez egalement tester notre application directement en ligne sans telechargement en suivant le lien suivant:
https://6332-41-202-207-3.ngrok-free.app

---

## Nature de la Solution proposée
Un pipeline pour le prétraitement des photos télécharger 
Un système de classification basé sur un modèle de Deep Learning
Une base de données locale d'espèces d'invertébrés marins
Une interface utilisateur intuitive
Un système de synchronisation pour les mises à jour (en mode connecté)


---

## PROCESSUS DE DEVELOPPEMENT
Notre travail s’est deroulé en 05 grandes phases allant de la collecte des donnees jusqu’au deploiement de l’application web et mobile
Phase 1 : Collecte et Préparation des Données
	- Acquisition de la base de données d'images d'invertébrés marins
	- Nettoyage et prétraitement des images
Phase 2 : Développement du Modèle
	- Sélection et adaptation d'architectures de Deep Learning.
	- Entraînement et optimisation du modèle
	- Tests et validation des performances
Phase 3 : Développement Web
	- Création de l'interface utilisateur
	- Implémentation des fonctionnalités
	- Intégration du modèle optimisé
Phase 4 : Développement Mobile
	- Création de l'interface utilisateur mobile
	- Intégration du modèle optimisé
	- Implémentation du système de stockage local
Phase 5 : Tests et Déploiement
	- Tests utilisateurs
	- Optimisation des performances


## Implementation
Dans cette section, nous allons vous présenter les différentes étapes que nous avons traversées. 
Veuillez noter que nous ne détaillerons que le processus principal qui nous a permis d'obtenir les performances de notre modèle final, sans entrer dans les détails, les approches intermédiaires ou toutes nos expérimentations. 
Cependant, vous pourrez trouver l'ensemble du workflow ainsi que toutes nos expérimentations sur le dépôt GitHub officiel de cette application a l’adresse suivante : https://github.com/NFChristianJ/classification-des-invertebres-marins

---
vous pouvez egalement tester notre application directement en ligne sans telechargement en suivant le lien suivant:
https://6332-41-202-207-3.ngrok-free.app

---

## Collecte et analyses des donnees
Pour ce travail, les données nous ont été fourni par notre encadreur professeur Tsopze
Elles restent toujours accessible a cette adresse: https://www.kaggle.com/datasets/noubissichristian/invertebresmarrins
En analysant les données, nous avons pu déceler un grand déséquilibre entre les classes.


## Prétraitement et préparations des donnees
Decoupage de train_small en 80/10/10
Redimensionnement des images (224*224)
Normalisation des images range [0;1]
Standardisation des images au formats RGB 
	- mean = [0.485, 0.456, 0.406]
	- std = [0.229, 0.224, 0.225]
Deux augmentation des données
	- La premiere pour toutes les donnees d’entrainement
	- La seconde pour les classes minoritaires

## Modele
MODELE : vitf_patch_16 (VISion transformer)
Architecture Transformer pour traitement des images. 
Patch Embedding : Division de l’image en patch 16x16, ce qui donne un total de (224/16)^2 = 196 patches.
Linear Embedding : Projection dans un espace de dimension fixe
Position Embedding : Ajouts des embeddings de position aux vecteurs de patch pour conserver l'information spatiale.
Transformer Encoder : Passage des vecteurs a encodeur transformer
Multi-Head Self-Attention : Pondérer des vecteurs de patch en fonction de leur importance relative par les couches
Feed Forward Network (FFN) : Transformation des vecteurs de patch en représentations par la (FFN)
Classification : Classification de la sortie de transformer pour la prédiction la classe de l'image.
Mécanisme d'attention : multi-head self-attention
Le Multi-Head Self-Attention permet au modèle de pondérer les vecteurs de patch en fonction de leur importance relative pour la tâche de classification.
La ponderation est la Query, Key et Value : les vecteurs de patch sont projetés en trois espaces différents : Query (Q), Key (K) et Value (V).
Score d'attention = (Q.K)/dim(K). Utilisé pour la pondération des vecteurs.
Multi-Head : le mécanisme d'attention est répété plusieurs fois avec des poids différents pour obtenir plusieurs représentations de l'image, ce qui permet au modèle de se concentrer sur les parties les plus importantes de l'image pour la tâche de classification, ce qui améliore la performance du modèle.

Pourquoi ca marche?
Les architectures basées sur les transformers en général et le modèle ViTF en particulier marche bien sur nos données malgrés le fait que nous ayons peu de ressources parce que ViTF traite l'image de manière globale, ce qui permet de capturer les relations entre les différentes parties de l’image, contrairement aux autres méthodes de vision par ordinateur tels que les CNN. Ceci est rendu possible grâce au mécanisme d’attention.


## Entrainement 
Nos experimentations sont dans la sections experimentation de ce repo et le model resultant est issu du carnet model_vitf. Pour cela nous avons fait du:
Fine Tuning de ViTF_patch_16
Entrainement sur 10 époques
Optimiseur Adam
Learning Rate 1e-04
Métriques
	- Precision
	- Rappel
	- F1 Score


## Evaluation
Notre model perente des score plutot satisfesant sur notre base de test
Precision general 89%
Rappel general 87%
F1-Score 88%

Précision de classification : 88.58% pour les espèces communes
Temps de traitement < 5 secondes par image
Taille de l'application < 100 MB
Fonctionnement fluide sur des appareils de moyenne gamme


## Fonctionnalités
La fonction principale de l’application est d’identifier les invertébrés marins à partir d’image, en suivant ces étapes:
Prise de photo
Téléchargement et soumission des photos à l’application 
Analyse par IA : une fois que la photo a été soumise, l’application utilisera des algorithmes d’apprentissage automatique pour analyser les caractéristiques visuelles de l’espèce, ensuite elle compare ces caractéristiques avec celles des espèces présente dans la base de données
Ensuite à partir d’un algorithme de reconnaissance elle fait une correspondance entre les caractéristiques uniques de l’espèce et les caractéristiques des espèces disponibles dans la base de données
Ensuite elle affiche l’espèce la plus probable dans une liste d’espèce possible avec leurs différentes probabilités

Pour tester l'application en ligne sans telechargement, vous pouvez suivre le lien suivant 
https://6332-41-202-207-3.ngrok-free.app

Notre model et notre application mobile sont disponible en telechargement a l'adresse:
https://drive.google.com/drive/folders/1vyNfWwcbszXT0pkpOazyXGaOeBMkt9v3?usp=sharing
