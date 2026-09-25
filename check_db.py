from sqlalchemy import create_engine, text
engine = create_engine('postgresql+psycopg2://postgres:veer@localhost:5432/flowforge')
with engine.connect() as conn:
    result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'task_embeddings'"))
    rows = result.fetchall()
    if rows:
        for r in rows:
            print(r)
    else:
        print('Table task_embeddings does NOT exist')
    
    # Also check pgvector
    try:
        result2 = conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector'"))
        ext = result2.fetchone()
        if ext:
            print('pgvector extension: INSTALLED')
        else:
            print('pgvector extension: NOT INSTALLED')
    except Exception as e:
        print(f'pgvector check error: {e}')
