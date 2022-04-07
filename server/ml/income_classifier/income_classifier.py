import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from rest_framework.exceptions import APIException

class IncomeClassifier:
    '''
    A wrapper for an income classifer model stored in the `training` folder.

    Attributes:
        values_fill_missing: a dictionary of mode values used to fill missing values in the input data
        encoder: the encoder used to convert categorical data to numerical data in the input data
        model: the trained income classifier model
    '''
    
    def __init__(self, saved_model):
        """Loads artifacts from the training folder for a given model.

        Args:
            saved_model (string): The name of a joblib file containing the model to load.
        """
        project_dir = Path(__file__).resolve().parent.parent.parent.parent
        path_to_artifacts = Path(project_dir, "training")
        self.values_fill_missing =  joblib.load(Path(path_to_artifacts, "train_mode.joblib"))
        self.encoder = joblib.load(Path(path_to_artifacts, "encoder.joblib"))
        self.model = joblib.load(Path(path_to_artifacts, saved_model))

    def preprocessing(self, input_data):
        '''
        Preprocess the input data so it can be used with the model.
        This method fills missing values and encodes categorical data using the same
        objects that were used to preprocess the model's training data.

        Args:
            input_data: original data to be used as the basis for a prediction

        Raises:
            APIException: when multiple samples are given for prediction

        Returns:
            input_data: the original data after it has been processed to comply with the model
        '''
        # JSON to pandas DataFrame
        input_data = pd.DataFrame(input_data, index=[0])
        if input_data.shape[0] > 1:
            raise APIException("Multiple samples provided to single sample prediction method")
        # fill missing values
        input_data.fillna(self.values_fill_missing)
        # convert categoricals
        categoricals = self.encoder.feature_names_in_
        input_data_encoded = self.encoder.transform(input_data[categoricals])
        input_data_encoded = pd.DataFrame(data=input_data_encoded, columns=categoricals)
        for category in categoricals:
            input_data[category] = input_data_encoded[category].values

        return input_data

    def predict(self, input_data):
        '''
        Use the loaded model to predict probabilities for income classes from the given data.

        Args:
            input_data: the preprocessed data to used in making the prediction

        Returns:
            predict_proba: a probability matrix that the income is greater than 50K.
        '''
        return self.model.predict_proba(input_data)

    def postprocessing(self, input_data):
        '''
        Wrap the predicted probability and its respective label in a JSON response with OK status.

        Args:
            input_data: the probability matrix returned from the model's prediction method

        Returns:
            response: JSON object containing probability, label, and OK status
        '''
        label = "<=50K"
        if input_data[1] > 0.5:
            label = ">50K"
        return {"probability": input_data[1], "label": label, "status": "OK"}

    def compute_prediction(self, input_data):
        '''
        The endpoint function that combines preprocessing, prediction, and postprocessing
        to generate a response.

        Args:
            input_data: the original sample data to be used in the prediction

        Returns:
            prediction: a JSON object containing prediction probability, label, and OK status
        '''
        try:
            input_data = self.preprocessing(input_data)
            prediction = self.predict(input_data)[0]  # only one sample
            prediction = self.postprocessing(prediction)
        except Exception as e:
            return {"status": "Error", "message": str(e)}

        return prediction
