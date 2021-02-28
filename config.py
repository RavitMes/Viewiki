import os

# app parameters
SECRET_KEY = os.urandom(32)
DEBUG = False
HOST = "127.0.0.1"


# db parameters
DB_NAME = 'db_name'
DB_HOST= 'insert_the_db_host'
DB_USER='insert_the_db_user'
DB_PASSWD='insert_the_db_password'

# Path to logger configuration file
LOG_CONF = 'logging.conf'

# other variables
PROJECT_NAME = ""
GREETS = ["Hope you'll have a wonderful day today and it's not sunday ;)",
                  "Don't forget to smile today!",
                  "Here is a suggestion for a nice song for you today: Roo Panes Lullaby love ",
                  "Here is a suggestion for a nice song for you today (in hebrew): מוש בן ארי - "
                  "משא ומתן ",
                  "Here is a suggestion for a nice song for you today: ג'יין בורדו - Colors of "
                  "the Wind ",
                  "Here is a suggestion for a nice song for you today: FORESTT - To The Sea ("
                  "would you believe it's an Israeli band?)",
                  "Here is a suggestion for a nice song for you today: Neil Young - Heart Of Gold"
                  ]

TABLES = [
    {"USERS":
         {"USER_ID": {"TYPE": "INT", "PRIMARY KEY": True, "AUTO_INCREMENT": True,
                      "NOT NULL": False,"UNIQUE": False},
          "NAME": {"TYPE": "VARCHAR(255)", "PRIMARY KEY": False, "AUTO_INCREMENT": False,
                   "NOT NULL": True, "UNIQUE": False},
          "EMAIL": {"TYPE": "VARCHAR(255)", "PRIMARY KEY": False,
                    "AUTO_INCREMENT": False, "NOT NULL": True, "UNIQUE": True},
          "PASSWORD": {"TYPE": "VARCHAR(255)", "PRIMARY KEY": False,
                       "AUTO_INCREMENT": False, "NOT NULL": True, "UNIQUE": False}}},

    {"PROJECTS":
         {"PROJECT_ID": {"TYPE": "INT", "PRIMARY KEY": True, "AUTO_INCREMENT": True,
                         "NOT NULL": False, "UNIQUE": False},
          "NAME": {"TYPE": "VARCHAR(255)", "PRIMARY KEY": False, "AUTO_INCREMENT": False,
                   "NOT NULL": True, "UNIQUE": True}}},

    {"WIKI_DATA": {
        "PROJECT_ID": {"TYPE": "INT", "PRIMARY KEY": False,"AUTO_INCREMENT": False,
                       "NOT NULL": True, "UNIQUE": False},
        "CATEGORY": {"TYPE": "VARCHAR(255)", "PRIMARY KEY": False, "AUTO_INCREMENT": False,
                     "NOT NULL": True, "UNIQUE": False},
        "WIKI_PAGE_URL": {"TYPE": "VARCHAR(255)", "PRIMARY KEY": False, "AUTO_INCREMENT": False,
                          "NOT NULL": True, "UNIQUE": False},
        "PAGE_INTERLINK": {"TYPE": "VARCHAR(255)", "PRIMARY KEY": False, "AUTO_INCREMENT": False,
                           "NOT NULL": False, "UNIQUE": False},
        "ADD": "CONSTRAINT pk PRIMARY KEY (PROJECT_ID, CATEGORY, WIKI_PAGE_URL, PAGE_INTERLINK)",
        "FOREIGN_KEY": {"col_from":["PROJECT_ID"], "table":["PROJECTS"], "col_to":["PROJECT_ID"]}}},

    {"LOG": {
     "DATE": {"TYPE": "VARCHAR(255)", "PRIMARY KEY": False, "AUTO_INCREMENT": False,
              "NOT NULL": True, "UNIQUE": False},
     "PROJECT_ID": {"TYPE": "INT", "PRIMARY KEY": False, "AUTO_INCREMENT": False,
                    "NOT NULL": True, "UNIQUE": False},
     "USER_ID": {"TYPE": "INT", "PRIMARY KEY": False,
                 "AUTO_INCREMENT": False,
                 "NOT NULL": True, "UNIQUE": False},
     "ACTION": {"TYPE": "VARCHAR(255)", "PRIMARY KEY": False,
                "AUTO_INCREMENT": False,
                "NOT NULL": True, "UNIQUE": False},
     "FOREIGN_KEY": {"col_from":["PROJECT_ID","USER_ID"], "table":["PROJECTS","USERS"], "col_to":["PROJECT_ID","USER_ID"]}}},

    {"USERS_PROJECTS": {
        "USER_ID": {"TYPE": "INT", "PRIMARY KEY": False, "AUTO_INCREMENT": False, "NOT NULL": True,
                    "UNIQUE": False},
        "PROJECT_ID": {"TYPE": "INT", "PRIMARY KEY": False, "AUTO_INCREMENT": False,
                       "NOT NULL": True, "UNIQUE": False},
        "ADD": "CONSTRAINT pk PRIMARY KEY (USER_ID, PROJECT_ID)",
        "FOREIGN_KEY": {"col_from":["PROJECT_ID","USER_ID"], "table":["PROJECTS","USERS"], "col_to":["PROJECT_ID","USER_ID"]}}}
]