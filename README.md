# Extracting Time Series Properties of Glucose Levels in Artificial Pancreas

In this project, several performance metrics of an Artificial Pancreas system are extracted from sensor data. 

## About the repo:
* main.py contains all the code parts for extracting the time series properties.
* You can also refer to the jupyter notebook in the repo (which has the same content).

## Datasets:
* Continuous Glucose Sensor data (CGMData.csv)
* Insulin pump data (InsulinData.csv)


## Metrics extracted:
* Percentage time in hyperglycemia (CGM > 180 mg/dL),
* Percentage of time in hyperglycemia critical (CGM > 250 mg/dL),
* Percentage time in range (CGM >= 70 mg/dL and CGM <= 180 mg/dL),
* Percentage time in range secondary (CGM >= 70 mg/dL and CGM <= 150 mg/dL),
* Percentage time in hypoglycemia level 1 (CGM < 70 mg/dL), and
* Percentage time in hypoglycemia level 2 (CGM < 54 mg/dL).

Each of the above metrics is extracted in three different time intervals: daytime (6 am to midnight), overnight (midnight to 6 am) and whole day (12 am to 12 am).
