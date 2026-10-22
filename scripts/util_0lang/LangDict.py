from typing import override

_NO = "<<fuck you>>"
_LEGACY = "<<probably legacy>>"
_UNIMPLEMENTED = "<<probably yet to be implemented>>"

class LangDict(dict[str, str]):
    lang_codeErrorCounter=0
    error_codes={}


    @override
    def __getitem__(self, key:str|tuple[str, dict[str,str]]) -> str:
        lang_code = key[0] if isinstance(key, tuple) else key
        attributes = key[1] if isinstance(key, tuple) else None

        if lang_code in self and not (
                (lang_code=="item-shield-woodmetal" and type(attributes) is dict)
        ):
            return super().__getitem__(lang_code)

        lang_code_parts = lang_code.split("-")
        # print(lang_code)
        match lang_code_parts, attributes:
            case ("item", ("crystalizedore"|"ore"), rarity, metal, rock), _:
                size = lang_code_parts[1] if lang_code_parts[1]=="ore" else "crystallizedore"
                return(
                    self["ore-in-rock"]
                    .replace("{0}",
                        self[f"{rarity}-{size}-chunk"]
                        .replace("{0}",
                             self[f"ore-{metal}"]
                         )
                    )
                    .replace("{1}",
                        self[f"rock-{rock}"]
                    )
                )
            case ("item", "creature", "fish", water, *name, sub_type, age, _), _:
                return self[f"item-creature-fish-{water}-{'-'.join(name)}-{sub_type}-{age}"]
            case ("item", "creature", "trader", _, trade, location), _:
                return self[f"item-creature-trader-*-{trade}-{location}"]
            case ("item", "fishchunk", _, size, "cooked"), _:
                return self[f"item-fishchunk-*-{size}-cooked"]
            case ("item", "armor", slot, "tailored", _, linen), _:
                return self[f"item-armor-{slot}-tailored-*-linen"]
            case ("item", "pressedmash", fruit), {"juicableLitresLeft": litres}:
                return self[f"item-pressedmash-{fruit}-{'wet' if float(litres)>0 else 'dry'}"]
            case ("item", "pressedmash", fruit), _:
                return self[f"item-pressedmash-{fruit}-dry"]
            case ("item", "honeymash"), {"juicableLitresLeft": litres}:
                return self[f"item-honeymash-{'wet' if float(litres)>0 else 'dry'}"]
            case ("item", "honeymash"), _:
                return self["item-honeymash-dry"]
            case ("block", "crate"), {"type": kind}:
                return self[f"block-{kind}-crate"]
            case ("block", "crate"), _:
                return self["block-wood-aged-crate"].replace(
                    "{0}",
                    self["cratelidstate-closed"]
                )
            case ("item", "chutesection", _), _:
                return self["item-chutesection-*"]
            case ("item", "antler", animal, _), _:
                return self[f"item-antler-{animal}-*"]
            case ("item", "jamhoneyportion"), _:
                return self["recipeingredient-item-jamhoneyportion-topping"]
            case ("item", "ontree", animal, _), _:
                return self[f"item-ontree-{animal}-*"]
            case ("item", "butterfly", "dead", name), _:
                return self["item-deadbutterfly"].replace(
                    "{0}",
                    self[f"item-creature-butterfly-{name}"]
                )

            case ("item", "shield", "metal"), {"metal": metal, "color":_}:
                return self[f"item-shield-metal-{metal}-*"]
            case ("item", "shield", "woodmetal"), {"deco": "none", "wood": wood, "metal": _}:
                return self[f"item-shield-woodmetal-*-{wood}-none"]
            case ("item", "shield", "woodmetalleather"), {"wood":"generic", "deco": "ornate", "metal": _, "color": _}:
                return self["item-shield-woodmetalleather-*-generic-*-ornate"]
            case ("item", "shield", "woodmetalleather"), {"deco": "none", "color": color, "wood": "generic", "metal": _}:
                return self[f"item-shield-woodmetalleather-*-generic-{color}-none"]

            case ("block", "antlermount"), {"type": shape}:
                return self[f"block-antlermount-{shape}"]

            case ("block", "lantern", "large"|"small", _), {"material":material}:
                size = lang_code_parts[2]
                return self[f"block-lantern-{size}-*-{material}"]
            case ("block", "painting", painting, _), _:
                return self[f"block-painting-{painting}-*"]
            case ("block", "planks", wood, _), _:
                return self[f"block-planks-{wood}-*"]
            case ("block", "log", "placed", wood, _), _:
                return self[f"block-log-placed-{wood}-*"]
            case ("block", "chandelier", _), _:
                return self["block-chandelier-*"]
            case ("block", "fruitingbushcutting", berry, _), _:
                return self[f"block-fruitingbushcutting-{
                    berry if not berry.startswith("currant") else berry[7:]+berry[:7]
                }-*"]
            case (
                (("block", "fruitingbush", state, berry, "snow"|"free"), _)
              | (("block", "fruitingbush", state, berry), _)
            ):
                return self[f"block-fruitingbush-{state}-{berry}-*"]
            case (
                (("block", "fruitingbush", state, berry, "snow"|"free"), _)
              | (("block", "fruitingbush", state, berry), _)
            ):
                return self[f"block-fruitingbush-{state}-{berry}-*"]
            case ("block", "windmillrotor", "wood", _), _:
                return self[f"block-windmillrotor-wood-*"]
            case ("block", "windmillrotor", _, _), _:
                return self[f"block-windmillrotor-*"]
            case ("block", "mushroom", shroom, _), _:
                return self[f"block-mushroom-{shroom}-normal"]
            case ("block", "burnedplanks", shape, kind, _), _:
                return self[f"block-burnedplanks-{shape}-{kind}-*"]
            case ("block", "torchholder", material, _, _), _:
                return self[f"block-torchholder-{material}-*"]
            case ("block", "axlearm", _, _), _:
                return self["block-axlearm-*"]
            case ("block", "groundstorage"), _:
                return self["Empty pile"]
            case ("block", "wattlegate", *_), _:
                return self["block-wattlegate-*"]
            case ("block", "wattle", *_), _:
                return self["block-wattle-*"]
            case ("block", "trough", "genericwood", size, *_), _:
                return self[f"block-trough-genericwood-{size if size=="small" else f"{size}-head"}-*"]
            case ("block", "torch", "basic", state, _), _:
                return self[f"block-torch-basic-{state}-up"]
            case ("block", "toolrack", _), _:
                return self["block-toolrack-*"]
            case ("block", "stickslayer", "wooden", _, _), _:
                return self["block-stickslayer-wooden-ew-*"]
            case ("block", "stackedbamboo", _), _:
                return self["block-stackedbamboo-*"]
            case ("block", "sign", "wall"|"ground", _), _:
                return self["block-sign-ground-*"]
            case ("block", "ore", *rarity, mineral, _), _:
                return self[f"block-ore-{
                    "" if not rarity else(
                    rarity[0] if mineral in ("olivine_peridot", "emerald", "diamond") else
                    "*"
                )+"-"
                }{mineral}-*"]
            case ("block", "palisadewall", *_), _:
                return self["block-palisadewall-*"]
            case ("block", "fencebamboo", *_), _:
                return self["block-fencebamboo-*"]
            case ("block", "bed", bed_type, *_), _:
                return self[f"block-bed-{bed_type}-head-*"]
            case ("block", "roughhewnfencegate", wood, *_), _:
                return self[f"block-roughhewnfencegate-{wood}-n-closed-*"]
            case ("block", "roughhewnfence", wood, *_), _:
                return self[f"block-roughhewnfence-{wood}-ew-*"]
            case ("block", "looseores", mineral, rock, _), _:
                if mineral in ("olivine", "sylvite"):
                    mineral = f"{mineral}-{rock}"
                return self[f"block-looseores-{mineral}-*"]
            case ("block", "woodenfencegate", wood, *_), _:
                return self[f"block-woodenfencegate-{wood}-n-closed-left-*"]
            case ("block", "woodenfence", wood, *_), _:
                return self[f"block-woodenfence-{wood}-ew-*"]
            case (("block",
                   "cobblestonestairs"|"cobblestoneslab"|"cobblestonefan"|"stonebrickstairs"|"looseboulders"
                   |"stonebrickslab"|"drystonefence",
                   stone, *_), _):
                return self[f"block-{lang_code_parts[1]}-{stone}-*"]
            case ("block", "slantedroofingcornerinner", material, *_), _:
                return self[f"block-slantedroofingcornerinner-{material}-*"]
            case ("block", "slantedroofingridgehalfright", material, *_), _:
                return self[f"block-slantedroofingridgehalfright-{material}-*"]
            case ("block", "ladder", "wood", wood, _), _:
                return self[f"block-ladder-wood-{wood}-*"]
            case ("block", "ladder", kind, "north"|"south"|"east"|"west"), _:
                return self[f"block-ladder-{kind}-*"]
            case ("block", "gravel", rock, *_), _:
                return self[f"block-gravel-{rock}-*"]
            case ("block", "slantedroofingtop", material, *_), _:
                return self[f"block-slantedroofingtop-{material}-*"]
            case ("block", "slantedroofingridgehalfleft", material, *_), _:
                return self[f"block-slantedroofingridgehalfleft-{material}-*"]
            case ("block", "slantedroofinghalfright", material, *_), _:
                return self[f"block-slantedroofinghalfright-{material}-*"]
            case ("block", "slantedroofinghalfleft", material, *_), _:
                return self[f"block-slantedroofinghalfleft-{material}-*"]
            case ("block", "slantedroofingcornerouter", material, *_), _:
                return self[f"block-slantedroofingcornerouter-{material}-*"]
            case ("block", "slantedroofingridgeend", material, *_), _:
                return self[f"block-slantedroofingridgeend-{material}-*"]
            case ("block", "slantedroofingbottom", material, *_), _:
                return self[f"block-slantedroofingbottom-{material}-*"]
            case ("block", "slantedroofing", material, *_), _:
                return self[f"block-slantedroofing-{material}-*"]
            case ("block", "polishedrockslab", rock, *_), _:
                return self[f"block-polishedrockslab-{rock}-*"]
            case ("block", "crystal", crystal, size, _), _:
                return self[f"block-crystal-{crystal}-{size}-up"]
            case ("block", "crystal", crystal, size, _), _:
                return self[f"block-crystal-{crystal}-{size}-up"]
            case ("block", "logquad", log_type, wood, _), _:
                return self[f"block-logquad-{log_type}-{wood}-{'north' if log_type=='barkedcorner' else '*'}"]
            case ("block", "plankstairs", wood, *_), _:
                return self[f"block-plankstairs-{wood}-*"]
            case ("block", "plankslab", wood, *_), _:
                return self[f"block-plankslab-{wood}-*"]
            case ("block", "stalagsection", rock, _), _:
                return (self[f"block-speleothem"].replace(
                    "{0}",
                    self[f"block-{rock}"]
                ))
            case ("block", "caveart", *_), _:
                return self["block-caveart-*"]
            case ("block", "tileslab", size, design, color, *_), _:
                return self[f"block-tileslab-{size}-{design}-{color}-*"]
            case ("block", "metalsheet", metal, _), _:
                return self[f"block-metalsheet-{metal}-{'down' if metal=='meteoriciron' else '*'}"]
            case ("block", "glassslab", color, *_), _:
                return self[f"block-glassslab-{color}-{'down-free' if color in ('smoky', 'pink') else '*'}"]
            case ("block", "leaves"|"leavesbranchy"|"leavesbranchystatic", *_, wood), _:
                return self[f"block-{lang_code_parts[1]}-*-{wood}"]
            case ("block", "slantedroofingridge", material, *_), _:
                return self[f"block-slantedroofingridge-{material}-*"]
            case ("block", "loosestones", material, _), _:
                return self[f"block-loosestones-{'-'.join(material)}-*"]
            case ("block", "sand", rock, _), _:
                return self[f"block-loosestones-{rock}-*"]
            case ("block", "mushroom", mushroom, _), _:
                return self[f"block-mushroom-{mushroom}-normal"]
            case ("block", "looseflints", _, _), _:
                return self[f"block-looseflints-*"]
            case ("block", "clayshinglestairs"|"clayshinglelabs", color, *_), _:
                return self[f"block-{lang_code_parts[1]}-{color}-*"]
            case ("block", "jonas", kind, *sub_kinds, _), _: # needs to be like this cause of jonas-lamp ):
                return self[f"block-jonas-{f'{kind}{("-"+"-".join(sub_kinds)) if sub_kinds else ""}'}-{('south', 'north')[kind in ('boilerdoor',)]}"]
            case ("block", "brickstairs"|"brickslabs", "blue"|"brown"|"fire"|"red", *_), _:
                return self[f"block-{lang_code_parts[1]}-{lang_code_parts[2]}-*"]
            case ("block", "brickstairs"|"brickslabs", "four"|"eight", color, *_), _:
                return self[f"block-{lang_code_parts[1]}-{lang_code_parts[2]}-{color}-*"]
            case ("block", "trapdoor", "opened"|"closed", *_), _:
                return self[f"block-trapdoor-{lang_code_parts[2]}-*"]
            case ("block", "trapdoor", kind, material, *_), _:
                return self[f"block-trapdoor-{kind}-{material}{(
                        (kind in ('solid', 'window') and material in ('aged', 'veryaged') and '-1') or
                        (material in ('rusted', 'iron', 'aged') and '-*') or
                        '*'
                )}"]
            case ("block", "symbols", sub_type, *_), _:
                return self[f"block-symbols-{sub_type}-*"]
            # case ("block", "saltwater"|"lava"|"water"|"rapidwater", *_), _:
            #     return self[f"block-{lang_code_parts[1]}-*"]
            # case ("block", "saltwater"|"lava"|"water"|"rapidwater", *_), _:
            #     return self[f"block-{lang_code_parts[1]}-*"]


            ### TODO (FUGLY) Technically doesn't have a name, but one can be implied
            case ("item", "shield", "metal"), attr if not attr:
                return "Metal round shield"
            case ("item", "shield", "woodmetalleather"), attr if not attr:
                return "Leather-reinforced round shield"
            case ("block", "antlermount"), _:
                return "Wall Mount"


            case ("block", block), attr:
                if (
                        ((lang_id:=f"rock-{block}") in self.keys()) or
                        ((lang_id:=f"block-{block}*") in self.keys()) or
                        ((lang_id:=f"block-{block}-*") in self.keys()) or
                        () or
                        ()
                ):
                    return self[lang_id]
                if block in ("air", "microblock", "fire", "platepile", "peatpile", "candle"):
                    return _LEGACY
                # print(block)
                return _NO


            # TODO (I don't wanna do these)
            case (
                (("block", "door", *_), _)
              | (("block", "coral", *_, _), _)
              | (("block", "crop", *_, _), _)
            ):
                return _NO

            # likely just not fully implemented:
            case (
                (("item", "tusk", "pig", *_), _)
              | (("item", "ontree", "bellpepper", _, _), _)
              | (("block", "crop", "bellpepper", _), _)
            ):
                return _UNIMPLEMENTED

            # these are all seemingly just leftover codes
            case (
                (("item", "clothes", *_), _)
              | (("item", "hide", "soaked", "bear", _, "body"), _)
              | (("item", "crushed", "leadoxide"), _)
              | (("item", "snowshovel", "generic"), _)
              | (("item", "clayworkitem", "blue"|"red"|"fire"), _) # funny items
              | (("item", "creature", "humanoid", "trader", _), _)
              | (("block", "lantern", _), _)
              | (("block", "mannequin", "head"|"legs"|"torso", "ns"|"we"), _)
              | (("block", "ladder", "wood", _), _)
              | (("block", "supportbeam", "veryagedrotten", *_), _)
              | (("block", "debarkedlog", "veryagedrotten", *_), _)
              | (("block", "fruitingbush", _), _)
              | (("block", "multiblock", *_), _)
              | (("block", "mushroom", *_), _)
              | (("block", "jonas", "lamp"), _)
              | (("item", "air"), _)
              | (("block", "microblock", *_), _)
            ):
                return _LEGACY

            case _:
                self.lang_codeErrorCounter+=1
                sub_type = "-".join(lang_code_parts[:2])
                if sub_type not in self.error_codes:
                    self.error_codes[sub_type] = set()
                self.error_codes[sub_type].add(lang_code)
                print(self.lang_codeErrorCounter, f"Debug lang_codeError: {lang_code:<55}, {attributes}")
                return ""
                ### vvv probably never actually gonna uncomment that since actual errors are annoying, but deleting it feels wrong :3
                # raise lang_codeError(f"{lang_code:<55}, {attributes}")

