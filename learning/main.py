import torch
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

x = torch.arange(1., 10.)
print(x, x.shape)

xReshaped = x.reshape(1, 7)
print(xReshaped)