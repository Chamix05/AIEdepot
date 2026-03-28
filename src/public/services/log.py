from db_connection import get_connection


def extract_log():
    db = get_connection()  # ta fonction qui ouvre la connexion
    cursor = db.cursor()
    cursor.execute("""
        SELECT e.sujet,e.loginU,c.resultat
        FROM email e
        JOIN classe c ON e.idc = c.idc
       
    """)
    logs = cursor.fetchall()
    db.commit()
    cursor.close()
    db.close()
    return logs