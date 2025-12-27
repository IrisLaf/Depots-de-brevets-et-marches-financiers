import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_top_classifications(df, n=5):
    top_classes = (
        df.groupby("classification")["nombre"]
        .sum()
        .sort_values(ascending=False)
        .head(n)
        .index
    )

    df_top = df[df["classification"].isin(top_classes)]

    colors = sns.color_palette("Set2", n_colors=len(top_classes))

    plt.figure()
    for (c, color) in zip(top_classes, colors):
        data = df_top[df_top["classification"] == c].sort_values("year")
        plt.plot(
            data["year"],
            data["nombre"],
            marker="o",
            label=c,
            color=color
        )

    plt.xlabel("Année")
    plt.ylabel("Nombre de brevets")
    plt.title(f"Évolution des {n} principales classifications")
    plt.ylim(bottom=0)
    plt.legend(
        title="Classification",
        bbox_to_anchor=(1.05, 1),
        loc="upper left"
    )
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_part_classification_par_annee(df):
    df_parts = df.copy()
    total_par_annee = df_parts.groupby("year")["nombre"].transform("sum")
    df_parts["part"] = df_parts["nombre"] / total_par_annee

    table = (
        df_parts
        .pivot(index="year", columns="classification", values="part")
        .fillna(0)
        .sort_index()
    )

    colors = sns.color_palette("Set2", n_colors=table.shape[1])

    plt.figure()
    bottom = pd.Series(0, index=table.index)

    for (classification, color) in zip(table.columns, colors):
        plt.bar(
            table.index,
            table[classification],
            bottom=bottom,
            label=classification,
            color=color
        )
        bottom += table[classification]

    plt.xlabel("Année")
    plt.ylabel("Part des brevets")
    plt.title("Répartition des brevets par catégorie de classification")
    plt.legend(
        title="Classification",
        bbox_to_anchor=(1.05, 1),
        loc="upper left"
    )
    plt.ylim(0, 1.1)
    plt.tight_layout()
    plt.show()
