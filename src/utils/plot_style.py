"""Style matplotlib commun aux figures du rapport."""
import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from src.utils.config import ROOT

BG = "#050505"
TEXT = "#F6EFE9"
MUTED = "#A39690"
BORDER = "#2E2825"
GOLD = "#F7C340"
COLORS = {-1: "#F04438", 0: "#A39690", 1: "#12B76A"}
DISPLAY_NAMES = {-1: "Négatif", 0: "Neutre", 1: "Positif"}
GOLD_MAP = LinearSegmentedColormap.from_list("gold", ["#0F0D0C", "#7A5C14", GOLD])


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
