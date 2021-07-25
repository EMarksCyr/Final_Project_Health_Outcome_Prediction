from sqlalchemy.sql.functions import user
from data_encoding import (
    get_encoding_table,
    get_field,
)

import zipfile
import glob
from pathlib import Path
import os
import time
import csv
from sqlalchemy import create_engine
from getpass import getpass

_TMP_DIR = Path("./tmp/")

user_id = 0
question_id_cache = {}  # field:question_id


def decode_line(line):
    l = []
    for field in get_encoding_table():
        l.append(get_field(line, field))
    return l


# TODO: update
def db_get_question_value_info_from_answer(db, question_id, question_answer):
    result = db.execute(
        """SELECT * FROM question_values
        WHERE
            question_id = %s AND
            (value = %s OR
                (value_end IS NOT NULL AND value <= %s AND %s <= value_end))
        """,
        (question_id, question_answer, question_answer, question_answer),
    )
    return result.fetchall()


# TODO: update
def is_user_answer_hidden(db, question_id, question_answer):
    """True if the given user answer correponds to a hidden question value.

    NOTE: User answers that have a value (ie. are not NULL or blank) can correspond to a hidden
    question value.
    """
    # If value is not in q vals and hidden is in q vals then is hidden answer
    value_rows = db_get_question_value_info_from_answer(
        db, question_id, question_answer
    )

    if not value_rows:
        # Check for HIDDEN value
        result = db.execute(
            "SELECT * FROM question_values WHERE question_id = %s AND value IS NULL",
            (question_id,),
        )
        rows = result.fetchall()
        if len(rows) > 0:
            assert (
                len(rows) == 1
            )  # Should be exactly one HIDDEN valid value per question

            # There is a valid HIDDEN value
            return True

        return False


from pathlib import Path


def extract_data():
    file = "./data/LLCP2019.ASC"
    assert Path(file).exists()
    with open(file, "r") as f:
        for line in f:
            yield decode_line(line)


