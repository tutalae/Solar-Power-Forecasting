
from sklearn import metrics 
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression
import json
import os
import pathlib
import pickle as pkl
import tarfile
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
import datetime as dt

if __name__ == "__main__":   
    
    # All paths are local for the processing container
    model_path = "/opt/ml/processing/model/model.tar.gz"
    test_x_path = "/opt/ml/processing/test/test_x.csv"
    test_y_path = "/opt/ml/processing/test/test_y.csv"
    output_dir = "/opt/ml/processing/evaluation"
    output_prediction_path = "/opt/ml/processing/output/"
        
    # Read model tar file
    with tarfile.open(model_path, "r:gz") as t:
        t.extractall(path=".")
    
    # Load model
    model = xgb.Booster()
    model.load_model("xgboost-model")
    print("model loaded")
    
    # Read test data
    X_test = xgb.DMatrix(pd.read_csv(test_x_path, header=None).values)
    y_test = pd.read_csv(test_y_path, header=None).to_numpy()
    
    # Run predictions
    # test_features_numeric = X_test.drop(['DATE_TIME', 'SOURCE_KEY'], axis=1)
    predictions = model.predict(X_test)

    # Calculate RMSE
    # rmse = np.sqrt(mean_squared_error(y_test,predictions))
    rmse = np.sqrt(metrics.mean_squared_error(y_test, predictions))


    report_dict = {
        "regression_metrics": {
            "rmse": {
                "value": rmse,
       
            },
        },
    }

  # Save evaluation report
    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
    with open(f"{output_dir}/evaluation.json", "w") as f:
        f.write(json.dumps(report_dict))
    
    # Save prediction baseline file - we need it later for the model quality monitoring
    pd.DataFrame({"prediction":np.array(np.round(predictions), dtype=int),
                  "rmse":rmse,
                  "label":y_test.squeeze()}
                ).to_csv(os.path.join(output_prediction_path, 'prediction_baseline/prediction_baseline.csv'), index=False, header=True)
