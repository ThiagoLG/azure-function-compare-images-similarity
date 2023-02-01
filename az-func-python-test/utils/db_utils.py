import pyodbc as pyo


def get_connection():
    strings_connection = ("Driver={SQL Server};"
                          "Server=thiago-ghebra.database.windows.net,1433;"
                          "Database=db_beer_catalog;"
                          "Uid=db_beer_master;"
                          "Pwd=@9$raW4dn3&c;"
                          "Encrypt=yes;"
                          "TrustServerCertificate=no;"
                          "Connection Timeout=30;")

    return pyo.connect(strings_connection)