def db_insert_user_answers(db, vals_to_insert):
    db.execute(
        """INSERT INTO user_answers(
        _STATE,
FMONTH, IDATE, IMONTH, IDAY, IYEAR, DISPCODE, SEQNO , _PSU , CTELENM1, PVTRESD1, COLGHOUS, STATERE1, CELPHONE, LADULT1, COLGSEX, NUMADULT, LANDSEX, NUMMEN, NUMWOMEN, RESPSLCT, SAFETIME, CTELNUM1, CELLFON5, CADULT1, CELLSEX, PVTRESD3, CCLGHOUS, CSTATE1, LANDLINE, HHADULT, SEXVAR, GENHLTH, PHYSHLTH, MENTHLTH, POORHLTH, HLTHPLN1, PERSDOC2, MEDCOST, CHECKUP1, BPHIGH4, BPMEDS, CHOLCHK2, TOLDHI2, CHOLMED2, CVDINFR4, CVDCRHD4, CVDSTRK3, ASTHMA3, ASTHNOW, CHCSCNCR, CHCOCNCR, CHCCOPD2, ADDEPEV3, CHCKDNY2, DIABETE4, DIABAGE3, HAVARTH4, ARTHEXER, ARTHEDU, LMTJOIN3, ARTHDIS2, JOINPAI2, MARITAL, EDUCA, RENTHOM1, NUMHHOL3, NUMPHON3, CPDEMO1B, VETERAN3, EMPLOY1, CHILDREN, INCOME2, WEIGHT2, HEIGHT3, PREGNANT, DEAF, BLIND, DECIDE, DIFFWALK, DIFFDRES, DIFFALON, SMOKE100, SMOKDAY2, STOPSMK2, LASTSMK2, USENOW3, ALCDAY5, AVEDRNK3, DRNK3GE5, MAXDRNKS, EXERANY2, EXRACT11, EXEROFT1, EXERHMM1, EXRACT21, EXEROFT2, EXERHMM2, STRENGTH, FRUIT2, FRUITJU2, FVGREEN1, FRENCHF1, POTATOE1, VEGETAB2, FLUSHOT7, FLSHTMY3, TETANUS1, PNEUVAC4, HIVTST7, HIVTSTD3, HIVRISK5, PDIABTST, PREDIAB1, INSULIN1, BLDSUGAR, FEETCHK3, DOCTDIAB, CHKHEMO3, FEETCHK, EYEEXAM1, DIABEYE, DIABEDU, TOLDCFS, HAVECFS, WORKCFS, TOLDHEPC, TRETHEPC, PRIRHEPC, HAVEHEPC, HAVEHEPB, MEDSHEPB, HPVADVC3, HPVADSHT, IMFVPLA1, SHINGLE2, LCSFIRST, LCSLAST, LCSNUMCG, LCSCTSCN, HADMAM, HOWLONG, HADPAP2, LASTPAP2, HPVTEST, HPLSTTST, HADHYST2, PCPSAAD3, PCPSADI1, PCPSARE1, PSATEST1, PSATIME, PCPSARS1, PCPSADE1, PCDMDEC1, BLDSTOOL, LSTBLDS3, HADSIGM3, HADSGCO1, LASTSIG3, CNCRDIFF, CNCRAGE, CNCRTYP1, CSRVTRT3, CSRVDOC1, CSRVSUM, CSRVRTRN, CSRVINST, CSRVINSR, CSRVDEIN, CSRVCLIN, CSRVPAIN, CSRVCTL2, HLTHCVR1, ASPIRIN, HOMBPCHK, HOMRGCHK, WHEREBP, SHAREBP, WTCHSALT, DRADVISE, INDORTAN, NUMBURN3, SUNPRTCT, WKDAYOUT, WKENDOUT, CIMEMLOS, CDHOUSE, CDASSIST, CDHELP, CDSOCIAL, CDDISCUS, CAREGIV1, CRGVREL3, CRGVLNG1, CRGVHRS1, CRGVPRB3, CRGVALZD, CRGVPER1, CRGVHOU1, CRGVEXPT, ACEDEPRS, ACEDRINK, ACEDRUGS, ACEPRISN, ACEDIVRC, ACEPUNCH, ACEHURT1, ACESWEAR, ACETOUCH, ACETTHEM, ACEHVSEX, PFPPRVN3, TYPCNTR8, NOBCUSE7, ASBIALCH, ASBIDRNK, ASBIBING, ASBIADVC, ASBIRDUC, MARIJAN1, USEMRJN2, RSNMRJN1, FOODSTMP, BIRTHSEX, SOMALE, SOFEMALE, TRNSGNDR, RCSGENDR, RCSRLTN2, CASTHDX2, CASTHNO2, QSTVER, QSTLANG, _METSTAT, _URBSTAT, MSCODE, _STSTR, _STRWT , _RAWRAKE , _WT2RAKE , _IMPRACE, _CHISPNC, _CRACE1, _CPRACE, _CLLCPWT , _DUALUSE, _DUALCOR , _LLCPWT2 , _LLCPWT , _RFHLTH, _PHYS14D, _MENT14D, _HCVU651, _RFHYPE5, _CHOLCH2, _RFCHOL2, _MICHD, _LTASTH1, _CASTHM1, _ASTHMS1, _DRDXAR2, _LMTACT2, _LMTWRK2, _PRACE1, _MRACE1  , _HISPANC, _RACE, _RACEG21, _RACEGR3, _RACE_G1, _SEX, _AGEG5YR, _AGE65YR, _AGE80, _AGE_G, HTIN4, HTM4, WTKG3, _BMI5, _BMI5CAT, _RFBMI5, _CHLDCNT, _EDUCAG, _INCOMG, _SMOKER3, _RFSMOK3, DRNKANY5, DROCDY3_, _RFBING5, _DRNKWK1, _RFDRHV7, _TOTINDA, METVL11_, METVL21_, MAXVO21_, FC601_, ACTIN12_, ACTIN22_, PADUR1_, PADUR2_, PAFREQ1_, PAFREQ2_, _MINAC11, _MINAC21, STRFREQ_, PAMISS2_, PAMIN12_, PAMIN22_, PA2MIN_, PAVIG12_, PAVIG22_, PA2VIGM_, _PACAT2, _PAINDX2, _PA150R3, _PA300R3, _PA30022, _PASTRNG, _PAREC2, _PASTAE2, FTJUDA2_, FRUTDA2_, GRENDA1_, FRNCHDA_, POTADA1_, VEGEDA2_, _MISFRT1, _MISVEG1, _FRTRES1, _VEGRES1, _FRUTSU1, _VEGESU1, _FRTLT1A, _VEGLT1A, _FRT16A, _VEG23A, _FRUITE1, _VEGETE1, _FLSHOT7, _PNEUMO3, _AIDTST4 ) VALUES (
%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
%s, %s, %s)""",
        vals_to_insert,
    )


DB_INSERT_BATCH_SIZE = 5000

if __name__ == "__main__":
    t0 = time.time()

    password = getpass("Enter database password")
    db = create_engine(f"postgresql://postgres:{password}@localhost:5432/BRFSSAnalysis")

    db.execute("TRUNCATE user_answers")

    vals_to_insert = []

    for user_answers in extract_data():
        vals_to_insert.append(user_answers)

        if len(vals_to_insert) >= DB_INSERT_BATCH_SIZE:
            db_insert_user_answers(db, vals_to_insert)
            vals_to_insert = []

    if vals_to_insert:
        db_insert_user_answers(db, vals_to_insert)

    t1 = time.time()

    print(f"Elapsed time: {t1 - t0}s")
