from db_connect import Base
from sqlalchemy import Column, Integer, String


# Definir las tablas y el tipo de datos (cada clase = una tabla, cada atributo = una columna)
class Drugscima(Base):
    __tablename__ = 'DRUGS_CIMA'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nregistro = Column(Integer)
    nombre_esp = Column(String)
    laboratorio = Column(String)
    estado = Column(String)
    atc_cima = Column(String)
    principio_activos_cima = Column(String)
    comercializado = Column(String)
    triangulo_amarillo = Column(String)
    observaciones_cima = Column(String)
    afecta_conduccion = Column(String)
    problemas_suministro = Column(String)

    def __init__(self, nregistro, nombre_esp, laboratorio, estado, atc_cima, principio_activos_cima,
                 comercializado, triangulo_amarillo, observaciones_cima, afecta_conduccion, problemas_suministro):
        self.nregistro = nregistro
        self.nombre_esp = nombre_esp
        self.laboratorio = laboratorio
        self.estado = estado
        self.atc_cima = atc_cima
        self.principio_activos_cima = principio_activos_cima
        self.comercializado = comercializado
        self.triangulo_amarillo = triangulo_amarillo
        self.observaciones_cima = observaciones_cima
        self.afecta_conduccion = afecta_conduccion
        self.problemas_suministro = problemas_suministro


class PanelGeneticoEsp(Base):
    __tablename__ = 'PanelGeneticoEsp'
    id = Column(Integer, primary_key=True, autoincrement=True)
    patologia_esp = Column(String)
    gen_esp = Column(String)
    farmaco_esp = Column(String)
    observaciones_esp = Column(String)

    def __init__(self, patologia_esp, gen_esp, farmaco_esp, observaciones_esp):
        self.patologia_esp = patologia_esp
        self.gen_esp = gen_esp
        self.farmaco_esp = farmaco_esp
        self.observaciones_esp = observaciones_esp


class EmaTable(Base):
    __tablename__ = 'EMA_table'
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_ema = Column(String)
    medicine_name_ema = Column(String)
    therapeutic_area = Column(String)
    inn_common_name_ema = Column(String)
    active_substance_ema = Column(String)
    authorisation_status_ema = Column(String)
    atc_code_ema = Column(String)
    condition_indication_ema = Column(String)
    url_ema = Column(String)

    def __init__(self, category_ema, medicine_name_ema, therapeutic_area, inn_common_name_ema, active_substance_ema,
                 authorisation_status_ema, atc_code_ema, condition_indication_ema, url_ema):
        self.category_ema = category_ema
        self.medicine_name_ema = medicine_name_ema
        self.therapeutic_area = therapeutic_area
        self.inn_common_name_ema = inn_common_name_ema
        self.active_substance_ema = active_substance_ema
        self.authorisation_status_ema = authorisation_status_ema
        self.atc_code_ema = atc_code_ema
        self.condition_indication_ema = condition_indication_ema
        self.url_ema = url_ema


class DrugsGkb(Base):
    __tablename__ = 'drugs_GKB'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_drug = Column(Integer)
    name_gkb = Column(String)
    generic_name_gkb = Column(String)
    trade_name_gkb = Column(String)
    external_voc_gkb = Column(String)
    rxnorm_identifiers_gkb = Column(String)
    atc_identifiers_gkb = Column(String)
    def __init__(self, id_drug, name_gkb, generic_name_gkb, trade_name_gkb, external_voc_gkb, rxnorm_identifiers_gkb,
                 atc_identifiers_gkb):
        self.id_drug = id_drug
        self.name_gkb = name_gkb
        self.generic_name_gkb = generic_name_gkb
        self.trade_name_gkb = trade_name_gkb
        self.external_voc_gkb = external_voc_gkb
        self.rxnorm_identifiers_gkb = rxnorm_identifiers_gkb
        self.atc_identifiers_gkb = atc_identifiers_gkb


class ClinicalAnnGkb(Base):
    __tablename__ = 'clinical_ann_GKB'
    id = Column(Integer, primary_key=True, autoincrement=True)
    clinical_annotation_id_var = Column(Integer)
    variant_haplotypes = Column(String)
    gene_clinann_gkb = Column(String)
    level_of_evidence = Column(String)
    phenotype_category = Column(String)
    drug_clinann_gkb = Column(String)
    phenotypes_clinann_gkb = Column(String)
    url_clinann_gkb = Column(String)

    def __init__(self, clinical_annotation_id_var, variant_haplotypes, gene_clinann_gkb, level_of_evidence,
                 phenotype_category, drug_clinann_gkb, phenotypes_clinann_gkb, url_clinann_gkb):
        self.clinical_annotation_id_var = clinical_annotation_id_var
        self.variant_haplotypes = variant_haplotypes
        self.gene_clinann_gkb = gene_clinann_gkb
        self.level_of_evidence = level_of_evidence
        self.phenotype_category = phenotype_category
        self.drug_clinann_gkb = drug_clinann_gkb
        self.phenotypes_clinann_gkb = phenotypes_clinann_gkb
        self.url_clinann_gkb = url_clinann_gkb


