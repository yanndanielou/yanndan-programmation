import csv
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum


@dataclass
class Segment:
    """
    Représente un segment de ligne ferroviaire.

    Attributs:
        segment_id: Identifiant unique du segment (ex: SEG_010201)
        num_segment: Numéro du segment (ex: 8321)
        direction: Direction du segment (UP ou DOWN)
        pk_abs_start: Point kilométrique absolu de début (ex: 374.213)
        pk_abs_end: Point kilométrique absolu de fin (ex: 506.825)
        length: Longueur du segment en mètres (ex: 13261)
    """

    segment_id: str
    num_segment: int
    direction: str
    pk_abs_start: float
    pk_abs_end: float
    length: float

    @classmethod
    def load_from_csv(cls, csv_file_path: str | Path) -> List["Segment"]:
        """
        Charge une liste de segments depuis un fichier CSV.

        Args:
            csv_file_path: Chemin vers le fichier CSV

        Returns:
            Liste des objets Segment

        Format du CSV:
            SEGMENT_ID;NUM_SEGMENT;DIRECTION;PK_ABS_START;PK_ABS_END;LENGTH
        """
        segments = []
        csv_path = Path(csv_file_path)

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")

            for row in reader:
                segment = cls(
                    segment_id=row["SEGMENT_ID"],
                    num_segment=int(row["NUM_SEGMENT"]),
                    direction=row["DIRECTION"],
                    pk_abs_start=float(row["PK_ABS_START"]),
                    pk_abs_end=float(row["PK_ABS_END"]),
                    length=float(row["LENGTH"]),
                )
                segments.append(segment)

        return segments


class Line:
    """
    Représente une ligne ferroviaire contenant une collection de segments.

    Attributs:
        segments: Liste des segments de la ligne
    """

    def __init__(self, segments: List[Segment] = None):
        """
        Initialise une ligne avec des segments.

        Args:
            segments: Liste des objets Segment (par défaut liste vide)
        """
        self.segments = segments or []

    def __repr__(self) -> str:
        return f"Line(segments={len(self.segments)})"

    def __len__(self) -> int:
        return len(self.segments)

    def add_segment(self, segment: Segment) -> None:
        """Ajoute un segment à la ligne."""
        self.segments.append(segment)

    def search_by_segment_id(self, segment_id: str) -> Segment | None:
        """
        Recherche un segment par son identifiant.

        Args:
            segment_id: L'identifiant du segment (ex: SEG_010201)

        Returns:
            L'objet Segment trouvé ou None
        """
        for segment in self.segments:
            if segment.segment_id == segment_id:
                return segment
        return None

    def search_by_num_segment(self, num_segment: int) -> List[Segment]:
        """
        Recherche tous les segments par leur numéro.

        Args:
            num_segment: Le numéro du segment (ex: 8321)

        Returns:
            Liste des segments trouvés
        """
        return [seg for seg in self.segments if seg.num_segment == num_segment]

    @classmethod
    def load_from_csv(cls, csv_file_path: str | Path) -> "Line":
        """
        Crée une ligne avec tous les segments chargés depuis un fichier CSV.

        Args:
            csv_file_path: Chemin vers le fichier CSV

        Returns:
            Objet Line contenant tous les segments
        """
        segments = Segment.load_from_csv(csv_file_path)
        return cls(segments)


class Direction(str, Enum):
    """Énumération des directions possibles."""

    UP = "UP"
    DOWN = "DOWN"


@dataclass
class TrackingCircuit:
    """
    Représente un circuit de detection d'occupation de voie ferrée.

    Attributs:
        id: Identifiant unique du circuit (ex: CDV_z124Nord)
        label: Libellé du circuit (ex: 124Nord)
        occupancy_id: Identifiant du capteur d'occupation
        direction_id: Identifiant de la direction (optionnel)
        default_direction: Direction par défaut (UP ou DOWN)
        zone_failure_id: Identifiant de zone de défaillance
        failure_id: Identifiant de défaillance
        turnback: Indicateur de retour à la ligne (bool)
        steering: Direction de pilotage (UP, DOWN, ou None)
        extension_id: Identifiant d'extension (optionnel)
        representation: Représentation (optionnel)
        authorized_acknowledgement_rights: Droits d'acquittement autorisés (optionnel)
        denied_acknowledgement_rights: Droits d'acquittement refusés (optionnel)
        virtual: Indicateur de circuit virtuel (bool)
    """

    id: str
    label: str
    occupancy_id: str
    direction_id: Optional[str]
    default_direction: Direction
    zone_failure_id: str
    failure_id: str
    turnback: bool
    steering: Optional[Direction]
    extension_id: Optional[str]
    representation: Optional[str]
    authorized_acknowledgement_rights: Optional[str]
    denied_acknowledgement_rights: Optional[str]
    virtual: bool

    @classmethod
    def load_from_csv(cls, csv_file_path: str | Path) -> List["TrackingCircuit"]:
        """
        Charge une liste de circuits de detection depuis un fichier CSV.

        Args:
            csv_file_path: Chemin vers le fichier CSV

        Returns:
            Liste des objets TrackingCircuit

        Format du CSV:
            ID;LABEL;OCCUPANCY_ID;DIRECTION_ID;DEFAULT_DIRECTION;ZONE_FAILURE_ID;FAILURE_ID;TURNBACK;STEERING;EXTENSION_ID;REPRESENTATION;AUTHORIZED_ACKNOWLEDGEMENT_RIGHTS;DENIED_ACKNOWLEDGEMENT_RIGHTS;VIRTUAL
        """
        circuits = []
        csv_path = Path(csv_file_path)

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")

            for row in reader:
                # Fonction helper pour convertir les valeurs vides en None
                def to_none(value: str) -> Optional[str]:
                    return None if value.strip() == "" else value.strip()

                # Fonction helper pour convertir en bool (0=False, 1=True)
                def to_bool(value: str) -> bool:
                    return value.strip() == "1"

                # Fonction helper pour convertir en Direction optionnelle
                def to_direction(value: str) -> Optional[Direction]:
                    val = to_none(value)
                    return Direction(val) if val else None

                circuit = cls(
                    id=row["ID"],
                    label=row["LABEL"],
                    occupancy_id=row["OCCUPANCY_ID"],
                    direction_id=to_none(row["DIRECTION_ID"]),
                    default_direction=Direction(row["DEFAULT_DIRECTION"]),
                    zone_failure_id=row["ZONE_FAILURE_ID"],
                    failure_id=row["FAILURE_ID"],
                    turnback=to_bool(row["TURNBACK"]),
                    steering=to_direction(row["STEERING"]),
                    extension_id=to_none(row["EXTENSION_ID"]),
                    representation=to_none(row["REPRESENTATION"]),
                    authorized_acknowledgement_rights=to_none(row["AUTHORIZED_ACKNOWLEDGEMENT_RIGHTS"]),
                    denied_acknowledgement_rights=to_none(row["DENIED_ACKNOWLEDGEMENT_RIGHTS"]),
                    virtual=to_bool(row["VIRTUAL"]),
                )
                circuits.append(circuit)

        return circuits
