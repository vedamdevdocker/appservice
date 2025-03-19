from datetime import  timedelta
DEBUG = True
SECRET_KEY = "FLASKVEDSECKEY"
JWT_SECRET_KEY = "JWTVEDSECKEY"
JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
READ_ACCESS_TYPE = "read"  # You can change this value as needed
DELETE_ACCESS_TYPE = "delete"  # You can change this value as needed
WRITE_ACCESS_TYPE = "write"  # You can change this value as needed
UPDATE_ACCESS_TYPE = "update"  # You can change this value as needed
PROJECT_MAIN_MODULES_DIRECTORY_NAME = "modules"
APPLICATION_CREDENTIALS = [
    {"userid":"0","username": "kishore", "name":"SUPER USER0" , "password": "$2b$12$OjcDyH3BflTBHiiiQ1pVtOwWnxFju6j7EUBG8GWZKeKICVghjeI96","status":"Active","emailid":"kishore@test.com","empid":"0","start_date":"01/01/2000","expiry_date":"01/01/3000"},
    {"userid":"1","username": "admin", "name":"SUPER USER1" ,"password": "$2b$12$gnuMPXgfBzU4HqpUwFEVBu71oTAPPZfgnW0GCi50R0rsxeleIN042","status":"Active","emailid":"admin@test.com","empid":"0","start_date":"01/01/2000","expiry_date":"01/01/3000"},
   #{"userid":"100-MAX value","username": "admin", "name":"SUPER USER1" ,"password": "$2b$12$gnuMPXgfBzU4HqpUwFEVBu71oTAPPZfgnW0GCi50R0rsxeleIN042"}   
    # Add more username-password pairs as needed the userids must be below 100. This count should match with the SUPER_USERS_COUNT in application
]
BACKEND_ENVIRONMENT = 'Development'
ENABLE_DETAILED_LOGS = True
# Specify the log file path
#LOG_FILE_PATH = "modules/utilities/logs/"
LOG_FILE_PATH = "/app/Logs/"

#DB_INSTANCES_PATH = "C:\SAS Opera\Companies\Company_0\system\db_instances\instance1"
# config.py
DB_INSTANCES_BASE_PATH = '/app/configs/'
APP_SERVER_HOST = '192.168.1.182'
APP_SERVER_PORT = '54840'
APP_SERVER_PROTOCOL = 'https'

COMPANY_FOLDER = 'DEV'
SYSTEM_FOLDER = 'system'
CONFIG_FOLDER = 'config'
PROJECT_ROOT = 'application'
APPLICATION_ROOT = 'AppService'
PRODUCT_HOME = 'C:\SAS Opera\Companies'

BACKEND_APP_ROOT_PATH = '/app'


SSL_CRT_FILE = './certs/server.crt'
SSL_KEY_FILE = './certs/server.key'

CERT_ABS_PATH1 = "C:\\SAS Opera\\Companies\\Company_0\\system\\application\\AppService\\certs\\server.crt"
KEY_ABS_PATH1 = "C:\\SAS Opera\\Companies\\Company_0\\system\\application\\AppService\\certs\\server.key"
