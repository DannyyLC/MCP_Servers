from pymongo import MongoClient
from typing import Any, List, Dict
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("mongo-server")

@mcp.tool()
def info_db(nombre_coleccion: str = None) -> Dict[str, Any]:
    """
    Devuelve las colecciones y los campos de cada una.
    Si se proporciona una colección, devuelve solo los campos de esa.
    """
    client = MongoClient("mongodb://localhost:27017/")
    db = client["miBaseDeDatos"]  # Cambia por el nombre real

    resultado = {}

    if nombre_coleccion:
        if nombre_coleccion in db.list_collection_names():
            campos = set()
            for doc in db[nombre_coleccion].find().limit(100):
                campos.update(doc.keys())
            resultado[nombre_coleccion] = list(campos)
        else:
            resultado["error"] = f"La colección '{nombre_coleccion}' no existe"
    else:
        for nombre in db.list_collection_names():
            campos = set()
            for doc in db[nombre].find().limit(100):
                campos.update(doc.keys())
            resultado[nombre] = list(campos)

    return resultado

@mcp.tool()
def buscar_documentos(coleccion: str, filtro: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
    """
    Busca documentos dentro de una colección usando un filtro.

    Parámetros:
        coleccion (str): Nombre de la colección.
        filtro (dict): Filtro de búsqueda en formato Mongo (opcional).

    Retorno:
        list: Lista de documentos encontrados.
    """
    client = MongoClient("mongodb://localhost:27017/")
    db = client["miBaseDeDatos"] 

    if coleccion not in db.list_collection_names():
        return [{"error": f"La colección '{coleccion}' no existe"}]

    documentos = list(db[coleccion].find(filtro).limit(20))  # Limitamos resultados para control
    for doc in documentos:
        doc["_id"] = str(doc["_id"])  # Convertir ObjectId a str para serialización
    return documentos

@mcp.tool()
def insertar_documento(coleccion: str, lista_datos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Inserta un nuevo documento en la colección especificada.

    Parámetros:
        coleccion (str): Nombre de la colección.
        lista_datos (list): Lista de diccionarios con los datos a insertar.

    Retorno:
        dict: ID del nuevo documento insertado.
    """
    client = MongoClient("mongodb://localhost:27017/")
    db = client["miBaseDeDatos"] 
    
    resultado = db[coleccion].insert_many(lista_datos)
    return {"inserted_id": [str(_id) for _id in resultado.inserted_ids]}

@mcp.tool()
def actualizar_documento(coleccion: str, filtro: Dict[str, Any], nuevos_valores: Dict[str, Any]) -> Dict[str, Any]:
    """
    Actualiza un documento que cumpla con el filtro, usando nuevos valores.

    Parámetros:
        coleccion (str): Nombre de la colección.
        filtro (dict): Condiciones para encontrar el documento.
        nuevos_valores (dict): Campos y valores a actualizar.

    Retorno:
        dict: Cantidad de documentos modificados.
    """
    client = MongoClient("mongodb://localhost:27017/")
    db = client["miBaseDeDatos"] 
    
    update = {"$set": nuevos_valores}
    resultado = db[coleccion].update_many(filtro, update)
    return {"matched": resultado.matched_count, "modified": resultado.modified_count}

@mcp.tool()
def eliminar_documento(coleccion: str, filtro: Dict[str, Any]) -> Dict[str, Any]:
    """
    Elimina un documento que cumpla con el filtro.

    Parámetros:
        coleccion (str): Nombre de la colección.
        filtro (dict): Filtro de búsqueda del documento a eliminar.

    Retorno:
        dict: Cantidad de documentos eliminados.
    """
    client = MongoClient("mongodb://localhost:27017/")
    db = client["miBaseDeDatos"] 

    resultado = db[coleccion].delete_many(filtro)
    return {"deleted": resultado.deleted_count}

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
