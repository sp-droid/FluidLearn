import numpy as np
import torch
from torch.utils.data import Dataset

def create_sequences(data, sequence_length, padding="zeros"): # Data must belong to a single case
    output = []
    if padding == "zeros":
        padded_data = np.concatenate([np.zeros((sequence_length - 1, *data.shape[1:])), data], axis=0)
    elif padding == "first":
        padded_data = np.concatenate([np.tile(data[0:1], (sequence_length - 1, *([1] * (data.ndim - 1)))), data], axis=0)
    else: 
        raise ValueError("Wrong padding value.")
    
    for i in range(len(data)):
        sequence = padded_data[i:i + sequence_length]
        output.append(sequence)
    return np.array(output)

class Normalize:
    def __init__(self, scaler):
        self.scaler = scaler

    def fit(self, data):
        self.shape = data.shape[1:]
        self.scaler.fit(data.reshape(-1,self.shape[0]))

    def fit_transform(self, data):
        self.shape = data.shape[1:]
        return self.scaler.fit_transform(data.reshape(-1,self.shape[0])).reshape((-1,) + self.shape)

    def transform(self, data):
        return self.scaler.transform(data.reshape(-1,self.shape[0])).reshape((-1,) + self.shape)
    
    def inverse_transform(self, data):
        return self.scaler.inverse_transform(data.reshape(-1,self.shape[0])).reshape((-1,) + self.shape)

class Dataset0D(Dataset):
    def __init__(self, inputs, outputs=None):
        self.inputs = torch.tensor(inputs, dtype=torch.float32)   # shape: (N, features)
        if outputs is None:
            self.outputs = None
        else:
            self.outputs = torch.tensor(outputs, dtype=torch.float32)   # shape: (N, features, H, W)

    def __len__(self):
        return self.inputs.shape[0]

    def __getitem__(self, i):
        if self.outputs is None: return self.inputs[i]
        
        return self.inputs[i], self.outputs[i] 

class Dataset0D2D(Dataset):
    def __init__(self, input_scalars, input_fields, output=None):
        self.input_scalars = torch.tensor(input_scalars, dtype=torch.float32)   # shape: (N, features)
        self.input_fields = torch.tensor(input_fields, dtype=torch.float32)     # shape: (N, features, H, W)
        if output is None:
            self.output = None
        else:
            self.output = torch.tensor(output, dtype=torch.float32)   # shape: (N, features, H, W)

    def __len__(self):
        return self.input_scalars.shape[0]

    def __getitem__(self, i):
        if self.output is None: return self.input_scalars[i], self.input_fields[i]
        
        return (self.input_scalars[i], self.input_fields[i]), self.output[i] 