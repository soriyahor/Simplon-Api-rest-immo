#Contexte du projet

En tant que dev IA, vous serez régulèrement amené à créer une ou plusieurs API Rest dans le cadre de vos projets.
Vous allez utiliser une base PostgreSQL contenant la data immo comme lors du dernier Brief en ressource
FastAPI pour la création de votre API + documentation
Swagger pour tester votre API
Un notebook pour faire la démo. Utiliser le module requests de python pour les appels.

#Modalités pédagogiques
Individuellement vous êtes amenés à créer un dépôt sur github et proposer une implémentation d'une API REST en utilisant FastAPI.
Temps accordé: 2,5 jours

#Mise en place

Il faut que sur notre environnement soit installer :
  -  fastapi : pip install fastapi
  -  uvicorn : pip install uvicorn

voir doc sur ce lien https://fastapi.tiangolo.com/fr/tutorial/first-steps/

On peut commencer à coder le premier user story et utiliser le format json pour les données dynamiques ( comme city ou year)

exemple :

`from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/revenu_fiscal_moyen/")
async def read_item(year: int, city: str):
    return f"SELECT revenu_fiscal_moyen, date, ville FROM foyers_fiscaux WHERE date = {year} AND ville = {city}"
uvicorn.run(app)`

Il faut lancer la commande uvicorn main:app --reload pour lancer le serveur
et regarder sur l'http://127.0.0.1:8000 (le swagger) le resultat.

Pour arreter le serveur, utiliser ctr+C


Ensuite, il sera possible de créer des fonctions :

exemple 

`from fastapi import FastAPI, HTTPException, Depends
import uvicorn

app = FastAPI()

def validate_year(year: str):
    if not year.isdigit() or not (len(year) == 4) :
        raise HTTPException(status_code=400, detail="L'année doit être une valeur numérique de 4 chiffres")

    return year

@app.get("/revenu_fiscal_moyen/")
async def revenu_fiscal_moyen(year: str = Depends(validate_year), city: str = ""):
    # Utilisez la valeur validée de l'année dans votre logique de traitement
    return f"SELECT revenu_fiscal_moyen, date, ville FROM foyers_fiscaux WHERE date = {year} AND ville = {city}"

uvicorn.run(app)`

On va pouvoir tester sur des valeurs réelles d'une base de données.
Pour cela, il faudra mettre le chemin d'accès dans main.py soit mettre sur le local avec le fichier 

A récuperer sur dbeaver : clic droit sur la base de données -> editer connection -> copier le path ou le créer

exemple:

`con = sqlite3.connect(r"C:\Users\Utilisateur\AppData\Roaming\DBeaverData\workspace6\.metadata\sample-database-sqlite-1\Chinook.db")
con = sqlite3.connect('Chinook.db')`
