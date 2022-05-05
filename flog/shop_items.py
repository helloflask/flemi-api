from datetime import timedelta


class Item:
    def __init__(
        self,
        name: str = "",
        category: str = "",
        exp: int = 0,
        gradient_deg: str = "45deg, ",
        expires: int = 0,
        color: str = "",
        **kwargs,
    ):
        self.name = name
        self.category = category
        self.exp = 0 if not exp else exp
        self.price = 0
        self.expires = timedelta(days=expires)
        if category == "":
            self.style = ""
            self.text_style = "color: inherit;"
        if category == "Classic":
            self.style = f"background-color: {color};"
            self.text_style = f"color: {color};"
            self.price = 5 * (expires / 30) - 2 * (expires / 30 - 1) - 0.01
        elif category == "Rare" or category == "Leveled":
            # gradient color
            gradient = f"linear-gradient({gradient_deg}{color})"
            self.style = f"background-image: {gradient};"
            self.text_style = f"""
                background: {gradient};
                -webkit-background-clip: text;
                color: transparent;
            """
            if category == "Rare":
                self.price = 9 * (expires / 30) - 2 * (expires / 30 - 1) - 0.01
        if "price" in kwargs.keys():
            self.price = kwargs["price"]


def items(id: int, mode="get") -> Item:
    item_list = (
        Item(category=""),
        Item(
            name="Rose",
            expires=30,
            color="#DE2344",
            category="Classic",
        ),
        Item(
            name="Orange",
            expires=30,
            color="#FE9A2E",
            category="Classic",
        ),
        Item(
            name="Sun",
            expires=30,
            color="#EBBC34",
            category="Classic",
        ),
        Item(
            name="Mint",
            expires=30,
            color="#2EFE9A",
            category="Classic",
        ),
        Item(
            name="Copper 2+",
            expires=30,
            exp=100,
            color="#2E64FE",
            category="Classic",
        ),
        Item(
            name="Violet",
            expires=30,
            color="#7401DF",
            category="Classic",
        ),
        Item(
            name="Fire",
            expires=30,
            color="#8000FF, #FE2E64, #FE9A2E",
            category="Rare",
        ),
        Item(
            name="Frozen",
            expires=30,
            color="#5882FA, #81F7F3",
            category="Rare",
        ),
        Item(
            name="Shore",
            expires=30,
            color="#04B486, #04B486, #F2F5A9",
            category="Rare",
        ),
        Item(
            name="Aurora",
            expires=30,
            color="#08088A, #04B486",
            category="Rare",
        ),
        Item(
            name="Sweet",
            expires=30,
            color="#F5A9D0, #BE81F7",
            category="Rare",
        ),
        Item(
            name="Helium",
            expires=30,
            color="#FF8000, #FF8000, #F6E3CE, #FF8000, #FF8000",
            gradient_deg="",
            category="Rare",
        ),
        Item(
            name="Rainbow",
            expires=30,
            color="#FFFF00, #FF00FF, #00FFFF",
            category="Rare",
        ),
        Item(
            name="Seven",
            expires=99999,
            color="#00FFBF, #2E64FE",
            exp=1100,
            category="Leveled",
        ),
        Item(
            name="Crown",
            expires=99999,
            exp=2500,
            color="#4000FF, #DF01A5",
            category="Leveled",
        ),
        Item(
            name="Black Sea",
            expires=99999,
            exp=3100,
            color="#2CD8D5, #6B8DD6, #8E37D7",
            gradient_deg="-225deg, ",
            category="Leveled",
            price=16.66,
        ),
        Item(
            name="Sky Five",
            expires=99999,
            exp=5500,
            color="#D4FFEC 0%, #57F2CC 48%, #4596FB 100%",
            gradient_deg="-225deg, ",
            category="Leveled",
            price=16.66,
        ),
        Item(
            name="Amour",
            expires=99999,
            exp=1500,
            color="#f77062, #fe5196",
            gradient_deg="to top, ",
            category="Leveled",
        ),
        Item(
            name="Harmony",
            expires=30,
            exp=0,
            color="#3D4E81 0%, #5753C9 48%, #6E7FF3 100%",
            gradient_deg="-225deg, ",
            category="Rare",
        ),
        Item(
            name="Phoenix",
            expires=30,
            exp=0,
            color="#f83600, #f9d423",
            gradient_deg="to right, ",
            category="Rare",
        ),
        Item(
            name="Life",
            expires=60,
            exp=0,
            color="#43e97b, #38f9d7",
            gradient_deg="to right, ",
            category="Rare",
        ),
        Item(
            name="Beach",
            expires=60,
            exp=0,
            color="#4facfe, #00f2fe",
            gradient_deg="to right, ",
            category="Rare",
        ),
    )
    return (
        item_list[id] if mode == "get" else (len(item_list) if mode == "len" else None)
    )
