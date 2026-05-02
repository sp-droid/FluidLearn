import torch
from torch import nn
from torchinfo import summary
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from IPython.display import clear_output

class BaseRegressionModel(nn.Module):
    def __init__(self, loss, device):
        super().__init__()
        
        self.loss = loss()
        self.loss_unreduced = loss(reduction="none")
        self.device = device

    # Return more information about the model
    def extra_repr(self):
        message = f"device={self.device}"
        return message
    
    # Summary method to display model architecture
    def summary(self, input_data):
        print(summary(self, input_data=(self.X_to_device(input_data, self.device),)))

    # Convert input data to the appropriate device regardless of the dimension
    @staticmethod
    def X_to_device(X, device):
        if isinstance(X, tuple) or isinstance(X, list):
            return tuple(x.to(device) for x in X)
        else:
            return X.to(device)

    # Plot training and validation loss
    def fit_plot(self, epoch, epochs):
        clear_output(wait=True)
        plt.figure(figsize=(8, 4))
        plt.plot(np.arange(1, epoch + 2), self.history["train_loss"], linewidth=2, label="Train")
        plt.plot(np.arange(1, epoch + 2), self.history["val_loss"], linewidth=2, label="Validation")
        plt.xlabel("Epoch")
        plt.ylabel(self.loss._get_name())
        plt.yscale("log")
        plt.xlim(1, epochs)
        plt.title(f"Epoch {epoch+1}/{epochs} - Train Loss: {self.history["train_loss"][-1]:.2e} - Val Loss: {self.history["val_loss"][-1]:.2e}")
        plt.legend()
        plt.show()

    # Train the model
    def fit(self,
        train_dataloader,
        val_dataloader,
        epochs,
        optimizer = lambda model: torch.optim.AdamW(model.parameters(), lr=1e-3),
        epoch_plot_interval = None
    ):
        self.optimizer = optimizer(self)
        best_val_loss = float("inf")
        best_weights = None

        self.history = {"train_loss": [], "val_loss": []}
        progress_bar = tqdm(range(epochs), desc="Training", unit="epoch")
        for epoch in progress_bar:
            # Training
            self.train()
            train_loss = 0
            for batch, (X, y) in enumerate(train_dataloader):
                X, y = self.X_to_device(X, self.device), y.to(self.device)
                # Zero parameter gradients
                self.optimizer.zero_grad()
                # Compute prediction error
                pred = self(X)
                loss = self.loss(pred, y)
                # Backpropagation
                loss.backward()
                self.optimizer.step()

                train_loss += loss.item()
            train_loss /= len(train_dataloader)
            self.history["train_loss"].append(train_loss)

            # Validation
            val_loss = self.validate(val_dataloader)
            self.history["val_loss"].append(val_loss)

            # Save best weights
            if epoch/epochs > 0.75 and val_loss < best_val_loss:
                best_val_loss = val_loss
                best_weights = {k: v.cpu().clone() for k, v in self.state_dict().items()}
            
            progress_bar.set_postfix(train_loss=train_loss, val_loss=val_loss)
            
            if epoch_plot_interval is not None and epoch > 0:
                if epoch % epoch_plot_interval == 0 or epoch == epochs - 1:
                    self.fit_plot(epoch, epochs)
        
        # Load best weights
        if epochs > 10: self.load_state_dict(best_weights)

        return self.history
    
    # Validate the model
    def validate(self, val_dataloader, reduced_error=True):
        self.eval()
        if reduced_error: val_loss = 0
        else: val_loss = np.zeros_like(next(iter(val_dataloader))[1].numpy())
        with torch.no_grad():
            for X, y in val_dataloader:
                X, y = self.X_to_device(X, self.device), y.to(self.device)
                pred = self(X)
                if reduced_error: val_loss += self.loss(pred, y).item()
                else: val_loss += self.loss_unreduced(pred, y).cpu().numpy()
        val_loss /= len(val_dataloader)
        return val_loss

    # Make predictions    
    def predict(self, test_dataloader):
        self.eval()
        predictions = []
        with torch.no_grad():
            for X in test_dataloader:
                X = self.X_to_device(X, self.device)
                pred = self(X)
                predictions.append(pred.cpu())
        predictions = torch.cat(predictions, dim=0)
        return predictions
    
    # Make autoregressive prediction NO batches
    def predict_autoregressive(self, test_dataloader, n_snaps, progress_bar=True):
        self.eval()
        predictions_snaps = []

        with torch.no_grad():
            X = next(iter(test_dataloader)) # Only the first snapshot is used
            scalars, fields = self.X_to_device(X, self.device)

            progress_bar = tqdm(range(n_snaps), desc="Autoregressive prediction", unit="Snapshot", disable=not progress_bar)
            for _ in progress_bar:
                X_snap = (scalars, fields)
                pred = self(X_snap)
                
                fields = pred
                predictions_snaps.append(pred.cpu())

        return predictions_snaps

    # Validate autoregression NO batches
    def validate_autoregressive(self, val_dataloader, reduced_error=True, return_predictions=False, progress_bar=True):
        self.eval()
        predictions_snaps = []
        losses = []

        with torch.no_grad():
            X, _ = next(iter(val_dataloader))
            scalars, fields = self.X_to_device(X, self.device)

            progress_bar = tqdm(val_dataloader, desc="Autoregressive validation", unit="Snapshot", disable=not progress_bar)
            for _, y_snap in progress_bar:
                X_snap, y_snap = (scalars, fields), y_snap.to(self.device)
                pred = self(X_snap)
                
                fields = pred
                if reduced_error:losses.append(self.loss(pred, y_snap).item())
                else: losses.append(self.loss_unreduced(pred, y_snap).cpu().numpy())
                if return_predictions: predictions_snaps.append(pred.cpu())

        if return_predictions: return losses, predictions_snaps
        return losses