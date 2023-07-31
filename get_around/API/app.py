import uvicorn
import pandas as pd 
from pydantic import BaseModel
from fastapi import FastAPI
import numpy as np
import joblib
from typing import List
import json
from xmlrpc.client import Boolean

description = """"
Welcome to the Getaround API,

This allows you to predict the ideal price for your car rental. This prediction is based on your car's characteristics: model, mileage, fuel type, etc. 

Here are the endpoints of this API : 

## Features

* `/features` in this part you will find all the values possible for your features, to help you make the best prediction

## Prediction

* `/predict` fill it with your cars informations and the model will give you the ideal price for your rental. The prediction corresponds to the price per rental day

Check out documentation for more information.
"""

# tags
tags_metadata = [

    {
        "name": "Features",
        "description": "Endpoint that gives the list of the possible values to enter for each features in order to get a rental price prediction"
    },

    {
        "name": "Prediction",
        "description": "Endpoint of prediction of the rental price for your car, based on a random forest model"
    }
    
]


# API object
app = FastAPI(title="GETAROUND API",
    description=description,
    version="1.0",
    openapi_tags=tags_metadata)


# Define features
class PredictionFeatures(BaseModel):
    model_key: str
    mileage: int
    engine_power: int
    fuel: str
    paint_color: str
    car_type: str
    private_parking_available: bool
    has_gps: bool
    has_air_conditioning: bool
    automatic_car: bool
    has_getaround_connect: bool
    has_speed_regulator: bool
    winter_tires: bool

# see the different feature

@app.get("/features", tags=["Features"])
async def features(feature):
    df = pd.read_csv('get_around_pricing_project.csv')

    columns = [*df.loc[:,feature].value_counts().index]
    return columns


# prediciton with model random forest

@app.post("/predict", tags=["Prediction"])
async def predict(predictionFeatures: PredictionFeatures):
    # Preprocessing
    encoder = joblib.load('encoder.joblib')

    # Read data 
    df = pd.DataFrame(dict(predictionFeatures), index=[0])

    # apply preprocessing
    df_encoded = encoder.transform(df)

    # Load the models from local
    model_rf  = 'model_rf.joblib'
    regressor_rf = joblib.load(model_rf)
    prediction = regressor_rf.predict(df_encoded)

    # Format response
    response = {"prediction": prediction.tolist()[0]}
    return response



if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000, debug=True, reload=True)