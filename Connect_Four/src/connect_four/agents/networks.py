"""Kien truc mang no-ron (PyTorch) dung cho Cap 5 (CNN Policy) va Cap 6 (DQN).

De dam bao `import connect_four` va kiem thu co ban hoat dong duoc ngay ca khi
chua cai PyTorch (vi du tren moi truong CI nhe), viec khoi tao mo hinh se kiem tra
va yeu cau PyTorch khi duoc su dung.
"""

from __future__ import annotations

from typing import Any


def _get_torch():
    try:
        import torch
        import torch.nn as nn
        return torch, nn
    except ImportError as err:
        raise ImportError(
            "PyTorch chua duoc cai dat. Vui long cai dat bang 'pip install torch' "
            "de su dung cac tac tu mang no-ron (Cap 5 & Cap 6)."
        ) from err


class CNNPolicyNet:
    """Mang CNN Policy (Cap 5) - Hoc co giam sat tu nuoc di Alpha-Beta.

    Input: Tensor (B, in_channels, 6, 7), mac dinh 2 kenh
           - Kenh 0: quan cua nguoi choi hien tai
           - Kenh 1: quan cua doi thu
           - Co the tang in_channels neu thi nghiem bo sung dac trung.
    Output: Logits 7 cot (B, 7)
    """

    def __new__(cls, in_channels: int = 2, hidden_channels: int = 64) -> Any:
        torch, nn = _get_torch()

        class _TorchCNNPolicyNet(nn.Module):
            def __init__(self, in_ch: int, hidden_ch: int) -> None:
                super().__init__()
                self.conv_block = nn.Sequential(
                    nn.Conv2d(in_ch, hidden_ch, kernel_size=3, padding=1),
                    nn.BatchNorm2d(hidden_ch),
                    nn.ReLU(),
                    nn.Conv2d(hidden_ch, hidden_ch, kernel_size=3, padding=1),
                    nn.BatchNorm2d(hidden_ch),
                    nn.ReLU(),
                    nn.Conv2d(hidden_ch, hidden_ch, kernel_size=3, padding=1),
                    nn.BatchNorm2d(hidden_ch),
                    nn.ReLU(),
                )
                self.fc = nn.Sequential(
                    nn.Flatten(),
                    nn.Linear(hidden_ch * 6 * 7, 128),
                    nn.ReLU(),
                    nn.Linear(128, 7),
                )

            def forward(self, x: torch.Tensor) -> torch.Tensor:
                features = self.conv_block(x)
                return self.fc(features)

        return _TorchCNNPolicyNet(in_channels, hidden_channels)


class DQNNet:
    """Mang Deep Q-Network (Cap 6) - Uoc luong gia tri hanh dong Q(s, a).

    Input: Tensor (B, 2, 6, 7)
    Output: Gia tri Q-value cho 7 cot hanh dong (B, 7)
    """

    def __new__(cls, in_channels: int = 2, hidden_channels: int = 64) -> Any:
        torch, nn = _get_torch()

        class _TorchDQNNet(nn.Module):
            def __init__(self, in_ch: int, hidden_ch: int) -> None:
                super().__init__()
                self.features = nn.Sequential(
                    nn.Conv2d(in_ch, hidden_ch, kernel_size=3, padding=1),
                    nn.ReLU(),
                    nn.Conv2d(hidden_ch, hidden_ch, kernel_size=3, padding=1),
                    nn.ReLU(),
                )
                self.value_head = nn.Sequential(
                    nn.Flatten(),
                    nn.Linear(hidden_ch * 6 * 7, 128),
                    nn.ReLU(),
                    nn.Linear(128, 7),  # Q-values cho 7 cot
                )

            def forward(self, x: torch.Tensor) -> torch.Tensor:
                feat = self.features(x)
                return self.value_head(feat)

        return _TorchDQNNet(in_channels, hidden_channels)
