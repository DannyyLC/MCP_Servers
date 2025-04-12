from typing import Any, List, Dict
from mcp.server.fastmcp import FastMCP
import aiosqlite

# Initialize FastMCP server
mcp = FastMCP("sql-server")

@mcp.tool()
async def query(query: str) -> List[Dict[str, Any]]:
    """Execute a SQL query (SELECT, INSERT, UPDATE, DELETE) and return results if applicable."""
    async with aiosqlite.connect('test.db') as conn:
        cursor = await conn.execute(query)
        
        if query.strip().upper().startswith("SELECT"):
            rows = await cursor.fetchall()
            columns = [column[0] for column in cursor.description] 
            return [dict(zip(columns, row)) for row in rows]  
        else:
            await conn.commit()
            return [{"message": "Query executed successfully"}]
        
@mcp.tool()
async def db_info() -> Dict[str, Any]:
    """Get all the information related to the database, including tables and their columns."""
    db_structure = {}
    
    async with aiosqlite.connect('test.db') as conn:
        cursor = await conn.cursor()
        
        # Obtener nombres de las tablas
        await cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = await cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            
            # Obtener las columnas de cada tabla
            await cursor.execute(f"PRAGMA table_info({table_name})")
            columns = await cursor.fetchall()
            
            db_structure[table_name] = [column[1] for column in columns]  
    
    return db_structure


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
