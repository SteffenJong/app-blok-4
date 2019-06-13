from tkinter import filedialog
from Bio.Blast import NCBIXML
import mysql.connector
import re

def read_xml(pk_dict, algorythm):

    """ this sunction filters the blast results
    :param pk_dict: the dictionary containing the blast results
    :param algorythm: the algorythm used to get the results
    :return: a dictionary containing the relevant blast results
    """
    #    print(pk_dict)
    blastsdict = []
   # print('-' * 80)
   # print('read xml')
   # print('\n')
    for key in pk_dict:
   #     print('key', pk_dict[key])
        newxml = open('new.xml', 'w')
        newxml.write(pk_dict[key])
        newxml.close()
        result_handle = open("new.xml")
        blast_records = NCBIXML.parse(result_handle)
        for blast_record in blast_records:  # .alignments:
            for alignment in blast_record.alignments:
                for hsp in alignment.hsps:
  #                  print('hspso;dfklc', hsp)
                    hit_dict = {}
                    hit_dict['pk'] = key
                    hit_dict['desctiption'] = alignment.title


 #                   print(hit_dict['desctiption'])
                    hit_dict['acession_ncbi'] = alignment.hit_id
                    hit_dict['e-value'] = hsp.expect
                    hit_dict['score'] = hsp.score
                    hit_dict['gaps'] = hsp.gaps
                    hit_dict['identity'] = (hsp.identities
                                            / hsp.align_length) * 100
                    # 'alignment.Hsp_identity' #alignment.Hsp_identity
                    hit_dict['lengte_alignment'] = blast_record.query_length
#                    print(hit_dict['lengte_alignment'])
 #                   print(hit_dict['acession_ncbi'])
                    hit_dict['query coverage'] = (
                                hsp.align_length / blast_record.query_length)
                    hit_dict['taxonomy'] = '934'
                    hit_dict['algotithm'] = algorythm + blast_record.version

                    blastsdict.append(hit_dict)
    return blastsdict


def fill_db(results):
    """ this function stores the blast results in the database
    :param results: the relevant blast results in a dictionary
    :return: N.V.T.
    """

    connect = mysql.connector.connect(
        host='hannl-hlo-bioinformatica-mysqlsrv.mysql.database.azure.com',
        user="rapwz@hannl-hlo-bioinformatica-mysqlsrv",
        db="rapwz",
        password='pwd123')

    print('_' * 80)
    print('FILL DB')
  #  print(results)
    print('_' * 80)
    loops = 0
    for dict in results:
#        dict['desctiption'] = dict['desctiption'].split('|')[2]
        dict['desctiption'] = re.sub("\w+\|[^\s]*\|",'', dict['desctiption'])

        print(dict['desctiption'])
        print(loops, 'inserted in database, ', len(dict) - loops, '% done')

        try:
            loops += 1
            print('sucess', dict['acession_ncbi'])
            print(dict.values())
            curser = connect.cursor()
        
            curser.execute(
                "insert into blastresultatentabel(description, "
                "accessiecode_ncbi, e_value, score, gaps, identities, "
                "lengte_alignment, query_coverage, "
                "aangeleverdedata_gekregenheader, taxonomy_level, alcgorythm)"
                "values ('{}', '{}', '{}','{}', '{}', '{}', '{}','{}','{}',"
                " null ,'{}')"
                .format(dict['desctiption'], dict['acession_ncbi'],
                        dict['e-value'], dict['score'], dict['gaps'],
                        dict['identity'], dict['lengte_alignment'],
                        dict['query coverage'], dict['pk'],
                        dict['algotithm']))
            connect.commit()
        except mysql.connector.errors.IntegrityError:
            print('IntegrityError', dict['acession_ncbi'])
            print(dict.values())
        except mysql.connector.errors.ProgrammingError:
            print('mistake', loops)
#    print(loops)


def open_bestand():
    """ this function opens an xml file and return the content as a dictionary
    :return: a dictionary containing the ontent of the xml file, using the
    header as key, and the blast algorythm as a string
    """
    algorythm = ''
    pk_dict = {}

    file_name = filedialog.askopenfilename(
        initialdir="/home/johannes/PycharmProjects/untitled2"
        , title="Kies een fasta file"
        , filetypes=(("XML files", "*.xml*"), ("Alle bestanden", "*.*")))

    bestand = open(file_name, 'r')
    for line in bestand:
        if line.startswith('@'):
            line = line.split('\t')
            line = line[0].split('1101')
            key = line[1]
            pk_dict[key] = '<?xml version="1.0"?>\n'
        else:
            if '<BlastOutput_program>' in line:
                algorythm = line.replace('<BlastOutput_program>', '') \
                    .replace('</BlastOutput_program>', '')
            pk_dict[key] += line
    return pk_dict, algorythm


def main():
    pk_list, algorythm = open_bestand()
    results = read_xml(pk_list, algorythm)
#    for dict in results:
 #       dict['desctiption'] = re.sub("\w+\|[^\s]*\|",'', dict['desctiption'])
  #      print(dict['desctiption'])
    fill_db(results)    #   gb|ANY80610.1|


main()
