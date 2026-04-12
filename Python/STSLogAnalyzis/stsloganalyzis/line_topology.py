from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass, field
from enum import Enum

from logger import logger_config


@dataclass
class Segment:
    """
    Représente un segment de ligne ferroviaire.

    Attributs:
        identifier: Identifiant unique du segment (ex: SEG_010201)
        num_segment: Numéro du segment (ex: 8321)
        direction: Direction du segment (UP ou DOWN)
        pk_abs_start: Point kilométrique absolu de début (ex: 374.213)
        pk_abs_end: Point kilométrique absolu de fin (ex: 506.825)
        length: Longueur du segment en mètres (ex: 13261)
        upstream_normal: Segment amont normal (optionnel)
        upstream_reverse: Segment amont reverse (optionnel)
        downstream_normal: Segment aval normal (optionnel)
        downstream_reverse: Segment aval reverse (optionnel)
    """

    identifier: str
    num_segment: int
    direction: str
    pk_abs_start: float
    pk_abs_end: float
    length: float
    upstream_normal: Optional["Segment"] = None
    upstream_reverse: Optional["Segment"] = None
    downstream_normal: Optional["Segment"] = None
    downstream_reverse: Optional["Segment"] = None

    def __post_init__(self) -> None:
        assert self.identifier
        assert isinstance(self.identifier, str)

    @classmethod
    def load_from_csv(cls, csv_file_path: str | Path) -> List["Segment"]:
        """
        Charge une liste de segments depuis un fichier CSV.

        Args:
            csv_file_path: Chemin vers le fichier CSV

        Returns:
            Liste des objets Segment

        Format du CSV:
            identifier;NUM_SEGMENT;DIRECTION;PK_ABS_START;PK_ABS_END;LENGTH
        """
        segments = []
        csv_path = Path(csv_file_path)

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")

            for row in reader:
                segment = cls(
                    identifier=row["SEGMENT_ID"],
                    num_segment=int(row["NUM_SEGMENT"]),
                    direction=row["DIRECTION"],
                    pk_abs_start=float(row["PK_ABS_START"]),
                    pk_abs_end=float(row["PK_ABS_END"]),
                    length=float(row["LENGTH"]),
                )
                segments.append(segment)

        return segments

    @classmethod
    def load_topology_from_csv(
        cls,
        segments: List["Segment"],
        relations_csv_file_path: str | Path,
    ) -> None:
        """
        Établit la topologie entre les segments en chargeant les relations depuis un fichier CSV.

        Args:
            segments: Liste des segments existants
            relations_csv_file_path: Chemin vers le fichier CSV des relations

        Format du CSV:
            identifier;SEGMENT_AMONT_NORMAL_ID;SEGMENT_AMONT_REVERSE_ID;SEGMENT_AVAL_NORMAL_ID;SEGMENT_AVAL_REVERSE_ID

        Note: identifier et les autres colonnes sont des num_segment (int)
        """
        # Créer un dictionnaire des segments par num_segment
        segments_by_num = {seg.num_segment: seg for seg in segments}

        csv_path = Path(relations_csv_file_path)

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")

            for row in reader:
                # Fonction helper pour convertir les valeurs vides en None
                def to_int_or_none(value: str) -> Optional[int]:
                    val = value.strip()
                    return int(val) if val and val != "" else None

                current_num = to_int_or_none(row["SEGMENT_ID"])
                if current_num is None:
                    continue

                current_segment = segments_by_num.get(current_num)
                if not current_segment:
                    logger_config.print_and_log_warning(f"Segment avec num_segment {current_num} non trouvé dans la liste des segments.")
                    continue

                # Charger les relations
                upstream_normal_num = to_int_or_none(row["SEGMENT_AMONT_NORMAL_ID"])
                upstream_reverse_num = to_int_or_none(row["SEGMENT_AMONT_REVERSE_ID"])
                downstream_normal_num = to_int_or_none(row["SEGMENT_AVAL_NORMAL_ID"])
                downstream_reverse_num = to_int_or_none(row["SEGMENT_AVAL_REVERSE_ID"])

                # Établir les références
                if upstream_normal_num is not None:
                    current_segment.upstream_normal = segments_by_num.get(upstream_normal_num)
                    if current_segment.upstream_normal is None:
                        logger_config.print_and_log_warning(f"Segment amont normal {upstream_normal_num} non trouvé pour le segment {current_num}.")

                if upstream_reverse_num is not None:
                    current_segment.upstream_reverse = segments_by_num.get(upstream_reverse_num)
                    if current_segment.upstream_reverse is None:
                        logger_config.print_and_log_warning(f"Segment amont reverse {upstream_reverse_num} non trouvé pour le segment {current_num}.")

                if downstream_normal_num is not None:
                    current_segment.downstream_normal = segments_by_num.get(downstream_normal_num)
                    if current_segment.downstream_normal is None:
                        logger_config.print_and_log_warning(f"Segment aval normal {downstream_normal_num} non trouvé pour le segment {current_num}.")

                if downstream_reverse_num is not None:
                    current_segment.downstream_reverse = segments_by_num.get(downstream_reverse_num)
                    if current_segment.downstream_reverse is None:
                        logger_config.print_and_log_warning(f"Segment aval reverse {downstream_reverse_num} non trouvé pour le segment {current_num}.")


