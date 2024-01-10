from fastapi import FastAPI, HTTPException
import uvicorn
import sqlite3
from enum import Enum


app = FastAPI()

con = sqlite3.connect('Chinook.db')

def execute_sql_query(con, query):
    cur = con.cursor()
    cur.execute(query)
    result = cur.fetchall()
    print(query)
    print(result)
    if result is None or len(result) == 0:
        raise HTTPException(status_code=400, detail='Aucune valeur')
    if len(result) == 1:
        return result[0]
    else:
        return result


def validate_year(year: str):
    if not year.isdigit() or not (len(year) == 4) :
        raise HTTPException(status_code=400, detail="L'année doit être une valeur numérique de 4 chiffres")
    return year
    
def city_exists(con, city, table):
    query = f"SELECT COUNT(*) FROM {table} WHERE UPPER(ville) LIKE '{city.upper()}%'"
    result = execute_sql_query(con, query)
    return result[0] > 0

def is_number(nb_piece):
    if not isinstance(nb_piece, int):
        raise HTTPException(detail="La valeur doit être un chiffre")
    return nb_piece


class Type(Enum):
    MAISON = "Maison"
    APPARTEMENT = "Appartement"



#1 En tant qu'Agent je veux pouvoir consulter le revenu fiscal moyen des foyers de ma ville (Montpellier)
@app.get("/revenu_fiscal/", description="Retourne le revenu fiscal moyen des  foyers de ma ville")
async def revenu_fiscal_moyen(city: str):
    if not city_exists(con, city, 'foyers_fiscaux'):
        raise HTTPException(status_code=400, detail="La ville n'est pas correcte ou n'existe pas")
    query = f"SELECT AVG(revenu_fiscal_moyen) FROM foyers_fiscaux WHERE UPPER(ville) LIKE '{city.upper()}%'"
    return execute_sql_query(con, query)


#2 En tant qu'Agent je veux consulter les 10 dernières transactions dans ma ville (HENDAYE)
@app.get("/transaction/", description="Permet de consulter les dernières x transactions de ma ville (x étant définit par limit)")
async def transaction_city(limit:int, city: str):
    if not city_exists(con, city, 'transactions_sample'):
        raise HTTPException(status_code=400, detail="La ville n'est pas correcte ou n'existe pas")
    query = f"SELECT * FROM transactions_sample WHERE UPPER(ville) LIKE UPPER('{city}%') ORDER BY date_transaction DESC LIMIT '{limit}';"
    return execute_sql_query(con, query)

# year = validate_year(year)

#3 En tant qu'Agent je souhaite connaitre le nombre d'acquisitions dans ma ville (Paris) durant l'année 2022

@app.get("/acquisition/", description="Permet de connaitre le nombre d'acquisition de ma ville par année")
async def acquisition(year:str, city: str):
    if not city_exists(con, city, 'transactions_sample'):
        raise HTTPException(status_code=400, detail="La valeur n'est pas correcte ou n'existe pas")
    year = validate_year(year)
    query = f"SELECT COUNT(*) FROM transactions_sample WHERE UPPER(ville) LIKE UPPER('{city}%') AND date_transaction LIKE '{year}%';"
    return execute_sql_query(con, query)


#4 En tant qu'Agent je souhaite connaitre le prix au m2 moyen pour les maisons vendues l'année 2022
@app.get("/prix_m2/", description="Permet de connaitre le prix par m² par type de logement et par année")
async def prix_m2(year:str, type:Type):
    query= f"SELECT AVG(prix/surface_habitable) FROM transactions_sample WHERE UPPER(type_batiment) LIKE UPPER('{type.value}') AND date_transaction LIKE '{year}%';"
    return execute_sql_query(con, query)

#5 En tant qu'Agent je souhaite connaitre le nombre d'acquisitions de studios dans ma ville (Rennes) durant l'année 2022
@app.get("/nb_acquisition/", description="Permet de connaitre le nombre d'acquisition en fonction du nombre de pièces, par logement et par année")
async def nb_acquisition(year:str, nb_piece:int, type: Type, city:str):
    if not city_exists(con, city, 'transactions_sample'):
        raise HTTPException(status_code=400, detail="La valeur n'est pas correcte ou n'existe pas")
    year = validate_year(year)
    nb_piece = is_number(nb_piece)
    query= f"SELECT count(*)FROM transactions_sample WHERE type_batiment = '{type.value}' And n_pieces ='{nb_piece}' AND date_transaction LIKE '{year}%' AND UPPER(ville) = UPPER('{city}')"
    return execute_sql_query(con, query)

