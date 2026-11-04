"""Style matplotlib commun aux figures du rapport."""
import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from src.utils.config import ROOT

BG = "#FFFFFF"
TEXT = "#120D02"
MUTED = "#5C5048"
BORDER = "#D6C9BF"
GOLD = "#F7C340"
COLORS = {-1: "#D92D20", 0: "#8A7F78", 1: "#039855"}
DISPLAY_NAMES = {-1: "Négatif", 0: "Neutre", 1: "Positif"}
GOLD_MAP = LinearSegmentedColormap.from_list("gold", ["#FFFFFF", "#FBE1A0", GOLD])


def apply_style() -> None:
    for path in (ROOT / "assets" / "fonts").glob("*.ttf"):
        font_manager.fontManager.addfont(path)
    plt.rcParams.update({
        "figure.facecolor": BG,
        "savefig.facecolor": BG,
        "axes.facecolor": BG,
        "axes.edgecolor": BORDER,
        "axes.labelcolor": MUTED,
        "axes.titlecolor": TEXT,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": False,
        "text.color": TEXT,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "font.family": "Outfit Thin",  # Nom interne de la graisse normale de ce fichier.
        "axes.titlesize": 16,
        "axes.titlelocation": "left",
        "legend.frameon": False,
    })


def set_title(ax, title: str) -> None:
    ax.set_title(title.upper(), fontfamily="Anton", pad=12)
