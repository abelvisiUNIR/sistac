"""
scripts/python/data/mongo_transfer.py
Exporta, respalda o transfiere datos de una base de datos MongoDB a otra.

Este script permite copiar colecciones enteras de datos (cargos, cvs, ground_truth, etc.)
de una instancia/base de datos origen a otra instancia/base de datos destino.

Uso:
    # Copiar de la base por defecto a una base de backup local
    python scripts/python/data/mongo_transfer.py --target-db sistac_tfe_backup

    # Copiar a otro servidor MongoDB
    python scripts/python/data/mongo_transfer.py --target-uri "mongodb://servidor-remoto:27017" --target-db sistac_tfe
"""

from __future__ import annotations

import argparse
import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


def transfer_database(
    source_uri: str,
    source_db_name: str,
    target_uri: str,
    target_db_name: str,
    collections_to_transfer: list[str]
) -> None:
    print("=" * 60)
    print("SISTAC — Herramienta de Transferencia de MongoDB")
    print("=" * 60)
    print(f"Origen  : {source_uri} [{source_db_name}]")
    print(f"Destino : {target_uri} [{target_db_name}]")
    print("-" * 60)

    # 1. Conectar a origen
    try:
        source_client = MongoClient(source_uri, serverSelectionTimeoutMS=3000)
        source_client.server_info()  # Forzar conexión
        source_db = source_client[source_db_name]
        print("[INFO] Conectado con éxito al servidor origen.")
    except ConnectionFailure as e:
        print(f"[ERROR] No se pudo conectar al servidor origen: {e}")
        sys.exit(1)

    # 2. Conectar a destino
    try:
        target_client = MongoClient(target_uri, serverSelectionTimeoutMS=3000)
        target_client.server_info()  # Forzar conexión
        target_db = target_client[target_db_name]
        print("[INFO] Conectado con éxito al servidor destino.")
    except ConnectionFailure as e:
        print(f"[ERROR] No se pudo conectar al servidor destino: {e}")
        sys.exit(1)

    print("-" * 60)

    # 3. Realizar transferencia colección por colección
    for col_name in collections_to_transfer:
        print(f"Procesando colección: '{col_name}'...")
        
        # Verificar si la colección existe en origen y tiene documentos
        if col_name not in source_db.list_collection_names():
            print(f"  [OMITIDO] La colección '{col_name}' no existe en origen.")
            continue
            
        source_col = source_db[col_name]
        target_col = target_db[col_name]
        
        total_docs = source_col.count_documents({})
        if total_docs == 0:
            print(f"  [OMITIDO] La colección '{col_name}' está vacía.")
            continue
            
        print(f"  Encontrados {total_docs} documentos en origen. Copiando...")
        
        # Leer todos los documentos
        documents = list(source_col.find({}))
        
        # Para evitar problemas con el campo _id si ya existe, limpiamos o usamos upsert
        # En este caso, realizamos un reemplazo por ID único o inserción masiva.
        # Si la colección destino tiene datos, podemos limpiarla o actualizar.
        # Por seguridad, realizaremos upsert basándonos en el campo '_id' o campo clave
        
        success_count = 0
        batch_size = 500
        for i in range(0, len(documents), batch_size):
            batch = documents[i : i + batch_size]
            
            # Construir operaciones de escritura
            for doc in batch:
                try:
                    # Usamos update_one con upsert=True para no duplicar si se ejecuta varias veces
                    target_col.update_one({"_id": doc["_id"]}, {"$set": doc}, upsert=True)
                    success_count += 1
                except Exception as err:
                    print(f"  [ERROR DOC] Fallo al copiar documento {doc.get('_id', 'Desconocido')}: {err}")
                    
        print(f"  [ÉXITO] Colección '{col_name}': {success_count}/{total_docs} documentos copiados/actualizados.")
        print()

    print("=" * 60)
    print("Transferencia de base de datos finalizada exitosamente.")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Transfiere o respalda colecciones de MongoDB"
    )
    parser.add_argument(
        "--source-uri",
        default="mongodb://localhost:27017",
        help="URI del servidor MongoDB de origen (default: mongodb://localhost:27017)"
    )
    parser.add_argument(
        "--source-db",
        default="sistac_tfe",
        help="Nombre de la base de datos de origen (default: sistac_tfe)"
    )
    parser.add_argument(
        "--target-uri",
        default="mongodb://localhost:27017",
        help="URI del servidor MongoDB de destino (default: mongodb://localhost:27017)"
    )
    parser.add_argument(
        "--target-db",
        required=True,
        help="Nombre de la base de datos de destino (REQUERIDO)"
    )
    parser.add_argument(
        "--collections",
        default="cargos,cvs,ground_truth,c0_times,evaluaciones,metricas_historial",
        help="Colecciones a transferir separadas por comas (default: cargos,cvs,ground_truth,c0_times,evaluaciones,metricas_historial)"
    )
    
    args = parser.parse_args()
    
    cols = [c.strip() for c in args.collections.split(",") if c.strip()]
    
    transfer_database(
        source_uri=args.source_uri,
        source_db_name=args.source_db,
        target_uri=args.target_uri,
        target_db_name=args.target_db,
        collections_to_transfer=cols
    )
