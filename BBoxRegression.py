import numpy as np
import tensorflow as tf

class BBoxRegression:
    def __init__(self, npy_model, trainable):
        self.npy_model = npy_model
        self.var_dict = {}
        self.trainable = trainable

    def build(self, feature_holder, box_holder):
        self.weights, self.bbox1 = self.bbox_layer(feature_holder, 4096, 4, 'bbox1')

        self.regression_loss = tf.square(box_holder - self.bbox1)
        self.regression_loss_mean = tf.reduce_mean(self.regression_loss)
        self.regularization = 1000 * tf.reduce_sum(tf.square(self.weights), 0)
        self.loss = self.regularization + self.regression_loss_mean
        self.optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.1).minimize(self.loss)

        self.npy_model = None

    def get_var(self, initial_value, name, idx, var_name):
        if self.npy_model is not None and name in self.npy_model:
            value = self.npy_model[name][idx]
        else:
            value = initial_value

        var = tf.Variable(value, name=var_name)

        self.var_dict[(name, idx)] = var

        return var

    def get_bbox_var(self, in_size, out_size, name):
        initial_value = tf.truncated_normal([in_size, out_size], 0.0, 0.001)
        weights = self.get_var(initial_value, name, 0, name + '_weights')

        initial_value = tf.truncated_normal([out_size], 0.0, 0.001)
        biases = self.get_var(initial_value, name, 1, name + '_biases')

        return weights, biases

    def bbox_layer(self, bottom, in_size, out_size, name):
        with tf.variable_scope(name):
            weights, biases = self.get_bbox_var(in_size, out_size, name)

            x = tf.reshape(bottom, [-1, in_size])
            bbox = tf.nn.bias_add(tf.matmul(x, weights), biases)

            return weights, bbox

    def get_var_count(self):
        count = 0
        for var in list(self.var_dict.values()):
            count += np.multiply(var.get_shape().as_list())
        return count
