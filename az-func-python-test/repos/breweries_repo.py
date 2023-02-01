import pandas as pd

# Returns all data from breweries table
def get_all_breweries_data(cnn, close_cnn):
  # Query to search
  query = "SELECT * FROM dbo.breweries"
  
  # execute query against breweries list
  df = pd.read_sql(query, cnn)

  # close connection if necessary
  if close_cnn == True:
    cnn.close()

  # return result of query executings, formatted as json
  return df.to_json(orient='records')