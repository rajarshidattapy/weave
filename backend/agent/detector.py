from bs4 import BeautifulSoup


def detect_components(html):

    soup = BeautifulSoup(html, "lxml")

    components = []

    sections = soup.find_all(["section", "article"])

    for i, sec in enumerate(sections):

        classes = sec.get("class", [])

        components.append({
            "id": f"component_{i}",
            "html": str(sec),
            "classes": classes
        })

    return components