import pandas as pd

## this function takes the dataframe from 'fetchKeywords.py' as an input
def apiToDataFrame(api_dataframe):
    # The analyzeDataFrame function now handles DataFrame input directly
    # So we just return the DataFrame as-is
    if isinstance(api_dataframe, pd.DataFrame) and not api_dataframe.empty:
        return api_dataframe
    elif isinstance(api_dataframe, list) and len(api_dataframe) > 0:
        return pd.DataFrame(api_dataframe)
    else:
        return None