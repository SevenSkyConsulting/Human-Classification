import json

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_squared_error

# Example input data for multiple users
with open('p_data.json', mode='r') as data, open('p_target.json', mode='r') as target:
    data = json.load(data)
    targets = json.load(target)

data_types = {"E_commerce": ['Expensive', 'Normal', 'Cheap'],
              "News": ['Sport', 'Travel', 'Politic'],
              "Education": ['Business', 'Psychology', 'Computer'],
              "Music": ['Rock', 'Pop', 'Hip_hop']
              }


# Flattening function to convert nested dictionary to flat format
def flatten_input_data(train_data):
    flat_data = []
    data_keys = list(data_types.keys())
    data_values = list(data_types.values())
    for person in train_data:
        person_data = {}
        for idx, sub in enumerate(person):
            person_data[f'{data_keys[idx]}_{data_values[idx][0]}'] = sub[0]
            person_data[f'{data_keys[idx]}_{data_values[idx][1]}'] = sub[1]
            person_data[f'{data_keys[idx]}_{data_values[idx][2]}'] = sub[2]

        flat_data.append(person_data)
    return flat_data


def classifier(f_targets: []):

    for target in targets:
        f_targets.append({"Horror": target[0], "Action": target[1], "Drama": target[2]})

    # Flattening input and output
    X = flatten_input_data(data)
    y = pd.DataFrame(f_targets)

    # Convert to DataFrame
    X = pd.DataFrame(X)

    # Splitting data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Random Forest Regressor for multi-output regression
    model = MultiOutputRegressor(RandomForestRegressor())

    # Training the model
    model.fit(X_train, y_train)

    # Making predictions
    y_pred = model.predict(X_test)

    # Evaluating the model
    mse = mean_squared_error(y_test, y_pred, multioutput='raw_values')
    print("Mean Squared Error for each output category:", mse)
