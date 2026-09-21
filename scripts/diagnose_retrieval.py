from pprint import pprint
import sys
from pathlib import Path

# Ensure project root is on sys.path so `src` imports work when running this script
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.database import get_user_documents, get_connection

# Import vector-store pieces optionally (may fail if heavy deps not installed)
try:
    from src.vector_store import search_documents, get_vector_store
except Exception as e:
    print('Optional import failed (vector store):', e)
    search_documents = None
    get_vector_store = None

try:
    from src.embeddings import get_embedding_model
except Exception:
    get_embedding_model = None

# Debug script: prints every document row in the database, checks the vector store connection, then runs a few
# sample search queries for every customer found in the DB so retrieval issues can be spotted from the terminal output.
def main():
    print('--- Database: documents for all users ---')
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('SELECT customer_id, filename, is_deleted, pages_processed, chunks_stored FROM documents ORDER BY uploaded_at DESC')
        rows = cur.fetchall()
        for r in rows[:50]:
            print(r)
    except Exception as e:
        print('DB query error:', e)
    finally:
        conn.close()

    print('\n--- Vector store path & collection status ---')
    if get_vector_store is None:
        print('Vector store import unavailable, skipping.')
    else:
        try:
            vs = get_vector_store()
            coll = getattr(vs, '_collection', None)
            print('Has _collection attr:', bool(coll))
        except Exception as e:
            print('Vector store error:', e)

    print('\n--- Test search for sample queries ---')
    sample_queries = [
        'what is email',
        'what is phone',
        'what is this document about',
    ]

    # Try each customer from DB
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute('SELECT DISTINCT customer_id FROM documents')
        customers = [
            cid for r in cur.fetchall()
            if (cid := (r.get('customer_id') if isinstance(r, dict) else r[0])) is not None
        ]
    except Exception:
        customers = []
    finally:
        conn.close()

    if not customers:
        print('No customers with documents found in DB.')
        return

    for cust in customers:
        print('\n=== Customer:', cust, '===')
        docs = get_user_documents(cust)
        print('Active documents:', [d.get('filename') for d in docs])
        if search_documents is None:
            print('   Vector store unavailable, skipping search.')
            continue
        for q in sample_queries:
            try:
                results = search_documents(query=q, user_id=cust, doc_name=None)
                print(f"Query: '{q}' -> {len(results)} results")
                if results:
                    for r in results[:3]:
                        md = r.metadata
                        print(' - source:', md.get('source'), 'page:', md.get('page'))
                        print('   snippet:', (r.page_content or '')[:200].replace('\n',' '))
                else:
                    print('   No results returned for this query and customer.')
            except Exception as e:
                print('   search_documents error:', e)

if __name__ == '__main__':
    main()
