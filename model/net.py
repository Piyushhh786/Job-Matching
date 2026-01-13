import torch
from torch import nn
from torch.nn import functional as F 
from joblib import load
vectorizer = load("tfidf_vectorizer.joblib")
# from normalizer.preprocess_data import process_sentence

# class
class Net(nn.Module):
    def __init__(self):
        input_size = 7193
        output_siz = 2
        hidden_size = 400
        super(Net,self).__init__()
        self.fc1 = torch.nn.Linear(input_size,hidden_size)
        self.fc2 = torch.nn.Linear(hidden_size,hidden_size)
        self.fc3 = torch.nn.Linear(hidden_size,output_siz)
    
    def forward(self,X):
        X = torch.relu((self.fc1(X)))
        X = torch.relu((self.fc2(X)))
        X = self.fc3(X)
        return F.log_softmax(X,dim=1)


def load_imp_sentence_classifier(
    checkpoint_path="imp_sentence_classifier.pth",
    lr=0.01,
):
    # 1 -> object of network
    model = Net()
    print("Working well")
    # 2️ -> Create optimizer (same as training)
    optimiser = torch.optim.Adam(model.parameters(), lr=lr)

    # 3 -> Load checkpoint
    checkpoint = torch.load(checkpoint_path)

    # 4 -> Restore states (most important)
    model.load_state_dict(checkpoint["model_state"])
    optimiser.load_state_dict(checkpoint["optimizer_state"])


    return model