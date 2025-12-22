def plot_top_classifications(df, n=5):
    top_classes = (
        df.groupby("classification")["nombre"]
        .sum()
        .sort_values(ascending=False)
        .head(n)
        .index
    )

    df_top = df[df["classification"].isin(top_classes)]

    plt.figure()
    for c in top_classes:
        data = df_top[df_top["classification"] == c].sort_values("year")
        plt.plot(data["year"], data["nombre"], marker="o", label=c)

    plt.xlabel("Année")
    plt.ylabel("Nombre de brevets")
    plt.title(f"Évolution des {n} principales classifications")
    plt.ylim(bottom=0)
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_evolution_classification(df, classification):
    data = df[df["classification"] == classification].sort_values("year")

    plt.figure()
    plt.plot(data["year"], data["nombre"], marker="o")
    plt.xlabel("Année")
    plt.ylabel("Nombre de brevets")
    plt.title(f"Évolution des brevets – {classification}")
    plt.ylim(bottom=0)
    plt.grid(True)
    plt.show()

def plot_part_classification_par_annee(df):
    # 1. Calcul des parts (%) par année
    df_parts = df.copy()
    total_par_annee = df_parts.groupby("year")["nombre"].transform("sum")
    df_parts["part"] = df_parts["nombre"] / total_par_annee

    # 2. Passage au format large pour le graphique empilé
    table = (
        df_parts
        .pivot(index="year", columns="classification", values="part")
        .fillna(0)
        .sort_index()
    )

    # 3. Graphique en barres empilées
    plt.figure()
    bottom = pd.Series(0, index=table.index)

    for classification in table.columns:
        plt.bar(
            table.index,
            table[classification],
            bottom=bottom,
            label=classification
        )
        bottom += table[classification]

    plt.xlabel("Année")
    plt.ylabel("Part des brevets")
    plt.title("Répartition des brevets par catégorie de classification")
    plt.legend(title="Classification", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.ylim(0, 1.1)
    plt.tight_layout()
    plt.show()

