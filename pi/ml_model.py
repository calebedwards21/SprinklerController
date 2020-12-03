import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split 
import matplotlib.pyplot as plt

class ML_Sprinkler:
    """
    This class represents a machine learning model for a sprinkling system
    based on future input data
    """

    def __init__(self, X, y):
        """
        Constructor for the ML Model
        """
        self.model = LinearRegression()
        self.X = X
        self.y = y


    def create_model(self):
        """
        Creates the model with future data
        y is size nx1
        X is size nxm
        """
        self.model = self.model.fit(self.X, self.y)


    def predict(self, X):
        """
        Predicts an output value based on input data X
        """
        return self.model.predict(X)


    def plot_model(self, X, y):
        """
        Plot the scatter plot of the model and input data
        """
        plt.scatter(X, y, color='k')
        plt.show()


    def test_model():
        """
        Tests the model with training and testing data
        """
        # Create model
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size = 0.2) 
        test_model = LinearRegression().fit(X_train, y_train)

        # Plot results
        y_pred = test_model.predict(X_test)
        plt.plot(X_test, y_pred, color='k')
        plt.show()


    def accuracy():
        """
        Returns the accuracy of the model
        """
        return self.model.score(self.X, self.y)