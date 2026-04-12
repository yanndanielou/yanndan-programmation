from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass, field
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


@dataclass
class Line:
    """
    Représente une ligne ferroviaire complète avec tous ses composants.

    Attributs:
        segments: Liste des segments de la ligne
        tracking_circuits: Dict des circuits de détection par ID
        tracking_blocks: Dict des blocs de détection par ID
    """

    segments: List[Segment]
    tracking_circuits: Dict[str, TrackingCircuit]
    tracking_blocks: Dict[str, TrackingBlock]
    not_created_tracking_blocks_ids_without_track_circuits: List[str]

    def __repr__(self) -> str:
        return f"Line(segments={len(self.segments)}, " f"circuits={len(self.tracking_circuits)}, " f"blocks={len(self.tracking_blocks)})"

    def __len__(self) -> int:
        return len(self.segments)

    # ============ Segments ============
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

    # ============ Tracking Circuits ============
    def add_tracking_circuit(self, circuit: TrackingCircuit) -> None:
        """Ajoute un circuit de détection à la ligne."""
        self.tracking_circuits[circuit.id] = circuit

    def search_tracking_circuit_by_id(self, circuit_id: str) -> TrackingCircuit | None:
        """
        Recherche un circuit de détection par son identifiant.

        Args:
            circuit_id: L'identifiant du circuit (ex: CDV_z124Nord)

        Returns:
            L'objet TrackingCircuit trouvé ou None
        """
        return self.tracking_circuits.get(circuit_id)

    def search_tracking_circuits_by_label(self, label: str) -> List[TrackingCircuit]:
        """
        Recherche tous les circuits dont le libellé correspond.

        Args:
            label: Le libellé du circuit

        Returns:
            Liste des circuits trouvés
        """
        return [c for c in self.tracking_circuits.values() if c.label == label]

    # ============ Tracking Blocks ============
    def add_tracking_block(self, block: TrackingBlock) -> None:
        """Ajoute un bloc de détection à la ligne."""
        self.tracking_blocks[block.id] = block

    def search_tracking_block_by_id(self, block_id: str) -> TrackingBlock | None:
        """
        Recherche un bloc de détection par son identifiant.

        Args:
            block_id: L'identifiant du bloc

        Returns:
            L'objet TrackingBlock trouvé ou None
        """
        return self.tracking_blocks.get(block_id)

    def search_tracking_blocks_by_circuit(self, circuit_id: str) -> List[TrackingBlock]:
        """
        Recherche tous les blocs associés à un circuit de détection.

        Args:
            circuit_id: L'identifiant du circuit

        Returns:
            Liste des blocs trouvés
        """
        return [b for b in self.tracking_blocks.values() if b.track_circuit_id == circuit_id]

    @classmethod
    def load_from_csv(
        cls,
        segments_csv_full_path: str | Path,
        track_circuits_csv_full_path: str | Path,
        tracking_blocks_csv_full_path: str | Path,
        ignore_tracking_blocks_without_circuits: bool,
    ) -> "Line":
        """
        Crée une ligne complète en chargeant les données depuis des fichiers CSV.

        Args:
            segments_csv_full_path: Chemin vers le fichier CSV des segments
            track_circuits_csv_full_path: Chemin vers le fichier CSV des circuits
            tracking_blocks_csv_full_path: Chemin vers le fichier CSV des blocs
            ignore_tracking_blocks_without_circuits: Si True, ignore les blocs sans circuit.
                                                      Si False, lève une exception.

        Returns:
            Objet Line contenant tous les composants
        """
        # Charger les segments
        segments = Segment.load_from_csv(segments_csv_full_path)

        # Charger les circuits
        circuits_list = TrackingCircuit.load_from_csv(track_circuits_csv_full_path)
        circuits_dict = {c.id: c for c in circuits_list}

        # Charger les blocs avec associations aux circuits
        blocks_list, not_created_tracking_blocks_ids_without_track_circuits = TrackingBlock._load_from_csv_raw(
            tracking_blocks_csv_full_path,
            circuits_dict,
            ignore_tracking_blocks_without_circuits,
        )
        blocks_dict = {b.id: b for b in blocks_list}

        return cls(
            segments=segments,
            tracking_circuits=circuits_dict,
            tracking_blocks=blocks_dict,
            not_created_tracking_blocks_ids_without_track_circuits=not_created_tracking_blocks_ids_without_track_circuits,
        )


class Direction(str, Enum):
    """Énumération des directions possibles."""

    UP = "UP"
    DOWN = "DOWN"
    BOTH = "BOTH"


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
        tracking_blocks: Liste des blocs de détection associés à ce circuit
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
    tracking_blocks: List["TrackingBlock"] = field(default_factory=list)

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


