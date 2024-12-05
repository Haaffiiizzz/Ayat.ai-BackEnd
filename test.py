
import numpy as np
import os
import matplotlib.pyplot as plt

folderDir = r"C:\Users\dadaa\Sudais New"
for folder in os.listdir(folderDir):
    folderPath = os.path.join(folderDir, folder)
    
    for file in os.listdir(folderPath): 
    
        filePath = os.path.join(folderPath, file)
        numpyArray = np.load(filePath)
        plt.figure(figsize=(10, 6))
        plt.imshow(numpyArray, aspect='auto', origin='lower', cmap='viridis')
        plt.colorbar(label="Intensity")
        plt.title(file)
        plt.xlabel("Time")
        plt.ylabel("Frequency")
        plt.show()
    break
