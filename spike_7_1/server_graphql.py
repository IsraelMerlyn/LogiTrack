import sqlite3
import strawberry
from strawberry.flask.views import GraphQLView
from flask import Flask

@strawberry.type
class User:
    id: int
    nombre: str
    email: str
    ultimo_login: str

@strawberry.type
class Query:
    @strawberry.field
    def user(self, id: int) -> User | None:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, email, ultimo_login FROM users WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(id=row[0], nombre=row[1], email=row[2], ultimo_login=row[3])
        return None

schema = strawberry.Schema(query=Query)

app = Flask(__name__)
app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view("graphql_view", schema=schema)
)

if __name__ == "__main__":
    app.run(port=5001, debug=False)
