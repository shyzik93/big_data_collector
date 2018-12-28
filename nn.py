# https://github.com/dataPAPA/tensorflow_mnist/blob/master/mnist.py
# https://rdipietro.github.io/friendly-intro-to-cross-entropy-loss/
# https://www.youtube.com/watch?v=R_Lmewg8W64&index=2&list=PLc7l3EqB0uxJLNSSQWEDjxXwO3iB8l5Wi

import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

# Загружаем MNIST датасет - числа, написанные от руки
mnist = input_data.read_data_sets("MNIST_data", one_hot=True)

x = tf.placeholder("float", [None, 784])
y = tf.placeholder("float", [None, 10])

W = tf.Variable(tf.zeros([784, 10]))
b = tf.Variable(tf.zeros([10]))

linear_prediction = tf.matmul(x, W) + b
scaled_prediction = tf.nn.softmax(linear_prediction)

loss_function = tf.losses.softmax_cross_entropy(y, linear_prediction)
learning_rate = 0.01
optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(loss_function)

# инициализация переменных и сессии

init = tf.global_variables_initializer()
sess = tf.InteractiveSession()
sess.run(init)

# запуск оптимизация

batch_size = 100

for iteration in range(200000):
    batch_x, batch_y = mnist.train.next_batch(batch_size)
    sess.run(optimizer, feed_dict={x: batch_x, y: batch_y})
    
    # вывод ошибки
    if iteration % 5000 == 0:
        loss = loss_function.eval({x:mnist.test.images, y:mnist.test.labels})
        print("#{}, loss={:.4f}".format(iteration, loss))
        
# Задаем граф вычислений, выдающий точность предсказания
predicted_label = tf.argmax(scaled_prediction, 1)
actual_label = tf.argmax(y, 1)
is_equal_labels = tf.equal(actual_label, predicted_label)
accuracy = tf.reduce_mean(tf.cast(is_equal_labels, "float"))

# Вычисляем точность
accracy_value = accuracy.eval({x: mnist.test.images, y: mnist.test.labels})
print ("Accuracy:", accracy_value)

# Предсказываем лейбы для тествого датасета
predicted_label = tf.argmax(scaled_prediction, 1)
predicted_test_values = predicted_label.eval(
    {x: mnist.test.images})
print ("Predictions: {}".format(predicted_test_values))