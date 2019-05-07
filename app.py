from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['get', 'post'])
def hello_world():
    param_kleur = request.args.get("kleur")
    if param_kleur is None:
        param_kleur = "green"
    return '''
    <body bgcolor="{}">
        Hello World
        <form method='post'>
            <input type="text" name="kleur" value="type een kleur"><br>
            Username: <input type="text" name="Username"><br>
            wachtwoord: <input type="password" name="Wachtwoord"><br>
            <input type="submit" value="klik">
        </form>
    </body>
    '''.format(param_kleur)


if __name__ == '__main__':
    app.run()
