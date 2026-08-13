import time
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, joinedload, selectinload
from sqlalchemy.engine import Engine
from models import Base, Usuario, Pedido, Producto

DB_URL = "sqlite:///spike_7_4/orm_spike.db"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Interceptor para contar consultas SQL
query_count = 0

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    global query_count
    query_count += 1

def sembrar_datos():
    session = SessionLocal()
    if session.query(Usuario).count() > 0:
        print(" Base de datos ya poblada.")
        session.close()
        return

    print(" Poblando base de datos con 1000 Usuarios, 5000 Pedidos y Productos...")
    productos = [Producto(nombre=f"Prod {i}", precio=10.5 * i) for i in range(1, 4)]
    session.add_all(productos)
    session.commit()

    usuarios = []
    for i in range(1, 1001):
        u = Usuario(nombre=f"User {i}", email=f"user{i}@test.com")
        for j in range(5):
            p = Pedido(total=100.0)
            p.productos.extend(productos)
            u.pedidos.append(p)
        usuarios.append(u)
    
    session.add_all(usuarios)
    session.commit()
    session.close()
    print(" Datos sembrados con éxito.")

def medir_lazy_load():
    global query_count
    query_count = 0
    session = SessionLocal()
    t0 = time.perf_counter()
    
    usuarios = session.query(Usuario).all()
    for u in usuarios:
        for p in u.pedidos:  # Dispara Query por cada usuario
            for prod in p.productos: # Dispara Query por cada pedido
                pass

    t1 = time.perf_counter()
    session.close()
    return (t1 - t0) * 1000, query_count

def medir_joinedload():
    global query_count
    query_count = 0
    session = SessionLocal()
    t0 = time.perf_counter()
    
    usuarios = session.query(Usuario).options(
        joinedload(Usuario.pedidos).joinedload(Pedido.productos)
    ).all()
    
    for u in usuarios:
        for p in u.pedidos:
            for prod in p.productos:
                pass

    t1 = time.perf_counter()
    session.close()
    return (t1 - t0) * 1000, query_count

def medir_selectinload():
    global query_count
    query_count = 0
    session = SessionLocal()
    t0 = time.perf_counter()
    
    usuarios = session.query(Usuario).options(
        selectinload(Usuario.pedidos).selectinload(Pedido.productos)
    ).all()
    
    for u in usuarios:
        for p in u.pedidos:
            for prod in p.productos:
                pass

    t1 = time.perf_counter()
    session.close()
    return (t1 - t0) * 1000, query_count

if __name__ == "__main__":
    print("\n Módulo 7 — Spike 7.4: Benchmark de Mapeo Objeto-Relacional (N+1)\n")
    sembrar_datos()

    print("\nEjecutando pruebas de lectura (1000 usuarios con relaciones anidadas)...\n")
    
    t_lazy, q_lazy = medir_lazy_load()
    t_joined, q_joined = medir_joinedload()
    t_selectin, q_selectin = medir_selectinload()

    print("=" * 65)
    print(f"{'Estrategia':<20} | {'Tiempo (ms)':<15} | {'Consultas SQL Generadas'}")
    print("=" * 65)
    print(f"{'Lazy Loading (Default)':<20} | {t_lazy:>11.2f} ms | {q_lazy:>15} (N+1 Fatal)")
    print(f"{'JoinedLoad (JOINs)':<20} | {t_joined:>11.2f} ms | {q_joined:>15} (Unica Query)")
    print(f"{'SelectInLoad (IN)':<20} | {t_selectin:>11.2f} ms | {q_selectin:>15} (Lotes eficientes)")
    print("=" * 65 + "\n")
