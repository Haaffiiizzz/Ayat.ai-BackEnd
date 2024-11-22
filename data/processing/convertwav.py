import os
import ffmpeg

inputDir = r"C:\Users\dadaa\Sudais Verse by Verse"
outputDir = r"C:\Users\dadaa\Sudais Verse by Verse Wav"

if not os.path.exists(outputDir):
    os.makedirs(outputDir)

for folder in os.listdir(inputDir):
    folderPath = os.path.join(inputDir, folder)
    if os.path.isdir(folderPath):
        outputFolderPath = os.path.join(outputDir, folder)
        if not os.path.exists(outputFolderPath):
            os.makedirs(outputFolderPath)
        for file in os.listdir(folderPath):
            if file.endswith(".mp3"):
                inputFilePath = os.path.join(folderPath, file)
                outputFilePath = os.path.join(outputFolderPath, file.replace(".mp3", ".wav"))
                
                # Use ffmpeg to convert and resample the audio
                ffmpeg.input(inputFilePath).output(outputFilePath, ar=16000, ac=1, sample_fmt='s16').run()
