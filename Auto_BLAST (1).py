"""
Auto-BLAST
Auteur: Demi van der Pasch

De functie van dit script is het automatisch uitvoeren van een BLAST
over meerdere sequenties in FASTQ-format die zich in een Excel-betstand
bevinden. De resultaten worden uiteindelijk opgeslagen in een
xml-bestand, zodat deze later in een database verwerkt kan worden.

Side note: alle prints die in het script terug te vinden zijn hebben een
functie in het bijhouden van waar het script gebleven is en hoe lang het
hier mee bezig is.

"""

# Hier worden packages geïmporteerd.
import pandas as pd
from Bio.Blast import NCBIWWW
import time


class BLAST:

    def __init__(self):
        print('~ START SCRIPT')

        # Deze string bevat de locatie van het in te lezen bestand.
        self.loc_input = "/home/demivdpasch/Documents/Course 4" \
                         "/Course4_dataset_v03.xlsx"

        # Deze string bevat de locatie van het bestand dat de output van
        # blastn zal gaan bevatten.
        self.loc_output_n = "report_n.xml"

        # Hier worden lege strings aangemaakt.
        self.headers = ""
        self.seqs = ""
        self.qscore = ""

        # Hier worden functies aangeroepen.
        self.excel_inlezen()
        print('~ einde inlezen')
        self.blast_n()
        print('~ einde blast_n')
        print('~ EINDE SCRIPT')

    def excel_inlezen(self):
        """ Deze functie verwerkt de kolommen uit een Excel-bestand in
        de vorm van lijsten.

        input:
        -   self.loc_best: deze string bevat de locatie van het Excel-
            bestand dat verwerkt moet worden.

        output:
        -   self.headers: een lijst met de headers uit het bestand.
        -   self.seqs: een lijst met de sequenties uit het bestand.
        -   self.qscore: een lijst met de quality scores uit het
            bestand.
        """
        print('~ start inlezen')

        # Hier wordt het Excel-bestand ingelezen.
        excel = pd.ExcelFile(self.loc_input)

        # Hier wordt enkel het gewenste tabblad geselecteerd en wordt
        # aangegeven dat er geen sprake is van headers.
        sheet = excel.parse("groep13", header=None)

        # Hier worden de headers, sequenties en quality scores in een
        # eigen lijst opgeslagen.
        self.headers = list(sheet[0]) + list(sheet[3])
        self.seqs = list(sheet[1]) + list(sheet[4])
        self.qscore = list(sheet[2]) + list(sheet[5])

    def blast_n(self):
        """ Deze functie voert een BLAST uit over meerdere sequenties en
        slaat deze gegevens automatisch op in een xml-bestand.

        input:
        -   self.headers: een lijst met de headers uit het bestand.
        -   self.seqs: een lijst met de sequenties uit het bestand.
        -   self.qscore: een lijst met de quality scores uit het
            bestand.

        output:
        -   report_n.xml: een xml-bestand met hierin alle resultaten
            van de uitgevoerde blastn.
        """
        print('~ start blast_n')

        # De beginwaarde van count wordt vastgesteld op -1.
        count = -1

        # Hier wordt geïtereerd over de sequenties in self.seqs.
        for seq in self.seqs:

            # Het bestand wordt geopend om gegevens toe te voegen.
            bestand = open(self.loc_output_n, 'a')

            # Per sequentie neemt count toe met 1.
            count += 1

            print('~ start sequentie', count, '(', time.ctime(),
                  '), header:', self.headers[count])

            # Hier wordt het resultaat van blastn in opgeslagen.
            result_handle = NCBIWWW.qblast(
                program="blastx", database="nr", sequence=seq,
                matrix_name="BLOSUM62", hitlist_size=75)

            # De headers, sequenties, quality score en blastn-resultaten
            # worden aan het xml-bestand toegevoegd.
            bestand.write(self.headers[count] + '\t'
                          + seq + '\t' + self.qscore[count])
            bestand.write(result_handle.getvalue())
            bestand.write('\n\n')

            print('\t\t\t~ einde', '(', time.ctime(), ')')

            # Het xml-bestand wordt gesloten.
            bestand.close()


def main():
    BLAST()


main()
