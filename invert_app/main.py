import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image as KivyImage
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.scrollview import ScrollView
from kivy.graphics.texture import Texture
from kivy.core.window import Window

import torch
import json
from torchvision import transforms
from PIL import Image as PILImage

# --- Charger le modèle PyTorch Mobile ---
model = torch.jit.load("model_mobile.pt", map_location="cpu")
model.eval()

# --- Charger les noms de classes ---
with open("class_indices.json", "r") as f:
    class_indices = json.load(f)

# Inverser dictionnaire pour idx → classe
idx_to_class = {v: k for k, v in class_indices.items()}

# --- Transformation d’image ---
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

class InvertClassifier(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        self.image_widget = KivyImage(size_hint=(1, 0.6))
        self.result_label = Label(size_hint=(1, 0.1), text='Résultat : ')
        self.top5_label = Label(size_hint=(1, 0.2), text='', halign='left', valign='top')
        self.choose_button = Button(text="Choisir une image", size_hint=(1, 0.1))
        self.choose_button.bind(on_press=self.choose_image)

        self.add_widget(self.image_widget)
        self.add_widget(self.result_label)
        self.add_widget(self.top5_label)
        self.add_widget(self.choose_button)

    def choose_image(self, instance):
        chooser = FileChooserIconView()
        chooser.bind(on_submit=self.load_image)
        self.clear_widgets()
        self.add_widget(chooser)

    def load_image(self, chooser, selection, touch):
        if selection:
            image_path = selection[0]
            self.show_result(image_path)

    def show_result(self, image_path):
        # Afficher l’image
        pil_image = PILImage.open(image_path).convert('RGB')
        tex = self.pil_to_texture(pil_image)
        self.clear_widgets()
        self.image_widget.texture = tex
        self.add_widget(self.image_widget)

        # Prédiction
        input_tensor = transform(pil_image).unsqueeze(0)
        with torch.no_grad():
            outputs = model(input_tensor)
            probs = torch.nn.functional.softmax(outputs, dim=1)[0]
            max_prob, predicted_idx = torch.max(probs, 0)

        # Affichage résultat
        if max_prob.item() < 0.6:
            self.result_label.text = "Espèce inconnue (confiance {:.2f}%)".format(max_prob.item() * 100)
            self.top5_label.text = ""
        else:
            predicted_class = idx_to_class[predicted_idx.item()]
            self.result_label.text = f"Classe prédite : {predicted_class} ({max_prob.item()*100:.2f}%)"

            # Top 5
            top5_probs, top5_indices = torch.topk(probs, 5)
            top5_text = "\n".join(
                f"{idx_to_class[i.item()]} : {p.item()*100:.2f}%" for i, p in zip(top5_indices, top5_probs)
            )
            self.top5_label.text = "Top 5 :\n" + top5_text

        self.add_widget(self.result_label)
        self.add_widget(self.top5_label)
        self.add_widget(self.choose_button)

    def pil_to_texture(self, image):
        image = image.resize((Window.width, int(Window.height * 0.6)))
        data = image.tobytes()
        texture = Texture.create(size=image.size)
        texture.blit_buffer(data, colorfmt='rgb', bufferfmt='ubyte')
        return texture


class InvertApp(App):
    def build(self):
        return InvertClassifier()

if __name__ == '__main__':
    InvertApp().run()