@dataclass
class Line:
    """
    Représente une ligne ferroviaire complète avec tous ses composants.
    """

    segments: List[Segment]
    track_circuits: List[TrackingCircuit]
    track_circuit_by_id: Dict[str, TrackingCircuit]
    tracking_blocks: List[TrackingBlock]
    switches: Dict[str, Switch]
    not_created_tracking_blocks_ids_without_track_circuits: List[str]
    tracking_block_on_segments: List[TrackingBlockOnSegment] = field(default_factory=list)
    tracking_block_on_segment_by_id: Dict[str, TrackingBlockOnSegment] = field(init=False)

    def __post_init__(self) -> None:
        self.tracking_block_by_id = {b.identifier: b for b in self.tracking_blocks}
        self.segment_by_id = {b.identifier: b for b in self.segments}
        self.segment_by_number = {b.num_segment: b for b in self.segments}
        self.tracking_block_on_segment_by_id = {rel.id: rel for rel in self.tracking_block_on_segments}

        logger_config.print_and_log_info(repr(self))

    def __repr__(self) -> str:
        return (
            f"Line(segments={len(self.segments)}, "
            f"circuits={len(self.track_circuit_by_id)}, "
            f"blocks={len(self.tracking_blocks)}, "
            f"block_relations={len(self.tracking_block_on_segments)}, "
            f"switches={len(self.switches)})"
        )

    def __len__(self) -> int:
        return len(self.segments)

    @classmethod
    def load_from_csv(
        cls,
        segments_csv_full_path: str | Path,
        segments_relations_csv_full_path: str | Path,
        track_circuits_csv_full_path: str | Path,
        tracking_blocks_csv_full_path: str | Path,
        switches_csv_full_path: str | Path,
        tracking_block_on_segments_csv_full_path: Optional[str | Path] = None,
        ignore_tracking_blocks_without_circuits: bool = False,
    ) -> "Line":
        """
        Crée une ligne complète en chargeant les données depuis des fichiers CSV.

        Args:
            segments_csv_full_path: Chemin vers le fichier CSV des segments
            relations_csv_full_path: Chemin vers le fichier CSV des relations entre segments
            track_circuits_csv_full_path: Chemin vers le fichier CSV des circuits
            tracking_blocks_csv_full_path: Chemin vers le fichier CSV des blocs
            switches_csv_full_path: Chemin vers le fichier CSV des aiguillages
            tracking_block_on_segments_csv_full_path: Chemin vers le fichier CSV des relations blocs/segments
            ignore_tracking_blocks_without_circuits: Si True, ignore les blocs sans circuit.
                                                      Si False, lève une exception.

        Returns:
            Objet Line contenant tous les composants
        """
        # Charger les segments
        segments = Segment.load_from_csv(segments_csv_full_path)

        # Charger la topologie des segments
        Segment.load_topology_from_csv(segments, segments_relations_csv_full_path)

        # Charger les circuits
        circuits_list = TrackingCircuit.load_from_csv(track_circuits_csv_full_path)
        track_circuit_by_id = {c.identifier: c for c in circuits_list}

        # Charger les blocs avec associations aux circuits
        blocks_list, not_created_tracking_blocks_ids_without_track_circuits = TrackingBlock._load_from_csv_raw(
            tracking_blocks_csv_full_path,
            track_circuit_by_id,
            ignore_tracking_blocks_without_circuits,
        )

        # Charger les relations bloc/segment si fournies
        tracking_block_by_id = {block.identifier: block for block in blocks_list}
        segments_dict = {segment.identifier: segment for segment in segments}
        tracking_block_on_segments = []
        if tracking_block_on_segments_csv_full_path is not None:
            tracking_block_on_segments = TrackingBlockOnSegment.load_from_csv(
                tracking_block_on_segments_csv_full_path,
                tracking_block_by_id,
                segments_dict,
            )

        # Charger les aiguillages
        switches_list = Switch.load_from_csv(switches_csv_full_path)
        switches_dict = {s.identifier: s for s in switches_list}

        return Line(
            segments=segments,
            track_circuits=circuits_list,
            track_circuit_by_id=track_circuit_by_id,
            tracking_blocks=blocks_list,
            switches=switches_dict,
            not_created_tracking_blocks_ids_without_track_circuits=not_created_tracking_blocks_ids_without_track_circuits,
            tracking_block_on_segments=tracking_block_on_segments,
        )


class Direction(str, Enum):
    """Énumération des directions possibles."""

    UP = "UP"
    DOWN = "DOWN"
    BOTH = "BOTH"
    UNKNOWN = "UNKNOWN"


