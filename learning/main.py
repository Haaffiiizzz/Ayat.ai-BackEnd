import torch
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

# scalar = torch.tensor([[2, 3, 4], [4, 5, 5]])
# print(scalar.size)

# new = np.load(r"C:\Users\dadaa\Muktashif\001001_mfccs.npy")
# print(new.ndim)

# Random_Tensor = torch.rand(3, 4)
# print(Random_Tensor)

# Image_Tensor = torch.rand(size=(224, 224, 3))
# print(Image_Tensor)

# zero_tensor = torch.zeros(3, 4)
# print(zero_tensor)

# one_tensor = torch.ones(3, 4)
# print(one_tensor)

# num = np.ones((2,3))
# print(num)

# torch_range = torch.arange(1, 11)
# print(torch_range)

# like_tensor = torch.zeros_like(input=torch_range)
# print(like_tensor)

# new_tensor = torch.rand(3, 4)
# print(new_tensor)
# print(f"Dtype: {new_tensor.dtype}\nSize {new_tensor.size()}\ndevice {new_tensor.device}")

# tensor_one = torch.rand(2, 3)
# tensor_two = torch.rand(3, 2)
# print(torch.matmul(tensor_one, tensor_two))

print(torch.matmul(torch.rand(2, 3), torch.rand(3, 3)))