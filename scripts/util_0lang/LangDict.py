from typing import override

class LangDict(dict[str, str]):
    lang_codeErrorCounter=0
    @override
    def __getitem__(self, key:str|tuple[str, dict[str,str]]) -> str:
        lang_code = key[0] if isinstance(key, tuple) else key
        attributes = key[1] if isinstance(key, tuple) else {}
        
        if lang_code in self and not (
                (lang_code=="item-shield-woodmetal" and attributes)
        ):
            return super().__getitem__(lang_code)
        lang_code_parts = lang_code.split("-")
        #print(lang_code)
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
            case ("item", "shield", "metal"), attr if not attr:
                ### TODO this isn't actially a todo, just wanted to say this is bad
                return "Metal round shield"
            case ("item", "shield", "woodmetal"), {"deco": "none", "wood": wood, "metal": _}:
                return self[f"item-shield-woodmetal-*-{wood}-none"]
            case ("item", "shield", "woodmetalleather"), {"wood":"generic", "deco": "ornate", "metal": _, "color": _}:
                return self["item-shield-woodmetalleather-*-generic-*-ornate"]
            case ("item", "shield", "woodmetalleather"), {"deco": "none", "color": color, "wood": "generic", "metal": _}:
                return self[f"item-shield-woodmetalleather-*-generic-{color}-none"]
            case ("item", "shield", "woodmetalleather"), attr if not attr:
                ### TODO this isn't actially a todo, just wanted to say this is bad
                return "Leather-reinforced round shield"

            case ("item"|"block", "air"), _:
                return self["Air"]

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
            case ("block", "windmillrotor", _), _:
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
            case ("block", "fire"), _:
                return self["Fire"]
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
            case ("block", "bed", type, *_), _:
                return self[f"block-bed-{type}-head-*"]
            case ("block", "brickslabs", "blue"|"brown"|"fire"|"red", *_), _:
                color = lang_code_parts[2]
                return self[f"block-brickslabs-{color}-*"]
            case ("block", "brickslabs", "four"|"eight", color, *_), _:
                shape = lang_code_parts[2]
                return self[f"block-brickslabs-{shape}-{color}-*"]
            case ("block", "roughhewnfencegate", wood, *_), _:
                return self[f"block-roughhewnfencegate-{wood}-n-closed-*"]
            case ("block", "roughhewnfence", wood, *_), _:
                return self[f"block-roughhewnfence-{wood}-ew-*"]
            case ("block", "looseores", mineral, rock), _:
                if mineral in ("olivine", "sylvite"):
                    mineral = f"{mineral}-{rock}"
                return self[f"block-looseores-{mineral}-*"]
            case ("block", "woodenfencegate", wood, *_), _:
                return self[f"block-woodenfencegate-{wood}-n-closed-left-*"]
            case ("block", "woodenfence", wood, *_), _:
                return self[f"block-woodenfence-{wood}-ew-*"]
            case ("block", "drystonefence", stone, *_), _:
                return self[f"block-drystonefence-{stone}-*"]
            case ("block", "cobblestonestairs", stone, *_), _:
                return self[f"block-cobblestonestairs-{stone}-*"]
            case ("block", "cobblestoneslab", stone, *_), _:
                return self[f"block-cobblestoneslab-{stone}-*"]
            case ("block", "stonebrickstairs", stone, *_), _:
                return self[f"block-stonebrickstairs-{stone}-*"]
            case ("block", "looseboulders", stone, *_), _:
                return self[f"block-looseboulders-{stone}-*"]
            case ("block", "slantedroofingcornerinner", material, *_), _:
                return self[f"block-slantedroofingcornerinner-{material}-*"]
            case ("block", "slantedroofingridgehalfright", material, *_), _:
                return self[f"block-slantedroofingridgehalfright-{material}-*"]
            case ("block", "stonebrickslab", material, *_), _:
                return self[f"block-stonebrickslab-{material}-*"]
            case ("block", "ladder", "wood", wood, _), _:
                print(f"block-ladder-wood-{wood}-*")
                print(self[f"block-ladder-wood-{wood}-*"])
                return self[f"block-ladder-wood-{wood}-*"]
            case ("block", "ladder", kind, "north"|"south"|"east"|"west"), _:
                return self[f"block-ladder-{kind}-*"]



            # likely just not fully implemented:
            case (
                (("item", "tusk", "pig", *_), _)
              | (("item", "ontree", "bellpepper", _, _), _)
              | (("block", "crop", "bellpepper", _), _)
            ):
                return ""

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
            ):
                return ""

            case _:
                self.lang_codeErrorCounter+=1
                print(self.lang_codeErrorCounter, f"Debug lang_codeError: {lang_code:<55}, {attributes}"); return lang_code
                #raise lang_codeError(f"{lang_code:<55}, {attributes}")

