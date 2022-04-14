# Machine Learning API with Django

This is my own work following the "Deploy Machine Learning Models with Django" tutorial by [Piotr Płoński](https://github.com/pplonski) at deploymachinelearning.com.

The original tutorial briefly covers a large number of topics and has a few issues, so this version improves upon the original in a number of ways.

## Improvements from the Tutorial

1. Newer versions of various software packages are used over the ones that were available in 2019 when the original tutorial was written. Namely, Django 4.0.3 is used instead of the specified 2.2.4 from the tutorial. See `requirements.txt` for other software versions.
2. This project does not create a `backend` directory for the `server` Django project as it appears in the tutorial that the `backend` directory contains nothing other than the Django project itself.
3.  The Django apps `endpoints` and `ml` exist at the top of the `server` Django directory instead of creating a new `app` directory just to hold Django apps.

## Data Training

4. The data training notebook `Data Training.ipynb` uses an `OrdinalEncoder` to encode categorical data instead of the `LabelEncoder` used in the tutorial. The [sklearn docs](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.LabelEncoder.html) for `LabelEncoder` explains why: 
    > This transformer should be used to encode target values, *i.e.* `y`, and not the input `X`.
5. The data training notebook `Data Training.ipynb` trains the `OrdinalEncoder` on the full set of inputs `X` instead of only using `X_train` as in the tutorial. This solves the issue that occurs when `X_test` contains unique values that are not also found in `X_train`. So the encoder must be trained on the full set of possible values for all input features.
6.  The data training notebook `Data Training.ipynb` takes one additional step after training the algorithms to evaluate their accuracy with `sklearn.metrics.confusion_matrix`.

## Models

7.  A number of `CharField` attributes in `endpoints/models.py` were changed to `TextField` which is more appropriate for strings of significant length, and `max_length` parameters were removed from `MLAlgoithm.description` and `MLAlgorithm.code`.
8.  `__str__` methods were written in various model classes to improve readability on the Django site admin.
9.  A `Meta` class was added to a number of models to improve readability in the generated pages.
10. Docstrings were added in various places to improve understanding.

## ML Objects

11. Replaced hardcoding of relative paths with `pathlib.Path` in places such as `ml.income_classifier.random_forest`.
12. Replaced hardcoding of categorical features in `ml.income_classifier` with `OrdinalEncoder.feature_names_in_` to allow for more dynamic processing.
13. Instead of using a `RandomForestClassifier` from `ml.income_classifier` and creating a new class for each new type of classifier algorithm, a general `IncomeClassifier` class was created to hold algorithm data for different income classier models.
14. The `MLRegistry.endpoints` property was changed to `MLRegistry.__endpoint_algorithms` to prevent unintended changes. 
15. A `get_algorithm` method was added to the `MLRegistry` which finds and returns algorithm objects from the registry. This method is then used in the `PredictView` to make requested predictions.
16. A `__str__` method was added to the `MLRegistry` class which returns a string representation of the endpoint algorithms dictionary. This method is used to test the absence (len == 2) or presence (len > 2) of algorithms in the registry.