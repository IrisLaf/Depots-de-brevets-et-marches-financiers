import io
import os
import zipfile
import pandas as pd
import xml.etree.ElementTree as ET


def process_all_years_s3(fs, root_s3_path):
    """
    Parcourt tous les dossiers d'années dans un bucket S3
    et concatène les données extraites de chaque année.
    """
    all_data = []

    # Liste les sous-dossiers (par années)
    year_dirs = [p for p in fs.ls(root_s3_path) if fs.isdir(p)]
    for year_path in sorted(year_dirs):
        year_name = year_path.rstrip("/").split("/")[-1]
        print(f"📂 Traitement du dossier {year_name}...")
        df_year = process_year_folder_s3(fs, year_path)
        if not df_year.empty:
            df_year["year"] = year_name
            all_data.append(df_year)

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()


def process_year_folder_s3(fs, year_path):
    """
    Parcourt les fichiers ZIP dans un dossier S3 pour une année donnée.
    """
    all_brevets = []

    zip_files = [f for f in fs.ls(year_path) if f.lower().endswith(".zip")]
    for zip_s3_path in zip_files:
        zip_name = zip_s3_path.split("/")[-1]
        print(f"  🗜️ Traitement de {zip_name}...")
        df_zip = extract_from_zip_s3(fs, zip_s3_path)
        if not df_zip.empty:
            all_brevets.append(df_zip)

    if all_brevets:
        return pd.concat(all_brevets, ignore_index=True)
    else:
        return pd.DataFrame()


def extract_from_zip_s3(fs, zip_s3_path):
    """
    Ouvre un fichier ZIP stocké sur S3, lit uniquement les XML,
    et applique extract_brevet_info() à chacun.
    """
    all_brevets = []

    try:
        with fs.open(zip_s3_path, "rb") as f:
            zip_bytes = io.BytesIO(f.read())

        with zipfile.ZipFile(zip_bytes, "r") as archive:
            for file_name in archive.namelist():
                if file_name.lower().endswith(".xml"):
                    with archive.open(file_name) as xml_file:
                        xml_content = io.BytesIO(xml_file.read())
                        try:
                            df_brevet = extract_brevet_info(xml_content)
                            all_brevets.append(df_brevet)
                        except Exception as e:
                            print(f"    ⚠️ Erreur sur {file_name}: {e}")

    except Exception as e:
        print(f"    ❌ Erreur avec {zip_s3_path}: {e}")

    if all_brevets:
        return pd.concat(all_brevets, ignore_index=True)
    else:
        return pd.DataFrame()


