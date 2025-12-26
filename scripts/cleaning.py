def deduplicate(df, key):
    """
    Garde, pour chaque valeur de `key`,
    l'observation la plus récente (publication_date),
    puis le plus grand doc-number en cas d'égalité.
    """
    # Trier selon la règle métier
    df_sorted = df.sort_values(
        by=[key, "publication_date", "doc-number"],
        ascending=[True, False, False]
    )

    # Garder la première occurrence par groupe
    df_dedup = df_sorted.drop_duplicates(
        subset=key,
        keep="first"
    )

    return df_dedup.sort_index()
