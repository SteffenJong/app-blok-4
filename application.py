from flask import Flask, request, make_response, render_template, url_for
import mysql.connector


def verwerk_get_list(list):
    first = True
    final_search = ""

    for term in list:
        if first:
            final_search += term
            first = False
        else:
            final_search += (r" ," + term)
    return final_search

app = Flask(__name__)


@app.route('/', methods=['get', 'post'])
def homepage():
    resp = make_response(render_template("homepage.html"))
    return resp


@app.route('/database/', methods=['get', 'post'])
def database():
    connection = mysql.connector.connect(host="hannl-hlo-bioinformatica-mysqlsrv.mysql.database.azure.com",
                                         user="rapwz@hannl-hlo-bioinformatica-mysqlsrv", db="rapwz", password="pwd123")

    searsch_in = request.form.getlist("search_in")
    show = request.form.getlist("show")
    zoekterm = request.form.get("zoekterm")

    print(searsch_in)
    print(show)
    print(zoekterm)

    final_show = ""
    final_search = ""

    final_search = verwerk_get_list(searsch_in)
    final_show = verwerk_get_list(show)

    print("final search:", final_search)
    print("final show:", final_show)
    print("zoekterm:", zoekterm)

    quiry = ""
    resultaat = ""
    titel_tabel = show

    if zoekterm is not None:
        quiry = "select {} from blastresultatentabel where {} like '%{}%' limit 50".format(final_show, final_search, zoekterm)
        print(quiry)
        cursor = connection.cursor()
        cursor.execute(quiry)
        resultaat = cursor.fetchall()
        cursor.close()
        print(resultaat, "-" * 80)
        print("zoekterm is not none")

    if final_show is not "" and zoekterm is None:
        quiry = "select {} from blastresultatentabel limit 50".format(final_show)
        print(quiry)
        cursor = connection.cursor()
        print("zoekterm is none ")
        print(final_show)
        cursor.execute(quiry)
        resultaat = cursor.fetchall()
        cursor.close()
        print(resultaat, "-" * 80)

    site = render_template('database.html', resultaat=resultaat, titel_tabel=titel_tabel)

    connection.close()

    return site


@app.route('/Blast', methods=['get', 'post'])
def blast():
    resp = make_response(render_template("blast.html"))
    return resp


@app.route('/about', methods=['get', 'post'])
def about():
    resp = make_response(render_template("about.html"))
    return resp


if __name__ == '__main__':
    app.run()
