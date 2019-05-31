import mysql.connector
import random
import keys

def AddToDatabase(user_id, oauth_token, oauth_secret):
    try:
        cnx = mysql.connector.connect(user=keys.kDATABASE_USER, password=keys.kDATABASE_PASSWORD,
                                host=keys.kDATABASE_HOST,
                                database=keys.kDATABASE_DATABASE)
                                
        delete_entry = ("DELETE FROM `tokens` WHERE `user_id` = '%s'" % user_id)
        cursor = cnx.cursor()
        cursor.execute(delete_entry)
        
        cursor = cnx.cursor()        
        while True:
            try:
                token_id = random.randint(0, (1<<32) - 1)
                add_entry = ("INSERT INTO `tokens` "
                            "(`token_id`, `oauth_token`, `oauth_token_secret`, `user_id`) "
                            "VALUES ('" + str(token_id) + "', '" + oauth_token + "', '" + oauth_secret + "', '" + user_id + "')")
                cursor.execute(add_entry)
                return token_id
            except mysql.connector.errors.IntegrityError as e:
                if e.errno != mysql.connector.errorcode.ER_DUP_ENTRY:
                    raise
    finally:
        cursor.close()
        cnx.close()  

def GetOAuthTokenAndSecret(user_id, token_id):
    try:
        cnx = mysql.connector.connect(user=keys.kDATABASE_USER, password=keys.kDATABASE_PASSWORD,
                                host=keys.kDATABASE_HOST,
                                database=keys.kDATABASE_DATABASE)
        cursor = cnx.cursor()
        select_entry = "SELECT `oauth_token`, `oauth_token_secret` FROM `tokens` WHERE `token_id` = '%s' AND `user_id` = '%s'" % ( token_id, user_id )
        cursor.execute(select_entry)
        
        for oauth_token, oauth_token_secret in cursor:
            return oauth_token, oauth_token_secret
    finally:
        cursor.close()
        cnx.close()

    return None, None
