# core/ml/model_loader.py
import torch
import torch.nn as nn
from timm.models import create_model
from timm.models.vision_transformer import Block
from timm.models.layers import DropPath
import os

# Custom block (your ParallelBlock)
class DepthwiseConv(nn.Module):
    def __init__(self, dim, kernel_size=3):
        super().__init__()
        self.dwconv = nn.Conv2d(dim, dim, kernel_size=kernel_size,
                                padding=kernel_size // 2, groups=dim)
        self.bn = nn.BatchNorm2d(dim)

    def forward(self, x):
        B, N, C = x.shape
        cls_token = x[:, :1]
        patch_tokens = x[:, 1:]
        H = W = int(patch_tokens.shape[1] ** 0.5)
        patch_tokens = patch_tokens.transpose(1, 2).view(B, C, H, W)
        patch_tokens = self.bn(self.dwconv(patch_tokens))
        patch_tokens = patch_tokens.flatten(2).transpose(1, 2)
        return torch.cat((cls_token, patch_tokens), dim=1)

class ParallelBlock(Block):
    def __init__(self, dim, num_heads, mlp_ratio=4., qkv_bias=True,
                 norm_layer=nn.LayerNorm, drop_path=0.0):
        super().__init__(dim, num_heads, mlp_ratio, qkv_bias=qkv_bias,
                         norm_layer=norm_layer, drop_path=0.0)
        self.depthwise_conv = DepthwiseConv(dim)
        self.attn_norm = norm_layer(dim)
        self.conv_norm = norm_layer(dim)
        self.fuse_mlp = nn.Sequential(
            nn.Linear(dim * 2, dim * 4),
            nn.GELU(),
            nn.Linear(dim * 4, dim)
        )
        self.drop_path = DropPath(drop_path) if drop_path > 0. else nn.Identity()

    def forward(self, x):
        x_attn = self.attn(self.attn_norm(x))
        x_conv = self.depthwise_conv(self.conv_norm(x))
        x_fused = torch.cat([x_attn, x_conv], dim=-1)
        x_fused = self.fuse_mlp(x_fused)
        x = x + self.drop_path(x_fused)
        x = x + self.drop_path(self.mlp(self.norm2(x)))
        return x


def load_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    class_names = ['Fall Army Worm', 'Grey Leaf Spot', 'Healthy', 'Northern Leaf Blight', 'Northern Leaf Spot', 'Common Rust']

    def load_custom_parallel_deit(num_classes, pretrained=False, replace_blocks=3):
        model = create_model('deit_tiny_patch16_224', pretrained=pretrained)
        for i, block in enumerate(model.blocks):
            if i < replace_blocks:
                mlp_hidden = block.mlp.fc1.out_features
                mlp_in = block.mlp.fc1.in_features
                mlp_ratio = mlp_hidden / mlp_in
                model.blocks[i] = ParallelBlock(
                    dim=block.norm1.normalized_shape[0],
                    num_heads=block.attn.num_heads,
                    mlp_ratio=mlp_ratio,
                    qkv_bias=block.attn.qkv.bias is not None,
                    norm_layer=type(block.norm1),
                    drop_path=0.0
                )
        model.head = nn.Linear(model.head.in_features, num_classes)
        return model

    model_path = os.path.join(os.path.dirname(__file__), "Custom_best_convDeitTiny.pth")
    model = load_custom_parallel_deit(num_classes=len(class_names))
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device).eval()

    return model, device, class_names


# Load once on module import
model, device, class_names = load_model()
