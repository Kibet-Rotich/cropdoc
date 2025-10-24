# core/ml/inference.py
import os
import numpy as np
import torch
from PIL import Image
from lime import lime_image
from skimage.segmentation import mark_boundaries
import matplotlib.pyplot as plt
from .model_loader import model, device, class_names
from .transforms import transform_test
import torch.nn.functional as F



def predict_with_lime_blue(image_path, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    image = Image.open(image_path).convert("RGB")
    rgb_img = np.array(image.resize((224, 224)))

    def batch_predict(images):
        batch = torch.stack([transform_test(Image.fromarray(img.astype(np.uint8))) for img in images]).to(device)
        with torch.no_grad():
            logits = model(batch)
            probs = torch.nn.functional.softmax(logits, dim=1)
        return probs.detach().cpu().numpy()

    explainer = lime_image.LimeImageExplainer()
    explanation = explainer.explain_instance(rgb_img, batch_predict, top_labels=1, hide_color=0, num_samples=1)
    top_pred = explanation.top_labels[0]
    temp, mask = explanation.get_image_and_mask(top_pred, positive_only=True, num_features=7, hide_rest=False)

    overlay = rgb_img.copy().astype(np.float32) / 255.0
    overlay[mask == 1] = 0.55 * overlay[mask == 1] + 0.45 * np.array([0, 0, 1.0])
    lime_img = mark_boundaries(overlay, mask, color=(1, 1, 1))

    input_tensor = transform_test(image).unsqueeze(0).to(device)
    with torch.no_grad():
        outputs = model(input_tensor)
        probs = torch.nn.functional.softmax(outputs, dim=1)
        conf, pred_idx = torch.max(probs, dim=1)

    pred_class = class_names[pred_idx.item()]
    conf = conf.item() * 100

    save_path = os.path.join(save_dir, f"lime_{os.path.basename(image_path)}")
    plt.imsave(save_path, lime_img)

    return {"class": pred_class, "confidence": round(conf, 2), "lime_path": save_path}


