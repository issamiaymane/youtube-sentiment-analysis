"""Génère les icônes de l'extension (trois barres or foncé sur fond blanc) en PNG, sans dépendance graphique."""
import struct
import zlib
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "chrome-extension" / "icons"


def png(size: int) -> bytes:
    rows = []
    for y in range(size):
        row = bytearray([0])
        for x in range(size):
            u, v = (x + 0.5) / size, (y + 0.5) / size
            radius = 0.2
            dx = max(radius - u, u - (1 - radius), 0)
            dy = max(radius - v, v - (1 - radius), 0)
            inside = dx * dx + dy * dy <= radius * radius
            bar = any(
                left <= u <= left + 0.16 and top <= v <= 0.76
                for left, top in ((0.2, 0.52), (0.42, 0.38), (0.64, 0.24))
            )
            if not inside:
                row += bytes((0, 0, 0, 0))
            elif bar:
                row += bytes((138, 101, 8, 255))
            else:
                row += bytes((255, 255, 255, 255))
        rows.append(bytes(row))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))

    header = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(b"".join(rows)))
        + chunk(b"IEND", b"")
    )


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for size in (16, 48, 128):
        (OUT / f"icon{size}.png").write_bytes(png(size))
