import torch
from torch import nn

from .models_base import BaseRegressionModel

class FFN0D(BaseRegressionModel):
    """A simple feed-forward neural network model for regression tasks."""
    def __init__(self, loss, device):
        super().__init__(loss=loss, device=device)

        b = 16
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(6+4*6, 32),
            nn.ReLU(),
            nn.Linear(32, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 3)
        )

    def forward(self, X):
        y = self.linear_relu_stack(X)
        return y

class FFN(BaseRegressionModel):
    """A simple feed-forward neural network model for regression tasks."""
    def __init__(self, loss, device):
        super().__init__(loss=loss, device=device)

        self.flatten = nn.Flatten()

        b = 512
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(32*64*3+1, b),
            nn.ReLU(),
            nn.Linear(b, b),
            nn.ReLU(),
            nn.Linear(b, b),
            nn.ReLU(),
            nn.Linear(b, 32*64*3)
        )

    def forward(self, X):
        x0D, x2D = X
        y = self.flatten(x2D)
        y = torch.cat([y, x0D], dim=1)
        y = self.linear_relu_stack(y)
        y = y.view(-1, 3, 32, 64)
        return y

from torch.nn import TransformerEncoder, TransformerEncoderLayer
class TransformerRegressor(BaseRegressionModel):
    """A minimal Transformer-based regression model."""
    def __init__(self, loss, device):
        super().__init__(loss=loss, device=device)

        self.flatten = nn.Flatten()

        # --- Transformer dimensions ---
        self.input_dim = 32 * 64 * 3 + 1      # flattened + x0D extra
        self.d_model = 128                  # internal feature size
        self.nhead = 4                      # number of attention heads
        self.ff_dim = 256                   # feedforward network dimension

        # split into tokens
        self.num_tokens = (self.input_dim + self.d_model - 1) // self.d_model
        self.pad_dim = self.num_tokens * self.d_model - self.input_dim

        # --- Project flattened input to d_model ---
        # self.input_proj = nn.Linear(self.seq_len, self.d_model)

        # --- Single transformer layer (smallest usable) ---
        encoder_layer = TransformerEncoderLayer(
            d_model=self.d_model,
            nhead=self.nhead,
            dim_feedforward=self.ff_dim,
            batch_first=True
        )
        self.transformer = TransformerEncoder(encoder_layer, num_layers=1)

        # --- Project back to output size ---
        self.output_proj = nn.Linear(self.num_tokens * self.d_model, 32 * 64 * 3)

    def forward(self, X):
        x0D, x2D = X

        y = self.flatten(x2D)           # (batch, 32*64*3)
        y = torch.cat([y, x0D], dim=1)  # (batch, 32*64*3+1)

        # Project to transformer dimension
        # y = self.input_proj(y)          # (batch, d_model)
        if self.pad_dim > 0:
            pad = torch.zeros(y.size(0), self.pad_dim, device=y.device)
            y = torch.cat([y, pad], dim=1)
        y = y.view(-1, self.num_tokens, self.d_model)

        # Transformer expects a sequence → treat entire vector as seq_len=1
        # y = y.unsqueeze(1)              # (batch, 1, d_model)
        y = self.transformer(y)         # (batch, 1, d_model)
        # y = y.squeeze(1)                # (batch, d_model)
        y = y.reshape(y.size(0), -1)    # (batch, num_tokens * d_model)

        # Project back to pixel space
        y = self.output_proj(y)         # (batch, 32*64*3)

        # Reshape into (batch, C, H, W)
        y = y.view(-1, 3, 32, 64)

        return y

class sequenceTestModel(BaseRegressionModel):
    """FFN adapted for sequence data"""
    def __init__(self, loss, device):
        super().__init__(loss=loss, device=device)

        self.flatten = nn.Flatten(start_dim=2) # LSTMs expect input shape [batch_size, sequence_length, features]

        b = 512
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(32*64*3+1, b),
            nn.ReLU(),
            nn.Linear(b, b),
            nn.ReLU(),
            nn.Linear(b, b),
            nn.ReLU(),
            nn.Linear(b, 32*64*3)
        )

    def forward(self, X):
        x0D, x2D = X

        y = self.flatten(x2D)
        y = torch.cat([y, x0D], dim=2)

        y = y[:, -1, :]
        y = self.linear_relu_stack(y)
        y = y.view(-1, 3, 32, 64)
 
        return y

