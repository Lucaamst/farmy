#!/usr/bin/env python3
"""
Script per cambiare la password del Super Amministratore FarmyGo
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from dotenv import load_dotenv
from pathlib import Path

# Carica variabili ambiente
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

# Configurazione
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME')

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

async def change_super_admin_password():
    print("🔐 CAMBIO PASSWORD SUPER AMMINISTRATORE FARMYGO")
    print("=" * 50)
    
    # Connessione MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Trova il super admin
        admin_user = await db.users.find_one({"role": "super_admin"})
        
        if not admin_user:
            print("❌ Super admin non trovato nel database!")
            return
        
        print(f"✅ Super admin trovato: {admin_user['username']}")
        print()
        
        # Richiedi nuova password
        print("Inserisci la nuova password per il super admin:")
        new_password = input("Nuova password: ").strip()
        
        if len(new_password) < 6:
            print("❌ La password deve essere di almeno 6 caratteri!")
            return
        
        # Conferma password
        confirm_password = input("Conferma password: ").strip()
        
        if new_password != confirm_password:
            print("❌ Le password non coincidono!")
            return
        
        # Hash della nuova password
        hashed_password = hash_password(new_password)
        
        # Aggiorna nel database
        result = await db.users.update_one(
            {"role": "super_admin"},
            {"$set": {"password": hashed_password}}
        )
        
        if result.modified_count > 0:
            print()
            print("✅ Password super admin aggiornata con successo!")
            print(f"🔑 Nuove credenziali:")
            print(f"   Username: {admin_user['username']}")
            print(f"   Password: {new_password}")
            print()
            print("⚠️  IMPORTANTE: Annota queste credenziali in un posto sicuro!")
        else:
            print("❌ Errore durante l'aggiornamento della password!")
            
    except Exception as e:
        print(f"❌ Errore: {e}")
    finally:
        client.close()

async def show_current_admin():
    """Mostra le informazioni del super admin attuale"""
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        admin_user = await db.users.find_one({"role": "super_admin"})
        if admin_user:
            print("📋 SUPER ADMIN ATTUALE:")
            print(f"   ID: {admin_user['id']}")
            print(f"   Username: {admin_user['username']}")
            print(f"   Creato: {admin_user.get('created_at', 'N/A')}")
            print(f"   Attivo: {admin_user.get('is_active', 'N/A')}")
        else:
            print("❌ Nessun super admin trovato!")
    except Exception as e:
        print(f"❌ Errore: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    print("🚀 FARMYGO - GESTIONE PASSWORD SUPER ADMIN")
    print()
    
    choice = input("Cosa vuoi fare?\n1. Visualizza super admin attuale\n2. Cambia password\nScelta (1/2): ").strip()
    
    if choice == "1":
        asyncio.run(show_current_admin())
    elif choice == "2":
        asyncio.run(change_super_admin_password())
    else:
        print("❌ Scelta non valida!")