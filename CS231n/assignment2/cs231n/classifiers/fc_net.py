import numpy as np

from cs231n.layers import *
from cs231n.layer_utils import *

relu = lambda x: x * (x > 0)

class TwoLayerNet(object):
  """
  A two-layer fully-connected neural network with ReLU nonlinearity and
  softmax loss that uses a modular layer design. We assume an input dimension
  of D, a hidden dimension of H, and perform classification over C classes.
  
  The architecure should be affine - relu - affine - softmax.

  Note that this class does not implement gradient descent; instead, it
  will interact with a separate Solver object that is responsible for running
  optimization.

  The learnable parameters of the model are stored in the dictionary
  self.params that maps parameter names to numpy arrays.
  """
  
  def __init__(self, input_dim=3*32*32, hidden_dim=100, num_classes=10,
               weight_scale=1e-3, reg=0.0):
    """
    Initialize a new network.

    Inputs:
    - input_dim: An integer giving the size of the input
    - hidden_dim: An integer giving the size of the hidden layer
    - num_classes: An integer giving the number of classes to classify
    - dropout: Scalar between 0 and 1 giving dropout strength.
    - weight_scale: Scalar giving the standard deviation for random
      initialization of the weights.
    - reg: Scalar giving L2 regularization strength.
    """
    self.params = {}
    self.reg = reg
    
    ############################################################################
    # TODO: Initialize the weights and biases of the two-layer net. Weights    #
    # should be initialized from a Gaussian with standard deviation equal to   #
    # weight_scale, and biases should be initialized to zero. All weights and  #
    # biases should be stored in the dictionary self.params, with first layer  #
    # weights and biases using the keys 'W1' and 'b1' and second layer weights #
    # and biases using the keys 'W2' and 'b2'.                                 #
    ############################################################################
    W1 = weight_scale * np.random.randn(input_dim, hidden_dim)
    b1 = np.zeros(hidden_dim)
    W2 = weight_scale * np.random.randn(hidden_dim, num_classes)
    b2 = np.zeros(num_classes)
    
    self.params['W1'] = W1
    self.params['b1'] = b1
    self.params['W2'] = W2
    self.params['b2'] = b2
    ############################################################################
    #                             END OF YOUR CODE                             #
    ############################################################################


  def loss(self, X, y=None):
    """
    Compute loss and gradient for a minibatch of data.

    Inputs:
    - X: Array of input data of shape (N, d_1, ..., d_k)
    - y: Array of labels, of shape (N,). y[i] gives the label for X[i].

    Returns:
    If y is None, then run a test-time forward pass of the model and return:
    - scores: Array of shape (N, C) giving classification scores, where
      scores[i, c] is the classification score for X[i] and class c.

    If y is not None, then run a training-time forward and backward pass and
    return a tuple of:
    - loss: Scalar value giving the loss
    - grads: Dictionary with the same keys as self.params, mapping parameter
      names to gradients of the loss with respect to those parameters.
    """  
    scores = None
    ############################################################################
    # TODO: Implement the forward pass for the two-layer net, computing the    #
    # class scores for X and storing them in the scores variable.              #
    ############################################################################
    W1 = self.params['W1']
    b1 = self.params['b1']
    W2 = self.params['W2']
    b2 = self.params['b2']
    reg = self.reg
    
    N, D = X.shape[0], np.prod(X.shape[1:])
    X = X.reshape(N, D)
    
    layer1 = X.dot(W1)+b1
    layer2 = relu(layer1)
    layer3 = layer2.dot(W2) + b2

    scores = layer3 # no need to make two variables, but more readable this way. #relu(X.dot(W1)+b1).dot(W2) + b2
    
    ############################################################################
    #                             END OF YOUR CODE                             #
    ############################################################################

    # If y is None then we are in test mode so just return scores
    if y is None:
      return scores
    
    loss, grads = 0, {}
    ############################################################################
    # TODO: Implement the backward pass for the two-layer net. Store the loss  #
    # in the loss variable and gradients in the grads dictionary. Compute data #
    # loss using softmax, and make sure that grads[k] holds the gradients for  #
    # self.params[k]. Don't forget to add L2 regularization!                   #
    #                                                                          #
    # NOTE: To ensure that your implementation matches ours and you pass the   #
    # automated tests, make sure that your L2 regularization includes a factor #
    # of 0.5 to simplify the expression for the gradient.                      #
    ############################################################################
    rows = np.sum(np.exp(layer3), axis=1)
    layer4 = np.sum(-layer3[range(N), y]+np.log(rows) ) / N
    # loss = np.sum(-scores[range(N), y]+np.log(np.sum(np.exp(scores), axis=1)) ) / N
    # loss += 0.5 * reg * (np.sum(W1*W1) + np.sum(W2*W2))
    loss = layer4 + 0.5 * reg * (np.sum(W1*W1) + np.sum(W2*W2))
    
    dlayer4 = 1.0

    # Gradient of np.log(np.sum(np.exp(layer3), axis=1))
    dlayer3 = (np.exp(scores).T / rows).T
    # Gradient of -layer3[range(N), y]:
    ys = np.zeros(dlayer3.shape)
    ys[range(N), y] = 1
    dlayer3 -= ys
    # / N term
    dlayer3 /= N
    # Chain rule
    dlayer3 *= dlayer4

    # Chain rule, element-wise multiplication works out
    dlayer2 = dlayer3.dot(W2.T)

    # Relu gradient
    dlayer1 = dlayer2 * (layer1>=0)

    dW1 = X.T.dot(dlayer1)
    dW2 = layer2.T.dot(dlayer3)

    # Same as matrix multiplication with 1-vector, chain rule works out
    db1 = np.sum(dlayer1, axis=0)
    db2 = np.sum(dlayer3, axis=0)

    # Regularization
    dW1 += reg * W1
    dW2 += reg * W2

    # Store
    grads['W1'] = dW1
    grads['W2'] = dW2
    grads['b1'] = db1
    grads['b2'] = db2
    ############################################################################
    #                             END OF YOUR CODE                             #
    ############################################################################

    return loss, grads


