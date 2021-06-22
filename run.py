from sandwich import app, db
from sandwich.models import User, Shop, Sandwich

if __name__ == '__main__':
    app.run(debug=True)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Shop': Shop, 'Sandwich': Sandwich}