@dataclass
class TrackingCircuit:
    """
    Représente un circuit de detection d'occupation de voie ferrée.

    Attributs:
        identifier: Identifiant unique du circuit (ex: CDV_z124Nord)
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

    identifier: str
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
                    identifier=row["ID"],
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
        identifier: Identifiant unique du bloc (ex: TB_CDV_z124Nord_01)
        label: Libellé du bloc (optionnel)
        type: Type du bloc (optionnel)
        track_circuit_id: Identifiant du circuit de détection associé
        isotropic: Indicateur isotrope (bool)
        border: Indicateur de limite (bool)
        steering: Direction de pilotage (UP, DOWN, ou None)
        extension_id: Identifiant d'extension (optionnel)
        tracking_circuit: Référence vers le circuit de détection associé (obligatoire)
    """

    identifier: str
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
                    identifier=block_id,
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
            logger_config.print_and_log_warning(
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


@dataclass
class Switch:
    """
    Représente un aiguillage (switch) d'une ligne ferroviaire.

    Attributs:
        identifier: Identifiant unique de l'aiguillage (ex: SW_001)
        label: Libellé de l'aiguillage (optionnel)
        normal_id: Identifiant de la position normale (optionnel)
        reverse_id: Identifiant de la position de déraillement (optionnel)
        forcing_id: Identifiant de forçage (optionnel)
        trailable: Indicateur tractable (bool)
        convergency_direction: Direction de convergence (UP, DOWN, ou None)
    """

    identifier: str
    label: Optional[str]
    normal_id: Optional[str]
    reverse_id: Optional[str]
    forcing_id: Optional[str]
    trailable: bool
    convergency_direction: Optional[Direction]

    @classmethod
    def _load_from_csv_raw(
        cls,
        csv_file_path: str | Path,
    ) -> List["Switch"]:
        """
        Charge les aiguillages depuis un fichier CSV et crée les objets Switch.

        Args:
            csv_file_path: Chemin vers le fichier CSV

        Returns:
            Liste des objets Switch créés

        Format du CSV:
            ID;LABEL;NORMAL_ID;REVERSE_ID;FORCING_ID;TRAILABLE;CONVERGENCY_DIRECTION
        """
        switches = []
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

                switch = cls(
                    identifier=row["ID"],
                    label=to_none(row["LABEL"]),
                    normal_id=to_none(row["NORMAL_ID"]),
                    reverse_id=to_none(row["REVERSE_ID"]),
                    forcing_id=to_none(row["FORCING_ID"]),
                    trailable=to_bool(row["TRAILABLE"]),
                    convergency_direction=to_direction(row["CONVERGENCY_DIRECTION"]),
                )
                switches.append(switch)

        return switches

    @classmethod
    def load_from_csv(cls, csv_file_path: str | Path) -> List["Switch"]:
        """
        Charge une liste d'aiguillages depuis un fichier CSV.

        Args:
            csv_file_path: Chemin vers le fichier CSV

        Returns:
            Liste des objets Switch

        Format du CSV:
            ID;LABEL;NORMAL_ID;REVERSE_ID;FORCING_ID;TRAILABLE;CONVERGENCY_DIRECTION
        """
        return cls._load_from_csv_raw(csv_file_path)


@dataclass
class TrackingBlockOnSegment:
    """
    Représente la relation entre un bloc de détection et un segment.

    Attributs:
        id: Identifiant unique de la relation
        tracking_block: Référence vers le bloc de détection
        segment: Référence vers le segment
        abs_begin: Position absolue de début (int)
        abs_end: Position absolue de fin (int)
    """

    id: str
    tracking_block: TrackingBlock
    segment: Segment
    abs_begin: int
    abs_end: int

    def __post_init__(self) -> None:
        assert self.tracking_block
        assert self.segment
        assert self.abs_begin
        assert self.abs_end

    @classmethod
    def load_from_csv(
        cls,
        csv_file_path: str | Path,
        tracking_blocks_dict: Dict[str, TrackingBlock],
        segments_dict: Dict[str, Segment],
    ) -> List["TrackingBlockOnSegment"]:
        """
        Charge une liste de relations TrackingBlock-Segment depuis un fichier CSV.

        Args:
            csv_file_path: Chemin vers le fichier CSV
            tracking_blocks_dict: Dictionnaire des blocs de détection par ID
            segments_dict: Dictionnaire des segments par ID

        Returns:
            Liste des objets TrackingBlockOnSegment

        Format du CSV:
            ID;TB_ID;SEGMENT_ID;ABS_BEGIN;ABS_END
        """
        relations = []
        csv_path = Path(csv_file_path)

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")

            for row in reader:
                relation_id = row["ID"]
                tb_id = row["TB_ID"]
                segment_id = row["SEGMENT_ID"]
                abs_begin = int(row["ABS_BEGIN"])
                abs_end = int(row["ABS_END"])

                tracking_block = tracking_blocks_dict.get(tb_id)
                if not tracking_block:
                    logger_config.print_and_log_warning(f"Bloc de détection '{tb_id}' non trouvé pour la relation '{relation_id}'.")
                    continue

                segment = segments_dict.get(segment_id)
                if not segment:
                    logger_config.print_and_log_warning(f"Segment '{segment_id}' non trouvé pour la relation '{relation_id}'.")
                    continue

                relation = cls(
                    id=relation_id,
                    tracking_block=tracking_block,
                    segment=segment,
                    abs_begin=abs_begin,
                    abs_end=abs_end,
                )
                relations.append(relation)

        return relations
