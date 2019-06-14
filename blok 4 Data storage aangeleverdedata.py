import re
import mysql.connector


def open_file():
    """This function serves to open .xml files
    :return: it returns the .xml file
    """
    file = open('report_n.xml', 'r')
    filecontent = file.readlines()
    #    print(filecontent)
    #    for line in filecontent:
    #       print(line)
    return filecontent


def sort(filecontent, connect):
    """This function serves to retreave the sequences and headers from the
    .xml file, and send them to the function where they are stored.
    :param filecontent: the contents of the file
    :param connect: a variable containing the connection info.
    :return: None
    """
    seqheaderlist = []

    resultsdict = {}
    for line in filecontent:

        # find sequence & fastq header
        if line.startswith('@'):
            line = line.split('	')
            seq_header = line[0]
            seqheaderlist.append(seq_header)
            resultsdict['seq_header'] = seq_header
            seq = line[1]

            store_seq_table(seq_header, seq, connect)


def store_seq_table(seq_header, seq, connect):
    """this function stores the sequence and the header in the database
    :param seq_header: the unique part of the header
    :param seq: the sequence
    :param connect: a variable containing the connection info.
    :return: none
    """
    seq_header = seq_header.split('1101')
    print('seq = ', seq)
    print('seq_header = ', seq_header)

    curser = connect.cursor()

    curser.execute(
        "insert into geleverdedata(gekregen_header, sequenties)"
        "values ('{}', '{}');"
            .format(seq_header[1], seq))
    connect.commit()


def main():
    filecontent = open_file()
    connect = mysql.connector.connect(
        host='hannl-hlo-bioinformatica-mysqlsrv.mysql.database.azure.com',
        user="rapwz@hannl-hlo-bioinformatica-mysqlsrv",
        db="rapwz",
        password='pwd123')

    sort(filecontent, connect)


main()

