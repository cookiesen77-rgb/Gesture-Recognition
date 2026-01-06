import torch.nn as nn
import torch


class GRU(nn.Module):
    """GRU 神经网络模型，用于手势序列分类"""
    
    def __init__(self, in_dim, hidden_dim, num_layer, num_classes):
        super(GRU, self).__init__()
        self.in_dim = in_dim
        self.hidden_dim = hidden_dim
        self.num_layer = num_layer  # GRU网络层数
        
        # GRU 层
        self.gru = nn.GRU(
            input_size=in_dim, 
            hidden_size=hidden_dim, 
            num_layers=num_layer, 
            batch_first=True,
            dropout=0.5 if num_layer > 1 else 0  # dropout 只在多层时生效
        )
        
        # PReLU 激活函数，防止死亡 ReLU 问题
        self.activation = nn.PReLU()
        
        # 全连接分类层
        self.classifier = nn.Sequential(
            nn.Linear(in_features=hidden_dim, out_features=num_classes),
        )

    def forward(self, x):
        x, h_0 = x  # 将输入拆分为数据和隐藏状态
        batch_size = x.shape[0]
        
        # 通过 GRU 层
        out, h_t = self.gru(x, h_0)
        
        # 取最后一层的输出
        out = h_t[-1:, :, :]
        out = out.view(batch_size, -1)  # 调整维度 (1, b, hidden) => (b, hidden)
        
        # 全连接层 + 激活
        out = self.classifier(out)
        out = self.activation(out)
        
        return out, h_t


# 为了向后兼容，保留旧的变量名
# 注意：模型文件 model.pt 中使用的是旧属性名
class GRULegacy(nn.Module):
    """向后兼容的 GRU 模型（用于加载旧模型）"""
    
    def __init__(self, in_dim, hidden_dim, num_layer, num_classes):
        super(GRULegacy, self).__init__()
        self.in_dim = in_dim
        self.hidden_dim = hidden_dim
        self.num_layer = num_layer
        self.lstm = nn.GRU(input_size=in_dim, hidden_size=hidden_dim, num_layers=num_layer, batch_first=True,
                           dropout=0.5)
        self.relu = nn.PReLU()
        self.classes = nn.Sequential(
            nn.Linear(in_features=hidden_dim, out_features=num_classes),
        )

    def forward(self, x):
        x, h_0 = x
        batch_size = x.shape[0]
        out, h_t1 = self.lstm(x, h_0)
        out = h_t1[-1:, :, :]
        out = out.view(batch_size, -1)
        out = self.classes(out)
        out = self.relu(out)
        return out, h_t1
