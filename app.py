from flask import Flask, jsonify, request, render_template, redirect, url_for, abort, session
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from src.service import ItemStore

app = Flask(__name__)
app.secret_key = "dev-secret-change-me"  # for sessions (OK for lab)

# --- demo users store (in-memory) ---
# users[username] = {"username": "...", "password_hash": "..."}
users = {}

def current_user():
    uname = session.get("user")
    return users.get(uname) if uname else None

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user():
            return redirect(url_for("login", next=request.path))
        return fn(*args, **kwargs)
    return wrapper

store = ItemStore()
store.create_item("Pens", 10)
store.create_item("Notebooks", 5)
store.create_item("A4 Papers", 500)

# ---------------- HTML UI ----------------
@app.get("/")
def index():
    items = store.list_items()
    user = current_user()
    return render_template("index.html", items=items, user=user)

@app.get("/ui/new")
@login_required
def new_item_form():
    return render_template("new_item.html", user=current_user())

@app.post("/ui/create")
@login_required
def create_item_form():
    name = (request.form.get("name") or "").strip()
    quantity_raw = (request.form.get("quantity") or "0").strip()
    try:
        quantity = int(quantity_raw)
    except ValueError:
        return render_template("new_item.html", error="Quantity must be an integer.",
                               name=name, quantity=quantity_raw, user=current_user()), 400
    if not name:
        return render_template("new_item.html", error="Name is required.",
                               name=name, quantity=quantity_raw, user=current_user()), 400
    store.create_item(name, quantity)
    return redirect(url_for("index"))

@app.get("/ui/edit/<int:item_id>")
@login_required
def edit_item_form(item_id: int):
    item = store.get_item(item_id)
    if not item:
        abort(404)
    return render_template("edit_item.html", item=item, user=current_user())

@app.post("/ui/update/<int:item_id>")
@login_required
def update_item_form(item_id: int):
    item = store.get_item(item_id)
    if not item:
        abort(404)
    name = (request.form.get("name") or "").strip()
    quantity_raw = (request.form.get("quantity") or "0").strip()
    if not name:
        return render_template("edit_item.html", item=item, error="Name is required.", user=current_user()), 400
    try:
        quantity = int(quantity_raw)
    except ValueError:
        return render_template("edit_item.html", item=item, error="Quantity must be an integer.", user=current_user()), 400
    store.update_item(item_id, name=name, quantity=quantity)
    return redirect(url_for("index"))

@app.post("/ui/delete/<int:item_id>")
@login_required
def delete_item_form(item_id: int):
    ok = store.delete_item(item_id)
    if not ok:
        abort(404)
    return redirect(url_for("index"))

# ---------------- AUTH PAGES ----------------
@app.get("/auth/register")
def register():
    if current_user():
        return redirect(url_for("index"))
    return render_template("auth_register.html")

@app.post("/auth/register")
def do_register():
    if current_user():
        return redirect(url_for("index"))
    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""
    if not username or not password:
        return render_template("auth_register.html", error="Username and password required", username=username), 400
    if username in users:
        return render_template("auth_register.html", error="Username already exists", username=username), 400
    users[username] = {"username": username, "password_hash": generate_password_hash(password)}
    session["user"] = username
    next_url = request.args.get("next") or url_for("index")
    return redirect(next_url)

@app.get("/auth/login")
def login():
    if current_user():
        return redirect(url_for("index"))
    return render_template("auth_login.html")

@app.post("/auth/login")
def do_login():
    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""
    u = users.get(username)
    if not u or not check_password_hash(u["password_hash"], password):
        return render_template("auth_login.html", error="Invalid credentials", username=username), 400
    session["user"] = username
    next_url = request.args.get("next") or url_for("index")
    return redirect(next_url)

@app.post("/auth/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))

# ---------------- JSON API (unchanged) ----------------
@app.get("/items")
def list_items_api():
    items = [vars(i) for i in store.list_items()]
    return jsonify(items), 200

@app.post("/items")
def create_item_api():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    quantity = data.get("quantity", 0)
    if not name:
        return jsonify({"error": "name is required"}), 400
    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return jsonify({"error": "quantity must be an integer"}), 400
    item = store.create_item(name, quantity)
    return jsonify(vars(item)), 201

@app.get("/items/<int:item_id>")
def get_item_api(item_id: int):
    item = store.get_item(item_id)
    if not item:
        return jsonify({"error": "not found"}), 404
    return jsonify(vars(item)), 200

@app.put("/items/<int:item_id>")
def update_item_api(item_id: int):
    item = store.get_item(item_id)
    if not item:
        return jsonify({"error": "not found"}), 404
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    quantity = data.get("quantity")
    if name is not None:
        name = str(name).strip()
        if not name:
            return jsonify({"error": "name cannot be empty"}), 400
    if quantity is not None:
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return jsonify({"error": "quantity must be an integer"}), 400
    updated = store.update_item(item_id, name=name, quantity=quantity)
    return jsonify(vars(updated)), 200

@app.delete("/items/<int:item_id>")
def delete_item_api(item_id: int):
    ok = store.delete_item(item_id)
    if not ok:
        return jsonify({"error": "not found"}), 404
    return jsonify({"status": "deleted"}), 200

if __name__ == "__main__":
    app.run(debug=True)
