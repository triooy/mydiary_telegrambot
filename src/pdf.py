from datetime import datetime

from fpdf import FPDF
from fpdf.enums import XPos, YPos


class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.col = 0  # Current column
        self.y0 = 0  # Ordinate of column start

    def header(self):
        self.set_font("Rokkitt", "B", 8)
        width = self.get_string_width(self.title) + 6
        self.set_x((210 - width) / 2)
        self.set_text_color(
            128,
        )
        self.set_line_width(1)
        self.cell(
            width,
            7,
            f"{self.title}",
            new_x=XPos.RIGHT,
            new_y=YPos.TOP,
            align="C",
            fill=False,
        )
        self.ln(10)
        # Saving ordinate position:
        self.y0 = self.get_y()

    def footer(self):
        self.set_y(-15)
        self.set_font("Rokkitt", "B", 8)
        self.set_text_color(128)
        self.cell(
            0,
            10,
            f"{self.page_no()}/{{nb}}",
            new_x=XPos.RIGHT,
            new_y=YPos.NEXT,
            align="C",
        )

    def set_col(self, col):
        # Set column position:
        self.col = col
        x = 10 + col * 95
        self.set_left_margin(x)
        self.set_x(x)

    @property
    def accept_page_break(self):
        if self.col < 1:
            # Go to next column:
            self.set_col(self.col + 1)
            # Set ordinate to top:
            self.set_y(self.y0)
            # Stay on the same page:
            return False
        # Go back to first column:
        self.set_col(0)
        # Trigger a page break:
        return True

    def chapter_title(self, label):
        self.set_font("Rokkitt", "B", 16)
        self.cell(
            0, 6, f"{label}", new_x=XPos.RIGHT, new_y=YPos.NEXT, align="L", fill=False
        )
        self.ln(4)
        # Saving ordinate position:
        self.y0 = self.get_y()

    def chapter_body(self, txt):
        # Reading text file:
        self.set_font("Rokkitt", "", 12)

        # Printing text in a 6cm width column:
        self.multi_cell(90, 5, txt)
        self.ln()
        # Start back at first column:
        self.set_col(0)

    def print_chapter(self, title, name):
        self.add_page()
        self.chapter_title(title)
        self.chapter_body(name)


def p(pdf, text, **kwargs):
    "Inserts a paragraph"
    pdf.multi_cell(
        w=pdf.epw,
        h=pdf.font_size,
        txt=text,
        new_x="LMARGIN",
        new_y="NEXT",
        **kwargs,
    )


def render_toc(pdf, outline):
    pdf.y += 50
    pdf.set_font("Rokkitt", "B", size=16)
    pdf.underline = True
    p(pdf, "Table of contents:")
    pdf.underline = False
    pdf.y += 20
    pdf.set_font("Rokkitt", size=12)
    for section in outline:
        link = pdf.add_link(page=section.page_number)
        p(
            pdf,
            f'{" " * section.level * 2} {section.name} {"." * (60 - section.level*2 - len(section.name))} {section.page_number}',
            align="C",
            link=link,
        )


def create_pdf(data, author, start_date=None, end_date=None):

    if start_date:
        # convert to datetime: str:22.02.2020
        start_date = datetime.strptime(start_date, "%d.%m.%Y")
        data = data[(data["date"] >= start_date)]
    if end_date:
        end_date = datetime.strptime(end_date, "%d.%m.%Y")
        data = data[(data["date"] <= end_date)]

    data["date"] = data["date"].dt.strftime("%d.%m.%Y")

    date = datetime.now().strftime("%d.%m.%Y")
    pdf = PDF()
    pdf.add_font("Rokkitt", "", "./data/fonts/Rokkitt/static/Rokkitt-Light.ttf")
    pdf.add_font("Rokkitt", "B", "./data/fonts/Rokkitt/static/Rokkitt-Regular.ttf")
    # pdf.add_font("emoji", fname="./data/fonts/Noto_Color_Emoji/NotoColorEmoji-Regular.ttf")
    # pdf.set_fallback_fonts(["emoji"])

    first_date = data["date"].iloc[0]
    last_date = data["date"].iloc[-1]
    title = "Tagebuch"
    pdf.set_title(
        title,
    )
    pdf.set_author(author)
    pdf.add_page()
    pdf.set_font("Rokkitt", "B", 40)
    # write a big title with author and dates on the first page
    pdf.ln()
    pdf.multi_cell(0, 50, author, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.multi_cell(
        0, None, f"{first_date} - {last_date}", new_x="LMARGIN", new_y="NEXT", align="C"
    )
    pdf.set_font("Rokkitt", "B", 20)
    pdf.cell(5, 450, f"Herausgegeben: {date}", align="L", new_x="LMARGIN", new_y="NEXT")

    number_of_entries = len(data)
    table_of_contents_pages = int(number_of_entries / 50) + 1

    pdf.insert_toc_placeholder(render_toc, table_of_contents_pages)

    pdf.set_col(0)
    pdf.add_page()
    col_width = 90
    col_height = 5
    for i, row in data.iterrows():
        date = row["date"]
        entry = row["entry"]
        images = row["images"]
        pdf.start_section(f"{date}", level=1)
        pdf.set_title(f"{date}")
        pdf.set_font("Rokkitt", "B", 16)
        pdf.multi_cell(
            col_width,
            col_height,
            f"{date}",
        )
        pdf.ln(1)
        pdf.set_font("Rokkitt", "", 12)

        entry = entry.split("\n")
        # remove empty lines in the end
        while entry[-1] == "":
            entry.pop()
        entry = "\n".join(entry) + "\n"
        pdf.multi_cell(col_width, None, entry)
        pdf.ln()
        if len(images) > 0:
            for image in images:
                pdf.image(
                    "./data/images/" + image,
                    w=col_width - 5,
                )

    first_date = datetime.strptime(first_date, "%d.%m.%Y").strftime("%Y_%m_%d")
    end_date = datetime.strptime(last_date, "%d.%m.%Y").strftime("%Y_%m_%d")
    dates = f"{first_date}-{end_date}"
    file = f'{dates}-{author.replace(" ", "_")}.pdf'.lower()
    filepath = file
    pdf.output(filepath, "F")
    return filepath
