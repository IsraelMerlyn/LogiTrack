import sqlite3
import time
from concurrent import futures
import grpc
import sys
import os

sys.path.append(os.path.dirname(__file__))

import user_pb2
import user_pb2_grpc

class UserServiceServicer(user_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):
        user_id = request.id
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, email, ultimo_login FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return user_pb2.UserResponse(
                id=row[0],
                nombre=row[1],
                email=row[2],
                ultimo_login=row[3]
            )
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Usuario no encontrado")
            return user_pb2.UserResponse()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(UserServiceServicer(), server)
    server.add_insecure_port("[::]:5002")
    print("🚀 Servidor gRPC corriendo en el puerto 5002...")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == "__main__":
    serve()
