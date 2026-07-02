import sqlite3

def init_db():
    conn=sqlite3.connect("historique.db")
    
    conn.execute("""
                 CREATE TABLE IF NOT EXISTS devis(
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     type_site TEXT,
                     nb_pages INTEGER,
                     prix_estime REAL,
                     date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                 )
                 
                """)
    conn.commit()
    conn.close()

def save_devis(type_site:str,nb_pages:int,prix:float):
    conn=sqlite3.connect("historique.db")
    conn.execute(
        "INSERT INTO devis (type_site,nb_pages,prix_estime) VALUES (?,?,?)",
        (type_site,nb_pages,prix)
    )
    conn.commit()
    conn.close()
    
    