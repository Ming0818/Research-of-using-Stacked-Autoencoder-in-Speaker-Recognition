import pdb
import os
import sys
import scipy.io.wavfile as wavfile
import theano
import theano.tensor as T
import numpy
from theano.tensor.shared_randomstreams import RandomStreams
from autoencoder.dA import dA

class mSdA(object):
		#Stacked denoising auto-encoder class (SdA)
    def __init__(
        self,
        layers = [39, 100, 100, 200],
        dAs = []
    ):
    		self.layers = layers
    		self.dAs = dAs
    				
    def train( self, train_set, batch_size = 100 ):
    		for i in xrange(len(self.layers) - 1):
    				train_data = T.dmatrix('train_data')
    				x = T.dmatrix('x')
    				rng = numpy.random.RandomState(123)
    				theano_rng = RandomStreams(rng.randint(2 ** 10))
    				da = dA(
        				numpy_rng=rng,
        				theano_rng=theano_rng,
        				input=x,
        				n_visible=self.layers[i],
        				n_hidden=self.layers[i+1]
    				)
    				cost, updates = da.get_cost_updates(
        				corruption_level=0.,
        				learning_rate=0.4
    				)
    				train_da = theano.function(
    						[train_data],
        				cost,
        				updates=updates,
        				givens={
            				x: train_data
        				}
        		)
        		
    				for epoch in xrange(20):
    						train_cost = []
    						for index in xrange(len(train_set)/batch_size):
    								train_cost.append(train_da(numpy.asarray(train_set[index * batch_size: (index + 1) * batch_size])))
    						print 'Training 1st ae epoch %d, cost ' % epoch, numpy.mean(train_cost)
    				train_set = da.get_hidden_values(train_set).eval()
    				self.dAs.append(da)
    
    def get_hidden_values(self, features):
    		for i in xrange(len(self.layers) - 1):
    				da = self.dAs[i]
    				features = da.get_hidden_values(features).eval()
    		return features
