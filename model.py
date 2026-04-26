import torch
import torch.nn.functional as F
from torch import nn
from torchvision import models, transforms
import cv2
import os

class SkinModel:
    def __init__(self, model_path, num_classes=3):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.model = models.mobilenet_v2(weights=None)
        self.model.classifier[1] = nn.Linear(self.model.last_channel, num_classes)

        # Resolve path relative to this script's directory
        if not os.path.isabs(model_path):
            model_path = os.path.join(os.path.dirname(__file__), model_path)

        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406],
                                 [0.229, 0.224, 0.225])
        ])

    def predict(self, frame):
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        input_tensor = self.transform(img).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = self.model(input_tensor)
            probs = F.softmax(outputs, dim=1)
            confidence, pred_index = torch.max(probs, dim=1)

        return pred_index.item(), confidence.item()