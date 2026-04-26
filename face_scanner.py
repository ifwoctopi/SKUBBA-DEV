import time
from collections import defaultdict

class FaceScanner:
    def __init__(self, duration=3):
        self.duration = duration
        self.start_time = None
        self.scanning = True
        self.prediction_scores = defaultdict(list)
        self.results = []

    def start(self):
        if self.start_time is None:
            self.start_time = time.time()

    def add_prediction(self, label, confidence):
        if self.scanning:
            self.prediction_scores[label].append(confidence)

    def update(self):
        if not self.scanning or self.start_time is None:
            return

        elapsed = time.time() - self.start_time

        if elapsed >= self.duration:
            self.scanning = False
            self.compute_results()

    def compute_results(self):
        averaged = []
        for label, scores in self.prediction_scores.items():
            avg_conf = sum(scores) / len(scores)
            averaged.append((label, avg_conf))

        self.results = sorted(averaged, key=lambda x: x[1], reverse=True)

    def reset(self):
        self.start_time = None
        self.scanning = True
        self.prediction_scores.clear()
        self.results = []