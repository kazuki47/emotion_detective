# backend/app/model.py

from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2FeatureExtractor
import torch

MODEL_NAME = "Bagus/wav2vec2-xlsr-japanese-speech-emotion-recognition"

model = Wav2Vec2ForSequenceClassification.from_pretrained(MODEL_NAME)
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(MODEL_NAME)
model.eval()
