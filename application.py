from flask import Flask, request, make_response, render_template, url_for
from Bio.Blast import NCBIXML, NCBIWWW
import mysql.connector


def verwerk_get_list_show(list):
    first = True
    final_search = ""

    for term in list:
        if first:
            final_search += term
            first = False
        else:
            final_search += (r" ," + term)
    return final_search

def verwerk_get_list_search(list):
    first = True
    final_search = ""

    for term in list:
        if first:
            final_search += term
            first = False
        else:
            final_search += (r" or " + term)
    return final_search

app = Flask(__name__)


@app.route('/')
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

    final_search = verwerk_get_list_search(searsch_in)
    final_show = verwerk_get_list_show(show)

    print("final search:", final_search)
    print("final show:", final_show)
    print("zoekterm:", zoekterm)

    quiry = ""
    resultaat = ""
    titel_tabel = show

    if zoekterm is not None:
        quiry = "select {} from blastresultatentabel where {} like '%{}%' limit 50".format(final_show, final_search, zoekterm)
        print(quiry)

    if final_show is not "" and zoekterm is None:
        quiry = "select {} from blastresultatentabel limit 50".format(final_show)
        print(quiry)

    if quiry is not "":
        cursor = connection.cursor()
        cursor.execute(quiry)
        resultaat = cursor.fetchall()
        cursor.close()

    site = render_template('database.html', resultaat=resultaat, titel_tabel=titel_tabel)

    connection.close()

    return site


@app.route('/Blast', methods=['get', 'post'])
def blast():
    program = ""
    sequentie = ""
    lijst_res = []
    lijst_titel_kol = []
    counter = 0
    program = request.form.get("program")
    sequentie = request.form.get("sequentie")

    if program and sequentie is not "":
        print("blasting")
        result_handle = NCBIWWW.qblast(
            program=program, database="nr", sequence=sequentie)

        blast_records = NCBIXML.parse(result_handle)
        blast_record = next(blast_records)
        for alignment in blast_record.alignments:
            for hsp in alignment.hsps:
                hit_description = ""
                hit_id = ""
                ids = ""
                e_v = ""
                sc = ""
                gap = ""
                print("-" * 80)
                hit_description = alignment.hit_def
                hit_id = alignment.hit_id
                ids = hsp.identities
                e_v = hsp.expect
                sc = hsp.score
                gap = hsp.gaps
                lijst_res.append([hit_id, hit_description, e_v, sc, ids, gap])
        lijst_titel_kol = ["accessiecode_ncbi", "description", "e_value", "score", "identities", "gaps"]
    print(lijst_res)
    print("done")

    resp = make_response(render_template("blast.html", lijst_res=lijst_res, lijst_titel_kol=lijst_titel_kol))


    return resp


@app.route('/about')
def about():
    resp = make_response(render_template("about.html"))
    return resp


if __name__ == '__main__':
    app.run()