#7 En tant qu'Agent je souhaite connaitre le prix au m2 moyen pour les maisons vendues à Messimy l'année 2022 
@app.get("/prix_m2_maison/", description="Permet de connaitre le prix par m² par type de logement, par ville et par année ")
async def prix_m2_maison(year:str, type: Type, city: str):
    if not city_exists(con, city, 'transactions_sample'):
        raise HTTPException(status_code=400, detail="La ville n'est pas correcte ou n'existe pas")
    year = validate_year(year)
    query= f"SELECT ville, AVG(prix/surface_habitable) FROM transactions_sample WHERE UPPER(type_batiment) = UPPER('{type.value}') AND ville LIKE '{city}' AND date_transaction LIKE '{year}%';"
    return execute_sql_query(con, query)

#8 En tant que CEO, je veux consulter le nombre de transactions (tout type confondu) par département, ordonnées par ordre décroissant
@app.get("/nb_transaction_departement/", description="Permet de consulter le nombre de transaction, tout type de logement, par departement par ordre décroissant")
async def nb_transaction_departement():
    query= f"SELECT departement , count(*) FROM transactions_sample GROUP BY departement ORDER BY departement DESC"
    return execute_sql_query(con, query)

#9 En tant que CEO je souhaite connaitre le nombre total de vente d'appartements en 2022 dans toutes les villes où le revenu fiscal moyen en 2018 est supérieur à 10k
@app.get("/nb_vente_appartement_plafond-ff/", description="Permet de connaitre le nombre total de logement vendu en fonction de l'année de transaction, de la ville, de l'année fiscale et du revenu fiscal")
async def nb_vente_appartement_plafond(year_ts:str, year_ff: str, plafond:int):
    year_ff = validate_year(year_ff)
    year_ts = validate_year(year_ts)
    plafond = is_number(plafond)
    query= f"SELECT ts.ville, count(*) FROM transactions_sample ts LEFT JOIN foyers_fiscaux ff ON ts.ville = UPPER(ff.ville) WHERE ff.revenu_fiscal_moyen > '{plafond}' AND ff.date ='{year_ff}' AND ts.date_transaction LIKE '{year_ts}%' GROUP BY ts.ville;"
    return execute_sql_query(con, query)

#10 En tant que CEO, je veux consulter le top 10 des villes les plus dynamiques en termes de transactions immobilières
@app.get("/top_ville_dynamique/", description="Permet de consulter le top X des villes les plus dynamiques")
async def top_ville_dynamique(limit:int):
    limit = is_number(limit)
    query= f"SELECT ville,* FROM transactions_sample GROUP BY ville ORDER BY prix DESC LIMIT '{limit}';"
    return execute_sql_query(con, query)

#11 En tant que CEO, je veux accéder aux 10 villes avec un prix au m2 moyen le plus bas pour les appartements
@app.get("/top_ville_prix_m2_bas/", description="Permet de connaitre le top X des villes avec la moyenne du prix du m le plus bas en fonction du logement")
async def top_ville_prix_m2_bas(limit:int, type: Type):
    limit = is_number(limit)
    query= f"SELECT ville, AVG(prix/surface_habitable) FROM transactions_sample WHERE UPPER(type_batiment) = UPPER('{type.value}') GROUP BY ville ORDER BY AVG(prix/surface_habitable) ASC LIMIT '{limit}';"
    return execute_sql_query(con, query)

#12 En tant que CEO, je veux accéder aux 10 villes avec un prix au m2 moyen le plus haut pour les maisons
@app.get("/top_ville_prix_m2_maison_haut", description="Permet de connaitre le top X des villes avec la moyenne du prix au m le plus haut en fonction du logement")
async def top_ville_prix_m2_maison_haut(limit:int, type: Type):
    limit = is_number(limit)
    query= f"SELECT ville, AVG(prix/surface_habitable) FROM transactions_sample WHERE UPPER(type_batiment) = UPPER('{type.value}') GROUP BY ville ORDER BY AVG(prix/surface_habitable) DESC LIMIT '{limit}';"
    return execute_sql_query(con, query)


uvicorn.run(app)