class FullyConnectedNet(object):
  """
  A fully-connected neural network with an arbitrary number of hidden layers,
  ReLU nonlinearities, and a softmax loss function. This will also implement
  dropout and batch normalization as options. For a network with L layers,
  the architecture will be
  
  {affine - [batch norm] - relu - [dropout]} x (L - 1) - affine - softmax
  
  where batch normalization and dropout are optional, and the {...} block is
  repeated L - 1 times.
  
  Similar to the TwoLayerNet above, learnable parameters are stored in the
  self.params dictionary and will be learned using the Solver class.
  """

  def __init__(self, hidden_dims, input_dim=3*32*32, num_classes=10,
               dropout=0, use_batchnorm=False, reg=0.0,
               weight_scale=1e-2, dtype=np.float32, seed=None):
    """
    Initialize a new FullyConnectedNet.
    
    Inputs:
    - hidden_dims: A list of integers giving the size of each hidden layer.
    - input_dim: An integer giving the size of the input.
    - num_classes: An integer giving the number of classes to classify.
    - dropout: Scalar between 0 and 1 giving dropout strength. If dropout=0 then
      the network should not use dropout at all.
    - use_batchnorm: Whether or not the network should use batch normalization.
    - reg: Scalar giving L2 regularization strength.
    - weight_scale: Scalar giving the standard deviation for random
      initialization of the weights.
    - dtype: A numpy datatype object; all computations will be performed using
      this datatype. float32 is faster but less accurate, so you should use
      float64 for numeric gradient checking.
    - seed: If not None, then pass this random seed to the dropout layers. This
      will make the dropout layers deteriminstic so we can gradient check the
      model.
    """
    self.use_batchnorm = use_batchnorm
    self.use_dropout = dropout > 0
    self.reg = reg
    self.num_layers = 1 + len(hidden_dims)
    self.dtype = dtype
    self.params = {}

    ############################################################################
    # TODO: Initialize the parameters of the network, storing all values in    #
    # the self.params dictionary. Store weights and biases for the first layer #
    # in W1 and b1; for the second layer use W2 and b2, etc. Weights should be #
    # initialized from a normal distribution with standard deviation equal to  #
    # weight_scale and biases should be initialized to zero.                   #
    #                                                                          #
    # When using batch normalization, store scale and shift parameters for the #
    # first layer in gamma1 and beta1; for the second layer use gamma2 and     #
    # beta2, etc. Scale parameters should be initialized to one and shift      #
    # parameters should be initialized to zero.                                #
    ############################################################################
    self.L = len(hidden_dims) + 1
    self.N = input_dim
    self.C = num_classes
    dims = [self.N] + hidden_dims + [self.C]
    Ws = {'W' + str(i + 1):
         weight_scale * np.random.randn(dims[i], dims[i + 1]) for i in range(len(dims) - 1)}
    b = {'b' + str(i + 1): np.zeros(dims[i + 1])
         for i in range(len(dims) - 1)}
    
    self.params.update(b)
    self.params.update(Ws)
    
    if self.use_batchnorm:
        gammas = {'gamma' + str(i + 1):
                  np.ones(dims[i + 1]) for i in range(len(dims) - 2)}
        betas = {'beta' + str(i + 1): np.zeros(dims[i + 1])
                 for i in range(len(dims) - 2)}

        self.params.update(betas)
        self.params.update(gammas)
    ############################################################################
    #                             END OF YOUR CODE                             #
    ############################################################################

    # When using dropout we need to pass a dropout_param dictionary to each
    # dropout layer so that the layer knows the dropout probability and the mode
    # (train / test). You can pass the same dropout_param to each dropout layer.
    self.dropout_param = {}
    if self.use_dropout:
      self.dropout_param = {'mode': 'train', 'p': dropout}
      if seed is not None:
        self.dropout_param['seed'] = seed
    
    # With batch normalization we need to keep track of running means and
    # variances, so we need to pass a special bn_param object to each batch
    # normalization layer. You should pass self.bn_params[0] to the forward pass
    # of the first batch normalization layer, self.bn_params[1] to the forward
    # pass of the second batch normalization layer, etc.
    self.bn_params = []
    if self.use_batchnorm:
      self.bn_params = [{'mode': 'train'} for i in xrange(self.num_layers - 1)]
    
    # Cast all parameters to the correct datatype
    for k, v in self.params.iteritems():
      self.params[k] = v.astype(dtype)


  def loss(self, X, y=None):
    """
    Compute loss and gradient for the fully-connected net.

    Input / output: Same as TwoLayerNet above.
    """
    X = X.astype(self.dtype)
    mode = 'test' if y is None else 'train'

    # Set train/test mode for batchnorm params and dropout param since they
    # behave differently during training and testing.
    if self.dropout_param is not None:
      self.dropout_param['mode'] = mode   
    if self.use_batchnorm:
      for bn_param in self.bn_params:
        bn_param[mode] = mode

    scores = None
    ############################################################################
    # TODO: Implement the forward pass for the fully-connected net, computing  #
    # the class scores for X and storing them in the scores variable.          #
    #                                                                          #
    # When using dropout, you'll need to pass self.dropout_param to each       #
    # dropout forward pass.                                                    #
    #                                                                          #
    # When using batch normalization, you'll need to pass self.bn_params[0] to #
    # the forward pass for the first batch normalization layer, pass           #
    # self.bn_params[1] to the forward pass for the second batch normalization #
    # layer, etc.                                                              #
    ############################################################################
    
    hidden = {}
    hidden['h0'] = X.reshape(X.shape[0], np.prod(X.shape[1:]))
    if self.use_dropout:
        # dropout on the input layer
        hdrop, cache_hdrop = dropout_forward(
            hidden['h0'], self.dropout_param)
        hidden['hdrop0'], hidden['cache_hdrop0'] = hdrop, cache_hdrop

    for i in range(self.L):
        idx = i + 1
        # Naming of the variable
        w = self.params['W' + str(idx)]
        b = self.params['b' + str(idx)]
        h = hidden['h' + str(idx - 1)]
        if self.use_dropout:
            h = hidden['hdrop' + str(idx - 1)]
        if self.use_batchnorm and idx != self.L:
            gamma = self.params['gamma' + str(idx)]
            beta = self.params['beta' + str(idx)]
            bn_param = self.bn_params[i]

        # Computing of the forward pass.
        # Special case of the last layer (output)
        if idx == self.L:
            h, cache_h = affine_forward(h, w, b)
            hidden['h' + str(idx)] = h
            hidden['cache_h' + str(idx)] = cache_h

        # For all other layers
        else:
            if self.use_batchnorm:
                h, cache_h = affine_norm_relu_forward(
                    h, w, b, gamma, beta, bn_param)
                hidden['h' + str(idx)] = h
                hidden['cache_h' + str(idx)] = cache_h
            else:
                h, cache_h = affine_relu_forward(h, w, b)
                hidden['h' + str(idx)] = h
                hidden['cache_h' + str(idx)] = cache_h

            if self.use_dropout:
                h = hidden['h' + str(idx)]
                hdrop, cache_hdrop = dropout_forward(h, self.dropout_param)
                hidden['hdrop' + str(idx)] = hdrop
                hidden['cache_hdrop' + str(idx)] = cache_hdrop

    scores = hidden['h' + str(self.L)]
    ############################################################################
    #                             END OF YOUR CODE                             #
    ############################################################################

    # If test mode return early
    if mode == 'test':
      return scores

    loss, grads = 0.0, {}
    ############################################################################
    # TODO: Implement the backward pass for the fully-connected net. Store the #
    # loss in the loss variable and gradients in the grads dictionary. Compute #
    # data loss using softmax, and make sure that grads[k] holds the gradients #
    # for self.params[k]. Don't forget to add L2 regularization!               #
    #                                                                          #
    # When using batch normalization, you don't need to regularize the scale   #
    # and shift parameters.                                                    #
    #                                                                          #
    # NOTE: To ensure that your implementation matches ours and you pass the   #
    # automated tests, make sure that your L2 regularization includes a factor #
    # of 0.5 to simplify the expression for the gradient.                      #
    ############################################################################
    # Computing of the loss
    data_loss, dscores = softmax_loss(scores, y)
    reg_loss = 0
    for w in [self.params[f] for f in self.params.keys() if f[0] == 'W']:
        reg_loss += 0.5 * self.reg * np.sum(w * w)

    loss = data_loss + reg_loss

    # Backward pass

    hidden['dh' + str(self.L)] = dscores
    for i in range(self.L)[::-1]:
        idx = i + 1
        dh = hidden['dh' + str(idx)]
        h_cache = hidden['cache_h' + str(idx)]
        if idx == self.L:
            dh, dw, db = affine_backward(dh, h_cache)
            hidden['dh' + str(idx - 1)] = dh
            hidden['dW' + str(idx)] = dw
            hidden['db' + str(idx)] = db

        else:
            if self.use_dropout:
                # First backprop in the dropout layer
                cache_hdrop = hidden['cache_hdrop' + str(idx)]
                dh = dropout_backward(dh, cache_hdrop)
            if self.use_batchnorm:
                dh, dw, db, dgamma, dbeta = affine_norm_relu_backward(dh, h_cache)
                hidden['dh' + str(idx - 1)] = dh
                hidden['dW' + str(idx)] = dw
                hidden['db' + str(idx)] = db
                hidden['dgamma' + str(idx)] = dgamma
                hidden['dbeta' + str(idx)] = dbeta
            else:
                dh, dw, db = affine_relu_backward(dh, h_cache)
                hidden['dh' + str(idx - 1)] = dh
                hidden['dW' + str(idx)] = dw
                hidden['db' + str(idx)] = db

    # w gradients where we add the regulariation term
    list_dw = {key[1:]: val + self.reg * self.params[key[1:]]
        for key, val in hidden.iteritems() if key[:2] == 'dW'}
    # Paramerters b
    list_db = {key[1:]: val for key, val in hidden.iteritems() if key[:2] =='db'}
    # Parameters gamma
    list_dgamma = {key[1:]: val for key, val in hidden.iteritems() if key[:6] == 'dgamma'}
    # Paramters beta
    list_dbeta = {key[1:]: val for key, val in hidden.iteritems() if key[:5] == 'dbeta'}

    grads = {}
    grads.update(list_dw)
    grads.update(list_db)
    grads.update(list_dgamma)
    grads.update(list_dbeta)
    ############################################################################
    #                             END OF YOUR CODE                             #
    ############################################################################

    return loss, grads

def affine_norm_relu_forward(x, w, b, gamma, beta, bn_param):
    """
    Convenience layer that perorms an affine transform followed by a ReLU

    Inputs:
    - x: Input to the affine layer
    - w, b: Weights for the affine layer
    - gamma, beta : Weight for the batch norm regularization
    - bn_params : Contain variable use to batch norml, running_mean and var

    Returns a tuple of:
    - out: Output from the ReLU
    - cache: Object to give to the backward pass
    """

    h, h_cache = affine_forward(x, w, b)
    hnorm, hnorm_cache = batchnorm_forward(h, gamma, beta, bn_param)
    hnormrelu, relu_cache = relu_forward(hnorm)
    cache = (h_cache, hnorm_cache, relu_cache)

    return hnormrelu, cache

def affine_norm_relu_backward(dout, cache):
    """
    Backward pass for the affine-relu convenience layer
    """
    h_cache, hnorm_cache, relu_cache = cache

    dhnormrelu = relu_backward(dout, relu_cache)
    dhnorm, dgamma, dbeta = batchnorm_backward_alt(dhnormrelu, hnorm_cache)
    dx, dw, db = affine_backward(dhnorm, h_cache)

    return dx, dw, db, dgamma, dbeta