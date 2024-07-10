from db_connect import session
from db_tables import Drugscima, ClinicalAnnAlleles, ClinicalAnnGkb, DrugDrugInteractions

# Funciones para la página de inicio


def estadisticas():
    """Obtener estadísticas de la base de datos"""
    num_farmacos = session.query(Drugscima).count()
    num_clinical_ann = session.query(ClinicalAnnGkb).count()
    clinical_1a = session.query(ClinicalAnnGkb).filter(ClinicalAnnGkb.level_of_evidence == "1A").count()
    clinical_1b = session.query(ClinicalAnnGkb).filter(ClinicalAnnGkb.level_of_evidence == "1B").count()
    clinical_2a = session.query(ClinicalAnnGkb).filter(ClinicalAnnGkb.level_of_evidence == "2A").count()
    clinical_2b = session.query(ClinicalAnnGkb).filter(ClinicalAnnGkb.level_of_evidence == "2B").count()
    clinical_3 = session.query(ClinicalAnnGkb).filter(ClinicalAnnGkb.level_of_evidence == "3").count()
    clinical_4 = session.query(ClinicalAnnGkb).filter(ClinicalAnnGkb.level_of_evidence == "4").count()
    num_ddi = session.query(DrugDrugInteractions).count()
    major = session.query(DrugDrugInteractions).filter(DrugDrugInteractions.level_ddi == "Major").count()
    moderate = session.query(DrugDrugInteractions).filter(DrugDrugInteractions.level_ddi == "Moderate").count()
    minor = session.query(DrugDrugInteractions).filter(DrugDrugInteractions.level_ddi == "Minor").count()
    unkown = session.query(DrugDrugInteractions).filter(DrugDrugInteractions.level_ddi == "Unknown").count()
    alle_ann = session.query(ClinicalAnnAlleles).count()
    return (num_farmacos, num_clinical_ann, clinical_1a, clinical_1b, clinical_2a, clinical_2b, clinical_3, clinical_4,
            num_ddi, major, moderate, minor, unkown, alle_ann)


def circle(pos, data, title):
    """Crea circulos"""
    circle_style = """
        width: 200px;
        height: 200px;
        border-radius: 80%;
        background-color: #ffffff;
        border: 15px solid hsl(210, 50%, 90%);
        display: flex;
        justify-content: center;
        align-items: center;
        margin:  75px auto 5px;
    """
    title_style = f"""
        color: #3498db;
        font-size: 18px;
        text-align: left;
        margin-top: -270px;
        margin-left: {pos}px;
        font-weight: bold;  
    """
    circle_html = f"""
        <div style="text-align: right;">
            <div style="{circle_style}">
                <span style="color: #3498db; font-size: 45px;">{data}</span>
            </div>
            <div style="{title_style}">{title}</div>
        </div>
    """
    return circle_html