class ClinicalAnnAlleles(Base):
    __tablename__ = 'clinical_ann_alleles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    clinical_annotation_id_alleles = Column(Integer)
    genotype_alleles = Column(String)
    annotation_text_alleles = Column(String)
    allele_function = Column(String)

    def __init__(self, clinical_annotation_id_alleles, genotype_alleles, annotation_text_alleles, allele_function):
        self.clinical_annotation_id_alleles = clinical_annotation_id_alleles
        self.genotype_alleles = genotype_alleles
        self.annotation_text_alleles = annotation_text_alleles
        self.allele_function = allele_function


class DrugsLabelGkb(Base):
    __tablename__ = 'drugsLabel_GKB'
    id = Column(Integer, primary_key=True, autoincrement=True)
    pharmgkb_id_label = Column(Integer)
    name_label = Column(String)
    source_label = Column(String)
    biomarker_flag_label = Column(String)
    testing_level_label = Column(String)
    prescribing_info_label = Column(String)
    dosing_info_label = Column(String)
    alternate_drug_label = Column(String)
    other_prescribing_guidance_label = Column(String)
    cancer_genome = Column(String)
    prescribing_label = Column(String)
    chemicals_label = Column(String)
    genes_label = Column(String)
    variants_haplotypes_label = Column(String)

    def __init__(self, pharmgkb_id_label, name_label, source_label, biomarker_flag_label, testing_level_label,
                 prescribing_info_abel, dosing_info_label, alternate_drug_label, other_prescribing_guidance_label,
                 cancer_genome, prescribing_label, chemicals_label, genes_label, variants_haplotypes_label):
        self.pharmgkb_id_label = pharmgkb_id_label
        self.name_label = name_label
        self.source_label = source_label
        self.biomarker_flag_label = biomarker_flag_label
        self.testing_level_label = testing_level_label
        self.prescribing_info_label = prescribing_info_abel
        self.dosing_info_label = dosing_info_label
        self.alternate_drug_label = alternate_drug_label
        self.other_prescribing_guidance_label = other_prescribing_guidance_label
        self.cancer_genome = cancer_genome
        self.prescribing_label = prescribing_label
        self.chemicals_label = chemicals_label
        self.genes_label = genes_label
        self.variants_haplotypes_label = variants_haplotypes_label


class RelationshipsGkb(Base):
    __tablename__ = 'relationships_GKB'
    id = Column(Integer, primary_key=True, autoincrement=True)
    entity1_id = Column(Integer)
    entity1_name = Column(String)
    entity1_type = Column(String)
    entity2_id = Column(Integer)
    entity2_name = Column(String)
    entity2_type = Column(String)
    evidence_relationship = Column(String)
    association_relationships = Column(String)
    pk = Column(String)
    pd = Column(String)
    pmids = Column(String)

    def __init__(self, entity1_id, entity1_name, entity1_type, entity2_id, entity2_name, entity2_type,
                 evidence_relationship, association_relationships, pk, pd, pmids):
        self.entity1_id = entity1_id
        self.entity1_name = entity1_name
        self.entity1_type = entity1_type
        self.entity2_id = entity2_id
        self.entity2_name = entity2_name
        self.entity2_type = entity2_type
        self.evidence_relationship = evidence_relationship
        self.association_relationships = association_relationships
        self.pk = pk
        self.pd = pd
        self.pmids = pmids


class VariantAnnotations(Base):
    __tablename__ = 'variant_annotations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    variant_annotation_id = Column(Integer)
    variant_haplotypes = Column(String)
    genes_varann = Column(String)
    drugs_varann = Column(String)
    phenotype_category_varann = Column(String)
    variant_annotation_sentence = Column(String)

    def __init__(self, variant_annotation_id, variant_haplotypes, genes_varann, drugs_varann, phenotype_category_varann,
                 variant_annotation_sentence):
        self.variant_annotation_id = variant_annotation_id
        self.variant_haplotypes = variant_haplotypes
        self.genes_varann = genes_varann
        self.drugs_varann = drugs_varann
        self.phenotype_category_varann = phenotype_category_varann
        self.variant_annotation_sentence = variant_annotation_sentence


class PhenoAnnotations(Base):
    __tablename__ = 'pheno_annotations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    variant_annotation_id_pheno = Column(Integer)
    variant_haplotypes_pheno = Column(String)
    gene_pheno = Column(String)
    drugs_pheno = Column(String)
    phenotype_category_pheno = Column(String)
    significance_pheno = Column(String)
    phenotype_annotation_sentence = Column(String)
    metabolizer_types_pheno = Column(String)

    def __init__(self, variant_annotation_id_pheno, variant_haplotypes_pheno, gene_pheno, drugs_pheno,
                 phenotype_category_pheno, significance_pheno, phenotype_annotation_sentence,
                 metabolizer_types_pheno):
        self.variant_annotation_id_pheno = variant_annotation_id_pheno
        self.variant_haplotypes_pheno = variant_haplotypes_pheno
        self.gene_pheno = gene_pheno
        self.drugs_pheno = drugs_pheno
        self.phenotype_category_pheno = phenotype_category_pheno
        self.significance_pheno = significance_pheno
        self.phenotype_annotation_sentence = phenotype_annotation_sentence
        self.metabolizer_types_pheno = metabolizer_types_pheno


class DrugDrugInteractions(Base):
    __tablename__ = 'D-D Interactions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    drug_1 = Column(String)
    drug_2 = Column(String)
    level_ddi = Column(String)

    def __init__(self, drug_1, drug_2, level_ddi):
        self.drug_1 = drug_1
        self.drug_2 = drug_2
        self.level_ddi = level_ddi
