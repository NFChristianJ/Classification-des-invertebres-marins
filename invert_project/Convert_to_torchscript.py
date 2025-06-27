import torch
import timm

# Charger ton modèle
model = timm.create_model('vit_base_patch16_224', pretrained=False)
model.head = torch.nn.Linear(model.head.in_features, 137)
model.load_state_dict(torch.load("C:/Users/Christian/Desktop/ClassificationInvertebresMarrins/model/model.pth", map_location="cpu"))
model.eval()

# Entrée factice (batch_size=1, 3 canaux, 224x224)
dummy_input = torch.randn(1, 3, 224, 224)

# Tracer le modèle
traced_model = torch.jit.trace(model, dummy_input)

# Sauvegarder
traced_model.save("vitf_model_scripted.pt")
