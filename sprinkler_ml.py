import numpy as np
from sklearn.linear_model import LinearRegression


input = [[1,2], [2,3], [3,4]]
output = [3, 5, 7]

input, output = np.array(input), np.array(output)

model = LinearRegression().fit(input, output)

arr = np.array([[7,8]])

print(model.predict(arr))
