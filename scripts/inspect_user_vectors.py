from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.database import get_user_documents

try:
    from src.vector_store import get_vector_store
except Exception as e:
    print('Vector store import failed:', e)
    get_vector_store = None


# Debug script: prints one customer's documents from the database, then digs into the raw Chroma collection to show
# how many vectors exist for that user and per filename, so a mismatch between the DB and the vector store can be spotted.
def inspect_user(customer_id: str):
    print('User:', customer_id)
    docs = get_user_documents(customer_id, include_deleted=True)
    print('DB documents (include_deleted=True):')
    for d in docs:
        print(' -', d.get('filename'), 'is_deleted=', d.get('is_deleted'), 'chunks=', d.get('chunks_stored'))

    if get_vector_store is None:
        print('Vector store unavailable in this environment.')
        return

    vs = get_vector_store()
    coll = getattr(vs, '_collection', None)
    print('Has _collection:', bool(coll))
    if not coll:
        print('No underlying collection object found; cannot inspect metadata.')
        return

    # Try several collection APIs to fetch items by user_id
    try:
        print('\nTrying coll.get(where={"user_id": customer_id})...')
        items = coll.get(where={'user_id': customer_id})
        print('Got items count (via get):', len(items.get('ids', [])) if isinstance(items, dict) else (len(items) if items else 0))
        # Print metadata for first few
        metadatas = items.get('metadatas') if isinstance(items, dict) else None
        if metadatas:
            for i, md in enumerate(metadatas[:10]):
                print(i, md)
        elif items:
            for i, it in enumerate(items[:10]):
                print(i, getattr(it, 'metadata', getattr(it, 'metadatas', it)))
    except Exception as e:
        print('coll.get failed:', e)

    try:
        print('\nTrying coll.query(filter={"user_id": customer_id})...')
        if hasattr(coll, 'query'):
            q = coll.query(filter={'user_id': customer_id})
            print('query result keys:', list(q.keys()) if isinstance(q, dict) else str(type(q)))
        else:
            print('coll has no query method')
    except Exception as e:
        print('coll.query failed:', e)

    # Try counting by source filenames
    print('\nCounts by source (from DB list):')
    active_names = [d.get('filename') for d in get_user_documents(customer_id, include_deleted=False)]
    for name in active_names:
        try:
            res = coll.get(where={'user_id': customer_id, 'source': name})
            count = 0
            if isinstance(res, dict):
                count = len(res.get('ids', []))
            elif res:
                count = len(res)
            print(f" - {name}: {count} vectors")
        except Exception as e:
            print(f" - {name}: get failed: {e}")


if __name__ == '__main__':
    # change the ID if needed
    inspect_user('CUS_D3B5BJ')