class LSTM(BaseRegressionModel):
    def __init__(self, loss, device):
        super().__init__(loss=loss, device=device)

        self.conv = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=2, stride=1, padding=1),
            nn.Conv2d(16, 16, kernel_size=2, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),  # Downsample
            nn.Conv2d(16, 32, kernel_size=2, stride=1, padding=1),
            nn.Conv2d(32, 32, kernel_size=2, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),  # Downsample
            nn.Conv2d(32, 64, kernel_size=2, stride=1, padding=1),
            nn.Conv2d(64, 64, kernel_size=2, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),  # Downsample
        )

        b1 = 768
        b2 = 512
        self.hidden_size = b1
        self.num_layers = 1
        self.lstm = nn.LSTM(input_size=2880+1, hidden_size=self.hidden_size, num_layers=self.num_layers, batch_first=True) # Batch before sequence
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(b1, b2),
            nn.ReLU(),
            nn.Linear(b2, b2),
            nn.ReLU(),
            nn.Linear(b2, b2),
            nn.ReLU(),
            nn.Linear(b2, 32*64*3)
        )

    def forward(self, X, h0=None, c0=None):
        x0D, x2D = X

        y = x2D.view(x2D.shape[0] * x2D.shape[1], x2D.shape[2], x2D.shape[3], x2D.shape[4])
        y = self.conv(y)

        y = y.view(x2D.shape[0], x2D.shape[1], -1) # LSTMs expect input shape [batch_size, sequence_length, features]
        y = torch.cat([y, x0D], dim=2)

        if h0 is None or c0 is None:
            h0 = torch.zeros(self.num_layers, y.shape[0], self.hidden_size).to(self.device)
            c0 = torch.zeros(self.num_layers, y.shape[0], self.hidden_size).to(self.device)
        y, (hn, cn) = self.lstm(y, (h0, c0))
        y = y[:, -1, :]
        y = self.linear_relu_stack(y)
        y = y.view(-1, 3, 32, 64)
 
        return y

class UNet(BaseRegressionModel):
    def __init__(self, loss, device):
        super().__init__(loss=loss, device=device)

        self.contractingC1 = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(16, 16, kernel_size=3, stride=1, padding=1),
            nn.ReLU()
        )
        self.contractingC2 = self.contractingBlock(16)
        self.contractingC3 = self.contractingBlock(32)
        
        self.contractingNeck = nn.Sequential(
            nn.MaxPool2d(kernel_size=2, stride=2), # 16x32
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(128, 128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            # nn.Dropout2d(p=0.5)
        )
        # Scalars feature map injection +2
        self.expandingNeck = nn.Sequential(
            nn.ConvTranspose2d(130, 64, kernel_size=2, stride=2),
            nn.ReLU()
        )

        # Skip connection x2
        self.expandingE3 = self.expandingBlock(128)
        # Skip connection x2
        self.expandingE2 = self.expandingBlock(64)
        # Skip connection x2
        self.expandingE1 = nn.Sequential(
            nn.Conv2d(32, 16, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(16, 16, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(16, 3, kernel_size=1, stride=1, padding=0)  # Output layer
        )

    @staticmethod
    def contractingBlock(feature_channels):
        return nn.Sequential(
            nn.MaxPool2d(kernel_size=2, stride=2), # 16x32
            nn.Conv2d(feature_channels, feature_channels*2, kernel_size=3, stride=1, padding=1), # 32x64
            nn.ReLU(),
            nn.Conv2d(feature_channels*2, feature_channels*2, kernel_size=3, stride=1, padding=1),
            nn.ReLU()
        )

    @staticmethod
    def expandingBlock(feature_channels):
        return nn.Sequential(
            nn.Conv2d(feature_channels, feature_channels // 2, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(feature_channels // 2, feature_channels // 2, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(feature_channels // 2, feature_channels // 4, kernel_size=2, stride=2),
            nn.ReLU()
        )

    def forward(self, X):
        x0D, x2D = X

        C1 = self.contractingC1(x2D)
        C2 = self.contractingC2(C1)
        C3 = self.contractingC3(C2)
        
        neck = self.contractingNeck(C3)
        scalar_map = x0D[:, :, None, None].expand(-1, -1, neck.shape[2], neck.shape[3])

        neck = torch.cat([neck, scalar_map], dim=1)
        neck = self.expandingNeck(neck)

        E3 = self.expandingE3(torch.cat([C3, neck], dim=1))
        E2 = self.expandingE2(torch.cat([C2, E3], dim=1))
        E1 = self.expandingE1(torch.cat([C1, E2], dim=1))
        y = E1.view(-1, x2D.shape[1], x2D.shape[2], x2D.shape[3])
        return y