from db_connect import session
from db_tables import DrugsGkb, EmaTable


def get_drugs():
    """Obtener una lista de todos los fármacos en la EMA y PharmGKB a partir de la base de datos.
    Devuelve una lista de nombres de medicamentos únicos."""
    all_drugs = []
    # EMA
    drugs_ema1 = session.query(EmaTable.medicine_name_ema).all()
    drugs_ema2 = session.query(EmaTable.active_substance_ema).all()
    for record1, record2 in zip(drugs_ema1, drugs_ema2):
        all_drugs.append(record1[0].casefold())
        all_drugs.append(record2[0].casefold())

    # PharmGKB
    drugs_gkb1 = session.query(DrugsGkb.name_gkb).all()
    drugs_gkb2 = session.query(DrugsGkb.generic_name_gkb).all()
    drugs_gkb3 = session.query(DrugsGkb.trade_name_gkb).all()
    for record1, record2, record3 in zip(drugs_gkb1, drugs_gkb2, drugs_gkb3):
        if record1[0] is not None:
            all_drugs.append(record1[0].casefold())
        if record2[0] is not None:
            all_drugs.append(record2[0].casefold())
        if record3[0] is not None:
            all_drugs.append(record3[0].casefold())

    all_drugs_final = list(set(all_drugs))
    return all_drugs_final
