from torch import nn
import torch.nn.functional as F
from dgl.nn.pytorch import GraphConv
from torch.nn.modules.batchnorm import BatchNorm1d

class GCN(nn.Module):
    def __init__(self, feature_size, hidden_size, num_classes, dropout_rate = 0.5):
        super(GCN, self).__init__()

        
        self.gcn = nn.Sequential(
            GraphConv(in_feats=feature_size, out_feats=hidden_size, activation=nn.ReLU()),
            nn.Dropout(dropout_rate),
            GraphConv(in_feats=hidden_size, out_feats=num_classes),
        )

    def forward(self, graph, n_feats):
        x = n_feats

        for layer in self.gcn:
            if isinstance(layer, GraphConv):
                x = layer(graph, x)
            else:
                x = layer(x)
        
        return x

class ParametrizeGCN(nn.Module):
    def __init__(self, feature_size, hidden_size, num_layers, num_classes, dropout_rate = 0.5):
        super(ParametrizeGCN, self).__init__()

        layers = []

        if num_layers == 1:
            layers.append(GraphConv(in_feats=feature_size, out_feats=num_classes))
        elif num_layers == 2:
            layers.append(GraphConv(in_feats=feature_size, out_feats=hidden_size, activation=nn.ReLU()))
            layers.append(nn.Dropout(dropout_rate))
            layers.append(GraphConv(in_feats=hidden_size, out_feats=num_classes))
        else:
            layers.append(GraphConv(in_feats=feature_size, out_feats=hidden_size, activation=nn.ReLU()))
            layers.append(nn.Dropout(dropout_rate))
            
            for _ in range(num_layers - 2):
                layers.append(GraphConv(in_feats=hidden_size, out_feats=hidden_size, activation=nn.ReLU()))
                layers.append(nn.Dropout(dropout_rate))
            
            layers.append(GraphConv(in_feats=hidden_size, out_feats=num_classes))
    
        self.gcn = nn.Sequential(*layers)

    def forward(self, graph, n_feats):
        x = n_feats

        for layer in self.gcn:
            if isinstance(layer, GraphConv):
                x = layer(graph, x)
            else:
                x = layer(x)
        
        return x


class GCNBlock(nn.Module):
    def __init__(self, in_feats, out_feats, activation, dropout_rate=0.5):
        super().__init__()

        self.block = nn.Sequential(
            GraphConv(in_feats=in_feats, out_feats=out_feats, activation=activation),
            BatchNorm1d(out_feats),
            nn.Dropout(dropout_rate)
        )

    def forward(self, graph, n_feats, normalize=False):
        x = n_feats

        for layer in self.block:
            if isinstance(layer, GraphConv):
                x = layer(graph, x)
            else:
                x = layer(x)
        # TODO: normalize features: x = x / torch.norm(x)
        return x

class GCNWithBlocks(nn.Module):
    def __init__(self, feature_size, hidden_size, num_classes, dropout_rate = 0.5):
        super(GCNWithBlocks, self).__init__()

        self.preprocessing = nn.Linear(in_features=feature_size, out_features=feature_size)

        self.gcn = nn.Sequential(
            GCNBlock(in_feats=feature_size, out_feats=hidden_size, activation=nn.ReLU()),
            GCNBlock(in_feats=hidden_size, out_feats=num_classes, activation=None)
        )

        self.postprocessing = nn.Linear(in_features=num_classes, out_features=num_classes)

    def forward(self, graph, n_feats):
        x = n_feats

        x = F.relu(self.postprocessing(x))

        for block in self.gcn:
            x = block(graph, x)

        x = self.postprocessing(x)

        return x
