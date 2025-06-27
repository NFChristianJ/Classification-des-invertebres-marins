import torch
import torchvision.transforms as transforms
from PIL import Image
import torch.nn as nn
from timm import create_model

model = create_model('vit_base_patch16_224',pretrained = True)
model.head = nn.Linear(model.head.in_features, 137)  # nombre de classes = 137

model.load_state_dict(torch.load("model.pth",map_location = torch.device('cpu')))
model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

image_path = "C:\\Users\\Christian\\Desktop\\UE Projet\\Dataset\\test_small\\test_small\\00G9CO1.jpeg" 
image = Image.open(image_path).convert('RGB')
input_tensor = transform(image).unsqueeze(0)  # batch size = 1

with torch.no_grad():
    output = model(input_tensor)
    predicted_class = torch.argmax(output, dim=1).item()
    print("L'invertébré prédit est de classe (index) :", predicted_class)