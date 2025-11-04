from fastapi import APIRouter, UploadFile, File, HTTPException
from db import students, transactions, accounts
from datetime import datetime
import tempfile
import pandas as pd

fees_router = APIRouter()

@fees_router.get("/students", tags=["Fees Management"])
async def list_students(school_code: str):
    """
    Récupère la liste des élèves pour un code d'école donné.
    """
    query = {"school_code": school_code}
    projection = {"_id": 0, "full_name": 1, "student_id": 1, "classroom": 1}
    student_list = list(students.find(query, projection))
    return {"students": student_list}


@fees_router.post("/students", tags=["Fees Management"])
async def import_students(file: UploadFile = File(...)):
    """
    Reçoit un fichier Excel et importe les élèves dans MongoDB.
    Format attendu :
    Nom_Complet | Matricule | Classe | Code_Ecole
    """

    # Vérifie l’extension du fichier
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Le fichier doit être au format Excel (.xlsx ou .xls)")

    try:
        # Enregistre temporairement le fichier reçu
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Lecture du fichier Excel
        df = pd.read_excel(tmp_path)

        # Vérifie les colonnes attendues
        required_columns = ["Nom_Complet", "Matricule", "Classe", "Code_Ecole"]
        for col in required_columns:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"Colonne manquante : {col}")

        # Renommage des colonnes pour correspondre au modèle MongoDB
        df = df.rename(columns={
            "Nom_Complet": "full_name",
            "Matricule": "student_id",
            "Classe": "classroom",
            "Code_Ecole": "school_code"
        })

        # Conversion en dictionnaires
        records = df.to_dict(orient="records")

        # Insertion ou mise à jour (pour éviter les doublons)
        count = 0
        for record in records:
            if not record.get("student_id"):
                continue  # Ignore les lignes sans matricule
            result = students.update_one(
                {"student_id": record["student_id"]},
                {"$set": record},
                upsert=True
            )
            if result.upserted_id or result.modified_count > 0:
                count += 1

        return {"status": "success", "imported": count}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@fees_router.get("/students/{student_id}", tags=["Fees Management"])
async def get_student(student_id: str):
    """
    Récupère les détails d'un élève par son ID.
    """
    student = students.find_one({"student_id": student_id}, {"_id": 0})
    if not student:
        raise HTTPException(status_code=404, detail="Élève non trouvé")
    return student

@fees_router.get("/accounsts/{account_number}/history", tags=["Fees Management"])
async def get_account_history(account_number: str):
    """
    Récupère l'historique des transactions pour un compte donné.
    """
    query = {"account": account_number}
    projection = {"_id": 0}
    transaction_list = list(transactions.find(query, projection))
    return {"transactions": transaction_list}


@fees_router.get("/accounsts/{account_number}", tags=["Fees Management"])
async def get_account_details(account_number: str):
    """
    Récupère les détails d'un compte par son numéro.
    """
    account = accounts.find_one({"account_number": account_number}, {"_id": 0})
    if not account:
        raise HTTPException(status_code=404, detail="Compte non trouvé")
    return account