def extract_brevet_info(xml_file_path):
    """
    Extrait les informations d'un fichier XML de brevet et retourne un DataFrame pandas
    avec toutes les sous-catégories décomposées en colonnes distinctes.

    Args:
        xml_file_path (str): Chemin vers le fichier XML.

    Returns:
        pd.DataFrame: DataFrame conteNAt toutes les informations extraites.
    """

    # Parse le fichier XML
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Initialisation des variables
    data = {}

    # Informations générales
    data["family_id"] = root.attrib.get("family-id", "NA")
    data["doc-number"] = root.attrib.get("doc-number", "NA")
    data["kind"] = root.attrib.get("kind", "NA")
    data["country"] = root.attrib.get("country", "NA")
    data["date-produced"] = root.attrib.get("date-produced", "NA")
    data["status"] = root.attrib.get("status", "NA")

    # Publication data
    publication_data = root.find(".//fr-publication-data/fr-publication-reference")
    if publication_data is not None:
        data["publication_country"] = publication_data.find(".//country").text \
            if publication_data.find(".//country") is not None else "NA"
        data["publication_doc-number"] = publication_data.find(".//doc-number").text \
            if publication_data.find(".//doc-number") is not None else "NA"
        data["publication_date"] = publication_data.find(".//date").text \
            if publication_data.find(".//date") is not None else "NA"
        data["publication_bopinum"] = publication_data.find(".//fr-bopinum").text \
            if publication_data.find(".//fr-bopinum") is not None else "NA"
        data["publication_nature"] = publication_data.find(".//fr-nature").text \
            if publication_data.find(".//fr-nature") is not None else "NA"

    # Application reference
    application_reference = root.find(".//fr-application-reference")
    if application_reference is not None:
        data["application_country"] = application_reference.find(".//country").text \
            if application_reference.find(".//country") is not None else "NA"
        data["application_doc-number"] = application_reference.find(".//doc-number").text \
            if application_reference.find(".//doc-number") is not None else "NA"
        data["application_date"] = application_reference.find(".//date").text \
            if application_reference.find(".//date") is not None else "NA"

    # Titre de l'invention
    data["invention-title"] = root.find(".//invention-title").text \
        if root.find(".//invention-title") is not None else "NA"

    # Déposants (applicants)
    max_entries = 3  # Nombre maximum d'entrées à considérer pour chaque catégorie
    for i in range(1, max_entries + 1):
        applicant = root.find(".//applicant[@sequence='{}']".format(i))
        if applicant is not None:
            orgname = applicant.find(".//orgname")
            if orgname is not None:
                data[f"applicant_{i}_orgname"] = orgname.text
            else:
                last_name = applicant.find(".//last-name")
                first_name = applicant.find(".//first-name")
                full_name = f"{last_name.text} {first_name.text}" \
                    if last_name is not None and first_name is not None else "NA"
                data[f"applicant_{i}_orgname"] = full_name

            address = applicant.find(".//address")
            if address is not None:
                data[f"applicant_{i}_address-1"] = address.find(".//address-1").text \
                    if address.find(".//address-1") is not None else "NA"
                data[f"applicant_{i}_city"] = address.find(".//city").text \
                    if address.find(".//city") is not None else "NA"
                data[f"applicant_{i}_postcode"] = address.find(".//postcode").text \
                    if address.find(".//postcode") is not None else "NA"
                data[f"applicant_{i}_country"] = address.find(".//country").text \
                    if address.find(".//country") is not None else "NA"
        else:
            data[f"applicant_{i}_orgname"] = "NA"
            data[f"applicant_{i}_address-1"] = "NA"
            data[f"applicant_{i}_city"] = "NA"
            data[f"applicant_{i}_postcode"] = "NA"
            data[f"applicant_{i}_country"] = "NA"

    # Inventeurs (inventors)
    for i in range(1, max_entries + 1):
        inventor = root.find(".//inventor[@sequence='{}']".format(i))
        if inventor is not None:
            last_name = inventor.find(".//last-name")
            data[f"inventor_{i}_last-name"] = last_name.text \
                if last_name is not None else "NA"

            first_name = inventor.find(".//first-name")
            data[f"inventor_{i}_first-name"] = first_name.text \
                if first_name is not None else "NA"

            address = inventor.find(".//address")
            if address is not None:
                data[f"inventor_{i}_address-1"] = address.find(".//address-1").text \
                    if address.find(".//address-1") is not None else "NA"
                data[f"inventor_{i}_city"] = address.find(".//city").text \
                    if address.find(".//city") is not None else "NA"
                data[f"inventor_{i}_postcode"] = address.find(".//postcode").text \
                    if address.find(".//postcode") is not None else "NA"
                data[f"inventor_{i}_country"] = address.find(".//country").text \
                    if address.find(".//country") is not None else "NA"
        else:
            data[f"inventor_{i}_last-name"] = "NA"
            data[f"inventor_{i}_first-name"] = "NA"
            data[f"inventor_{i}_address-1"] = "NA"
            data[f"inventor_{i}_city"] = "NA"
            data[f"inventor_{i}_postcode"] = "NA"
            data[f"inventor_{i}_country"] = "NA"

    # Agents
    for i in range(1, max_entries + 1):
        agent = root.find(".//agent[@sequence='{}']".format(i))
        if agent is not None:
            orgname = agent.find(".//orgname")
            data[f"agent_{i}_orgname"] = orgname.text \
                if orgname is not None else "NA"

            address = agent.find(".//address")
            if address is not None:
                data[f"agent_{i}_address-1"] = address.find(".//address-1").text \
                    if address.find(".//address-1") is not None else "NA"
                data[f"agent_{i}_city"] = address.find(".//city").text \
                    if address.find(".//city") is not None else "NA"
                data[f"agent_{i}_postcode"] = address.find(".//postcode").text \
                    if address.find(".//postcode") is not None else "NA"
                data[f"agent_{i}_country"] = address.find(".//country").text \
                    if address.find(".//country") is not None else "NA"
        else:
            data[f"agent_{i}_orgname"] = "NA"
            data[f"agent_{i}_address-1"] = "NA"
            data[f"agent_{i}_city"] = "NA"
            data[f"agent_{i}_postcode"] = "NA"
            data[f"agent_{i}_country"] = "NA"

    # Propriétaires (owners)
    for i in range(1, max_entries + 1):
        owner = root.find(".//fr-owner[@sequence='{}']".format(i))
        if owner is not None:
            last_name = owner.find(".//last-name")
            data[f"owner_{i}_last-name"] = last_name.text \
                if last_name is not None else "NA"

            first_name = owner.find(".//first-name")
            data[f"owner_{i}_first-name"] = first_name.text \
                if first_name is not None else "NA"

            address = owner.find(".//address")
            if address is not None:
                data[f"owner_{i}_address-1"] = address.find(".//address-1").text \
                    if address.find(".//address-1") is not None else "NA"
                data[f"owner_{i}_city"] = address.find(".//city").text \
                    if address.find(".//city") is not None else "NA"
                data[f"owner_{i}_postcode"] = address.find(".//postcode").text \
                    if address.find(".//postcode") is not None else "NA"
                data[f"owner_{i}_country"] = address.find(".//country").text \
                    if address.find(".//country") is not None else "NA"
        else:
            data[f"owner_{i}_last-name"] = "NA"
            data[f"owner_{i}_first-name"] = "NA"
            data[f"owner_{i}_address-1"] = "NA"
            data[f"owner_{i}_city"] = "NA"
            data[f"owner_{i}_postcode"] = "NA"
            data[f"owner_{i}_country"] = "NA"

    # Classifications CIB (IPC)
    for i in range(1, max_entries + 1):
        classification = root.find(".//classification-ipcr[@sequence='{}']".format(i))
        if classification is not None:
            data[f"classification_{i}_text"] = classification.find(".//text").text \
                if classification.find(".//text") is not None else "NA"
        else:
            data[f"classification_{i}_text"] = "NA"

    # Résumé (abstract)
    abstract = root.find(".//abstract/p")
    data["abstract"] = abstract.text if abstract is not None else "NA"

    # Références citées (citations)
    for i in range(1, max_entries + 1):
        citation = root.find(".//citation[{}]".format(i))
        if citation is not None:
            patcit = citation.find(".//patcit")
            if patcit is not None:
                data[f"citation_{i}_type"] = "patcit"
                data[f"citation_{i}_text"] = patcit.find(".//text").text \
                    if patcit.find(".//text") is not None else "NA"
                document_id = patcit.find(".//document-id")
                if document_id is not None:
                    data[f"citation_{i}_country"] = document_id.find(".//country").text \
                        if document_id.find(".//country") is not None else "NA"
                    data[f"citation_{i}_doc-number"] = document_id.find(".//doc-number").text \
                        if document_id.find(".//doc-number") is not None else "NA"
                    data[f"citation_{i}_date"] = document_id.find(".//date").text \
                        if document_id.find(".//date") is not None else "NA"
            else:
                nplcit = citation.find(".//nplcit")
                if nplcit is not None:
                    data[f"citation_{i}_type"] = "nplcit"
                    data[f"citation_{i}_text"] = nplcit.find(".//text").text \
                        if nplcit.find(".//text") is not None else "NA"
                else:
                    data[f"citation_{i}_type"] = "NA"
                    data[f"citation_{i}_text"] = "NA"
                    data[f"citation_{i}_country"] = "NA"
                    data[f"citation_{i}_doc-number"] = "NA"
                    data[f"citation_{i}_date"] = "NA"
        else:
            data[f"citation_{i}_type"] = "NA"
            data[f"citation_{i}_text"] = "NA"
            data[f"citation_{i}_country"] = "NA"
            data[f"citation_{i}_doc-number"] = "NA"
            data[f"citation_{i}_date"] = "NA"

    # Dates de disponibilité
    date_availability = root.find(".//fr-date-availability")
    if date_availability is not None:
        data["last-fee-payement"] = date_availability.find(".//fr-last-fee-payement/date").text \
            if date_availability.find(".//fr-last-fee-payement/date") is not None else "NA"
        data["next-fee-payement"] = date_availability.find(".//fr-next-fee-payement/date").text \
            if date_availability.find(".//fr-next-fee-payement/date") is not None else "NA"
        data["date-search-completed"] = \
            date_availability.find(".//fr-date-search-completed/date").text \
            if date_availability.find(".//fr-date-search-completed/date") is not None else "NA"

    # Convertir en DataFrame
    df = pd.DataFrame([data])

    return df


def extract_all_brevets_info(dossier_xml):
    """
    Extrait les informations de tous les fichiers XML d'un dossier.

    Args:
        dossier_xml (str): Chemin vers le dossier contenant les fichiers XML.

    Returns:
        pd.DataFrame: DataFrame avec les infos des fichiers XML.
    """

    # Liste pour stocker les DataFrames de chaque fichier XML
    all_brevets = []

    # Parcourir chaque fichier XML dans le dossier
    for fichier_xml in os.listdir(dossier_xml):
        if fichier_xml.endswith(".xml"):
            chemin_fichier_xml = os.path.join(dossier_xml, fichier_xml)
            try:
                df_brevet = extract_brevet_info(chemin_fichier_xml)
                all_brevets.append(df_brevet)
            except Exception as e:
                print(f"Erreur lors du traitement du fichier {fichier_xml}: {e}")

    # Concaténer tous les DataFrames en un seul
    if all_brevets:
        df_all_brevets = pd.concat(all_brevets, ignore_index=True)
        return df_all_brevets
    else:
        return pd.DataFrame()