@dataclass
class TrackingBlock:
    """
    Représente un bloc de détection (regroupement de circuits).

    Attributs:
        id: Identifiant unique du bloc (ex: TB_CDV_z124Nord_01)
        label: Libellé du bloc (optionnel)
        type: Type du bloc (optionnel)
        track_circuit_id: Identifiant du circuit de détection associé
        isotropic: Indicateur isotrope (bool)
        border: Indicateur de limite (bool)
        steering: Direction de pilotage (UP, DOWN, ou None)
        extension_id: Identifiant d'extension (optionnel)
        tracking_circuit: Référence vers le circuit de détection associé (obligatoire)
    """

    id: str
    label: Optional[str]
    type: Optional[str]
    track_circuit_id: str
    isotropic: bool
    border: bool
    steering: Optional[Direction]
    extension_id: Optional[str]
    tracking_circuit: TrackingCircuit

    @classmethod
    def _load_from_csv_raw(
        cls,
        csv_file_path: str | Path,
        circuits_dict: Dict[str, TrackingCircuit],
        ignore_tracking_blocks_without_circuits: bool = False,
    ) -> Tuple[List["TrackingBlock"], List[str]]:
        """
        Charge les blocs de détection depuis un fichier CSV et crée les objets TrackingBlock
        en établissant directement les associations avec les circuits.

        Args:
            csv_file_path: Chemin vers le fichier CSV
            circuits_dict: Dictionnaire des circuits par ID
            ignore_tracking_blocks_without_circuits: Si True, ignore les blocs dont le circuit n'existe pas.
                                                      Si False, lève une ValueError.

        Returns:
            Liste des objets TrackingBlock créés avec leurs associations aux circuits

        Format du CSV:
            ID;LABEL;TYPE;TRACK_CIRCUIT_ID;ISOTROPIC;BORDER;STEERING;EXTENSION_ID
        """
        blocks = []
        ignored_tracking_blocks_ids_because_no_track_circuit_defined = []
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

                block_id = row["ID"]
                circuit_id = row["TRACK_CIRCUIT_ID"]

                circuit = circuits_dict.get(circuit_id)

                # Gérer le cas où le circuit n'existe pas
                if not circuit:
                    if ignore_tracking_blocks_without_circuits:
                        ignored_tracking_blocks_ids_because_no_track_circuit_defined.append(block_id)
                        continue
                    else:
                        raise ValueError(f"Circuit '{circuit_id}' non trouvé pour le bloc '{block_id}'. " f"Chaque bloc doit référencer un circuit existant.")

                # Créer le bloc avec le circuit (obligatoire)
                block = cls(
                    id=block_id,
                    label=to_none(row["LABEL"]),
                    type=to_none(row["TYPE"]),
                    track_circuit_id=circuit_id,
                    isotropic=to_bool(row["ISOTROPIC"]),
                    border=to_bool(row["BORDER"]),
                    steering=to_direction(row["STEERING"]),
                    extension_id=to_none(row["EXTENSION_ID"]),
                    tracking_circuit=circuit,
                )
                blocks.append(block)

                # Ajouter le bloc à la liste du circuit
                circuit.tracking_blocks.append(block)

        if ignored_tracking_blocks_ids_because_no_track_circuit_defined:
            print(
                f"⚠️  {len(ignored_tracking_blocks_ids_because_no_track_circuit_defined)} bloc(s) ignoré(s) car leur circuit n'existe pas: "
                f"{', '.join(ignored_tracking_blocks_ids_because_no_track_circuit_defined)}"
            )

        return blocks, ignored_tracking_blocks_ids_because_no_track_circuit_defined

    @classmethod
    def load_from_csv(cls, csv_file_path: str | Path) -> List["TrackingBlock"]:
        """
        Charge une liste de blocs de détection depuis un fichier CSV.

        Note: Cette méthode est destinée à être utilisée via Line.load_from_csv()
        qui établit automatiquement les relations aux circuits.

        Args:
            csv_file_path: Chemin vers le fichier CSV

        Returns:
            Liste des objets TrackingBlock

        Format du CSV:
            ID;LABEL;TYPE;TRACK_CIRCUIT_ID;ISOTROPIC;BORDER;STEERING;EXTENSION_ID
        """
        # Cette méthode ne peut pas être utilisée seule car tracking_circuit est obligatoire
        raise NotImplementedError("Utilisez Line.load_from_csv() pour charger les blocs avec leurs circuits. " "TrackingBlock.tracking_circuit est obligatoire.")
