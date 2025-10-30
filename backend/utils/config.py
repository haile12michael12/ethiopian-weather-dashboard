import os

class Config:
    @staticmethod
    def get_database_path():
        """Get the database path"""
        home_directory = os.path.expanduser('~')
        forcast_FOLDER = os.path.join(home_directory, "airflow", "harvestedfiles")
        return os.path.join(forcast_FOLDER, "NMA_Threedays_forcast_DataBase.db")
    
    @staticmethod
    def create_database_directory():
        """Create the database directory if it doesn't exist"""
        home_directory = os.path.expanduser('~')
        forcast_FOLDER = os.path.join(home_directory, "airflow", "harvestedfiles")
        os.makedirs(forcast_FOLDER, exist_ok=True)
        return forcast_FOLDER