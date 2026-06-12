import torch
from PIL import Image

from torchvision import models
from torchvision import transforms


class ImageEncoder:

    def __init__(self):

        self.model = models.resnet50(
            pretrained=True
        )

        self.model.eval()

        self.transform = transforms.Compose(
            [
                transforms.Resize(
                    (224, 224)
                ),

                transforms.ToTensor()
            ]
        )

    def encode(
        self,
        image_path
    ):

        image = Image.open(
            image_path
        ).convert(
            "RGB"
        )

        image = self.transform(
            image
        ).unsqueeze(
            0
        )

        with torch.no_grad():

            embedding = (
                self.model(
                    image
                )
            )

        return embedding.numpy()