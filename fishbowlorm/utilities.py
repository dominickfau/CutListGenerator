from __future__ import annotations
from .models import FBBom, FBBomItemType, FBPart
from . import FishbowlORM



def get_parts_recursive(orm: FishbowlORM, bom: FBBom, bom_item_type: FBBomItemType) -> list[FBPart]:
    """Returns a list of parts that are in the BOM of the type bom_item_type."""
    parts = []
    for bom_item in bom.items:
        if bom_item.typeObj != bom_item_type: continue
        default_bom_id = bom_item.partObj.defaultBomId
        recursive_bom = FBBom.find_by_id(orm, default_bom_id)
        if recursive_bom is None: continue
        parts.append(bom_item.partObj)
        parts.extend(get_parts_recursive(orm, recursive_bom, bom_item_type))
    return parts


def get_child_parts(orm: FishbowlORM, parent_part: FBPart) -> list[FBPart]:
    """Returns a list of all parts required to make the part provided."""
    processed_boms = {} # type: dict[FBBom, list[FBPart]] # Used to speed up the process by saving the BOMs that have already been processed.
    required_parts = []
    raw_bom_item = FBBomItemType.find_by_name(orm, "Raw Good")

    default_bom_id = parent_part.defaultBomId
    bom = FBBom.find_by_id(orm, default_bom_id)
    if bom is None: return []

    if bom not in processed_boms:
        processed_boms[bom] = parts = get_parts_recursive(orm, bom, raw_bom_item)
    else:
        parts = processed_boms[bom]
    required_parts.extend(parts)

    return required_parts