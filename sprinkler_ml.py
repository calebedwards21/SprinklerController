import numpy as np
from sklearn.linear_model import LinearRegression

class ML_Sprinkler:
	"""
	This class represents a machine learning model for a sprinkling system
	based on false data
	"""

	def __init__(self):
		"""
		Constructor for the ML Model
		"""
		self._model = LinearRegression()


	def create_model(self):
		"""
		Creates the model with false data
		"""
		input = []
		output = []
		for temp in range(40, 110, 5): # Temp is in Farenheit
			for humidity in range(0, 100, 5): # Humidity is in %
				for moisture in range(250, 500, 25): # 250 is no moisture - low to high
					input_val = [temp, humidity, moisture, light]
					input.append(input_val)

					output_val = 0	# Create a false output value for the input data points
					if moisture > 400:
						output_val = 0
					else:
						output_val = 10 * (temp * 0.01) + 5 * (humidity * 0.01) + 15 * (moisture / 250)**(-1)  # Need to fix this
					output.append(output_val)

		input, output = np.array(input), np.array(output)
		self._model = self._model.fit(input, output)


	def predict(self, moisture, temp, humidity):
		"""
		Predicts an output value based on data from the false model
		"""
		arr = np.array([[moisture, temp, light, humidity]])
		return self._model.predict(arr)


