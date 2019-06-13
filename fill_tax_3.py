from Bio import Entrez
import mysql.connector
import time


def get_acession(acession, dab):
    """
    :param acession: an NCBI acession code
    :param dab: the database to search
    :return: a list containing the taxonomy matching the acession code
    """
    Entrez.email = "Johannesschonthaler@gmail.com"  # Always tell NCBI who you are
    handle = Entrez.efetch(db=dab, id=str(acession), rettype="gb",
                           retmode="text")
    webpage = handle.readlines()
    org = False
    results = []
    for line in webpage:
        if line.find('ORGANISM') != -1:
            org = True
        if line.find('REFERENCE') != -1 or line.find('COMMENT') != -1:
            org = False
        if org:
            line = line.replace(' ', '').replace('.', '').replace('\n', '')\
                .replace('ORGANISM', '')
            line = line.split(';')
            for i in line:
                if not  i == '':
                    results.append(i)
            print('line', line)
    print('results', results)
    return results


def get_data():
    """ this function is meant to retreave the acession codes where the
    taxonomylevel is 934
    :return: a list containing the acession codes where the taxonomylevel
    is 934, and the connect
    """
    connect = mysql.connector.connect(
        host='hannl-hlo-bioinformatica-mysqlsrv.mysql.database.azure.com',
        user="rapwz@hannl-hlo-bioinformatica-mysqlsrv",
        db="rapwz",
        password='pwd123')

    curser = connect.cursor()
    curser.execute("select accessiecode_ncbi from blastresultatentabel "
                   "where taxonomy_level like '934';")
    Data = curser.fetchall()
    return Data, connect


def taxonomy(acession, tax, connect):
    """ this function fills the taxonomy table in the database, and updates
    the foreign key in the blast_results table to match the organism name in
    the taxonomy table
    :param acession: the acession code matching the description
    :param tax: a list containing the taxonomy
    :param connect: the connection variable
    :return: none
    """
    print('tax', tax)
    name = tax[0]
    tax[0] = 'organisms'
    tax.append(name)
    print('tax', tax)
    curser = connect.cursor()
    tax_prev_level = 0
    print(len(tax)-1)
    for level in range(len(tax)):
        print('for level taxonomy in range len(tax) -1')
        print('-'*80)
        print('level', level)
        print('tax level = ', tax[level])
        curser.execute(
            "select taxonomy_level from taxonomy where taxonomyName "
            "like '{}';".format(tax[level]))    # check if level in db
        tax_level = curser.fetchall()
        try:
            tax_prev_level = tax_level[0][0]   # stores the previous value for the
                                        # insertion f the new level.

        except IndexError:      #if error ccurs, the string is not in the db
            curser.execute('select count(taxonomy_level) from taxonomy;')
            fetch_primkey = curser.fetchall()
            primkey =  fetch_primkey[0][0]+2
            print('new level found')
            print( 'data_to_insert', primkey, tax[level], tax_prev_level)
            data_to_insert = "insert into taxonomy(taxonomy_level, taxonomyName, TaxonomyLevelHigher) values('{}', '{}', '{}');".format(primkey, tax[level], tax_prev_level)
            print(data_to_insert)
            curser.execute(data_to_insert)
            connect.commit()
            tax_prev_level = primkey

        if len(tax)-1 == level:
            get_Tax_level = "select taxonomy_level from taxonomy " \
                            "where taxonomyName like '{}';".format(tax[level])
            print(get_Tax_level)
            curser.execute(get_Tax_level)
            fetch_primkey = curser.fetchall()
            primkey =  fetch_primkey[0][0]
            print(primkey)

            print('update foreighn key')
            print('-'*80)
            print('primkey', primkey)
            print('acession', acession)
            print('set', primkey, 'where acession', acession)
            executestr = "UPDATE blastresultatentabel SET " \
                         "taxonomy_level = '{}' WHERE " \
                         "accessiecode_ncbi like '%{}%';"\
                .format(primkey, acession)
            print(executestr)
            curser.execute(executestr)
            print('bout to commit')
            connect.commit()
            print('comitted')


def main():
    acession_list, connect = get_data()
    print(acession_list)
    loops = 0
    for result in acession_list:
        loops += 1
        print('result', result)
        acession = result[0].split('|')[1]
        print('acession', acession)
        time.sleep(.6)
        try:
            dab = 'protein'
            tax = get_acession(acession, dab)
            taxonomy(acession, tax, connect)

        except:
            try:
                dab = 'nucleotide'
                tax = get_acession(acession, dab)
                taxonomy(acession, tax, connect)

            except:
                try:
                    dab = 'genome'
                    tax = get_acession(acession, dab)
                    taxonomy(acession, tax, connect)
                except:
                    print('no result')

        print(loops, 'out of ', len(acession_list))


main()
