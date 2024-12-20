import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM

# Load the dataset
file_path = 'TATAMOTORS.NS.csv'  # Update with the correct path
data = pd.read_csv(file_path)

# Convert the 'Date' column to datetime format with the correct format
data['Date'] = pd.to_datetime(data['Date'], format='%d-%m-%Y')
data.set_index('Date', inplace=True)

# Select the 'Close' price for prediction
close_prices = data['Close'].values.reshape(-1, 1)

# Normalize the data using MinMaxScaler
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(close_prices)

# Prepare the data for LSTM
def create_dataset(dataset, time_step=1):
    X, Y = [], []
    for i in range(len(dataset) - time_step - 1):
        a = dataset[i:(i + time_step), 0]
        X.append(a)
        Y.append(dataset[i + time_step, 0])
    return np.array(X), np.array(Y)

time_step = 60  # Use 60 days to predict the next day
X, Y = create_dataset(scaled_data, time_step)

# Reshape input to be [samples, time steps, features] which is required for LSTM
X = X.reshape(X.shape[0], X.shape[1], 1)

# Split the data into training and testing datasets
train_size = int(len(X) * 0.8)
X_train, X_test = X[:train_size], X[train_size:]
Y_train, Y_test = Y[:train_size], Y[train_size:]

# Build the LSTM model
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape=(time_step, 1)))
model.add(LSTM(50, return_sequences=False))
model.add(Dense(25))
model.add(Dense(1))

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
model.fit(X_train, Y_train, batch_size=1, epochs=10)

# Make predictions
train_predict = model.predict(X_train)
test_predict = model.predict(X_test)

# Inverse transform to get the actual prices
train_predict = scaler.inverse_transform(train_predict)
test_predict = scaler.inverse_transform(test_predict)

# Calculate RMSE and MAE for the training data
train_rmse = np.sqrt(mean_squared_error(scaler.inverse_transform(Y_train.reshape(-1, 1)), train_predict))
test_rmse = np.sqrt(mean_squared_error(scaler.inverse_transform(Y_test.reshape(-1, 1)), test_predict))

train_mae = mean_absolute_error(scaler.inverse_transform(Y_train.reshape(-1, 1)), train_predict)
test_mae = mean_absolute_error(scaler.inverse_transform(Y_test.reshape(-1, 1)), test_predict)

# Print the results
print(f'Training RMSE: {train_rmse}')
print(f'Test RMSE: {test_rmse}')
print(f'Training MAE: {train_mae}')
print(f'Test MAE: {test_mae}')

# Plot the results
plt.figure(figsize=(12, 6))

# Plot the actual prices
plt.plot(scaler.inverse_transform(scaled_data), label='Actual Price')

# Plot the train predictions
plt.plot(np.arange(time_step, len(train_predict) + time_step), train_predict, label='Train Predict')

# Plot the test predictions
plt.plot(np.arange(len(train_predict) + (time_step * 2), len(train_predict) + (time_step * 2) + len(test_predict)), test_predict, label='Test Predict')

plt.title('Tata Motors Stock Price Prediction with LSTM')
plt.xlabel('Date')
plt.ylabel('Close Price')
plt.legend()
plt.show()