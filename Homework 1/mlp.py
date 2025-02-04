import torch
import torch
import torch.nn as nn
import torch.nn.functional as F


class MLP:
    def __init__(
        self,
        linear_1_in_features,
        linear_1_out_features,
        f_function,
        linear_2_in_features,
        linear_2_out_features,
        g_function
    ):
        """
        Args:
            linear_1_in_features: the in features of first linear layer
            linear_1_out_features: the out features of first linear layer
            linear_2_in_features: the in features of second linear layer
            linear_2_out_features: the out features of second linear layer
            f_function: string for the f function: relu | sigmoid | identity
            g_function: string for the g function: relu | sigmoid | identity
        """
        self.f_function = f_function
        self.g_function = g_function

        self.parameters = dict(
            W1 = torch.randn(linear_1_out_features, linear_1_in_features),
            b1 = torch.randn(linear_1_out_features),
            W2 = torch.randn(linear_2_out_features, linear_2_in_features),
            b2 = torch.randn(linear_2_out_features),
        )
        self.grads = dict(
            dJdW1 = torch.zeros(linear_1_out_features, linear_1_in_features),
            dJdb1 = torch.zeros(linear_1_out_features),
            dJdW2 = torch.zeros(linear_2_out_features, linear_2_in_features),
            dJdb2 = torch.zeros(linear_2_out_features),
        )

        # put all the cache value you need in self.cache
        self.cache = dict()

    def forward(self, x):
        """
        Args:
            x: tensor shape (batch_size, linear_1_in_features)
        """
        # TODO: Implement the forward function
        activation_mapping = {'relu':nn.ReLU(), 'sigmoid':nn.Sigmoid(), 'identity':nn.Identity()}
        z1 = torch.matmul(x, self.parameters['W1'].t()) + torch.ger(torch.ones(x.shape[0]), self.parameters['b1'])
        z2 = activation_mapping[self.f_function](z1)
        z3 = torch.matmul(z2, self.parameters['W2'].t()) + torch.ger(torch.ones(x.shape[0]), self.parameters['b2'])
        y_hat = activation_mapping[self.g_function](z3)
        self.cache['z1'] = z1
        self.cache['z2'] = z2
        self.cache['z3'] = z3
        self.cache['x'] = x
        
        return y_hat
    
    def backward(self, dJdy_hat):
        """
        Args:
            dJdy_hat: The gradient tensor of shape (batch_size, linear_2_out_features)
        """
        # TODO: Implement the backward function
        batch_size = dJdy_hat.shape[0]
        
        def grad(function, input_):
            grad_mappings = {'relu':torch.ones(input_.size()) * (input_ > 0), 
#                          'sigmoid':torch.exp(-input_)*(1+torch.exp(-input_))**(-2), 
                         'sigmoid':(1/(1+torch.exp(-input_)))*(1-(1/(1+torch.exp(-input_)))), 
                         'identity':torch.ones(input_.size())}
            return grad_mappings[function]
        
        dz1dW1= self.cache['x'].t()
        dz1db1= torch.ones(self.cache['x'].shape[0])
        dz2dz1 = grad(self.f_function, self.cache['z1'])
        dz3dz2 = self.parameters['W2']
        dz3dW2= self.cache['z2'].t()
        dz3db2= torch.ones(self.cache['z2'].shape[0])
        dy_hatdz3 = grad(self.g_function, self.cache['z3'])
        
        self.grads['dJdW1'] = torch.matmul(dz1dW1, torch.matmul(dJdy_hat * dy_hatdz3, dz3dz2) * dz2dz1).t()
        self.grads['dJdb1'] = torch.matmul(dz1db1, torch.matmul(dJdy_hat * dy_hatdz3, dz3dz2) * dz2dz1)
        self.grads['dJdW2'] = torch.matmul(dz3dW2, dJdy_hat * dy_hatdz3).t()
        self.grads['dJdb2'] = torch.matmul(dz3db2, dJdy_hat * dy_hatdz3)

    
    def clear_grad_and_cache(self):
        for grad in self.grads:
            self.grads[grad].zero_()
        self.cache = dict()

def mse_loss(y, y_hat):
    """
    Args:
        y: the label tensor (batch_size, linear_2_out_features)
        y_hat: the prediction tensor (batch_size, linear_2_out_features)

    Return:
        J: scalar of loss
        dJdy_hat: The gradient tensor of shape (batch_size, linear_2_out_features)
    """
    # TODO: Implement the mse loss
    loss = (0.5*(y_hat - y)**2).mean()
    dJdy_hat = (y_hat - y)/(y.shape[0]*y.shape[1])

    return loss, dJdy_hat

def bce_loss(y, y_hat):
    """
    Args:
        y_hat: the prediction tensor
        y: the label tensor
        
    Return:
        loss: scalar of loss
        dJdy_hat: The gradient tensor of shape (batch_size, linear_2_out_features)
    """
    # TODO: Implement the bce loss
    loss = - (y * torch.clamp(torch.log(y_hat), min=-100) + (1-y) * torch.clamp(torch.log(1-y_hat), min=-100)).mean()
    dJdy_hat = (- y/y_hat + (1-y)/(1-y_hat))/(y.shape[0]*y.shape[1])
    
    return loss, dJdy_hat











