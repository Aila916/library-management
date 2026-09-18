from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
import os, json

# This file creates the shared document object and saves progress
doc = Document()

for section in doc.sections:
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1.5)
    section.right_margin = Inches(1)

styles = doc.styles
normal = styles['Normal']
normal.font.name = 'Times New Roman'
normal.font.size = Pt(12)
normal.paragraph_format.line_spacing = 1.5

for level, size in [(1, 16), (2, 14), (3, 12)]:
    h = styles['Heading %d' % level]
    h.font.name = 'Times New Roman'
    h.font.size = Pt(size)
    h.font.bold = True
    h.font.color.rgb = RGBColor(0, 0, 0)

def h1(t): doc.add_heading(t, level=1)
def h2(t): doc.add_heading(t, level=2)
def h3(t): doc.add_heading(t, level=3)
def p(t, bold=False):
    para = doc.add_paragraph()
    run = para.add_run(t)
    run.bold = bold
def bullet(t): doc.add_paragraph(t, style='List Bullet')
def numbered(t): doc.add_paragraph(t, style='List Number')
def pb(): doc.add_page_break()

# COVER PAGE
p("WEB-BASED LIBRARY MANAGEMENT SYSTEM USING FLASK AND MySQL", True)
p("A PROJECT REPORT SUBMITTED TO THE SCHOOL OF COMPUTING AND INFORMATICS")
p("IN PARTIAL FULFILLMENT OF THE REQUIREMENTS FOR THE AWARD OF")
p("BACHELOR OF SCIENCE IN COMPUTER SCIENCE")
p("")
p("SUBMITTED BY:", True)
p("[YOUR NAME]")
p("[YOUR REGISTRATION NUMBER]")
p("")
p("SUPERVISOR:", True)
p("[SUPERVISOR NAME]")
p("")
p("2026", True)
pb()

# DECLARATION
h1("DECLARATION")
p("I hereby declare that this project is my original work and has not been submitted for any degree or diploma in any other university.")
p("Signature: ................................    Date: ................................")
p("[YOUR NAME]", True)
p("")
p("This project has been submitted for examination with my approval as the university supervisor.")
p("Signature: ................................    Date: ................................")
p("[SUPERVISOR NAME]", True)
pb()

# DEDICATION
h1("DEDICATION")
p("This project is dedicated to my family, whose unwavering support, encouragement, and understanding have been instrumental throughout my academic journey.")
pb()

# ACKNOWLEDGEMENT
h1("ACKNOWLEDGEMENT")
p("I sincerely express my gratitude to Almighty God for the gift of life and sound mind. I also thank my supervisor for their guidance, support, and constructive criticism throughout this study. I thank the management and staff of the university for their cooperation during data collection. Special appreciation goes to my lecturers, classmates, and friends for their encouragement and intellectual support.")
pb()

# TABLE OF CONTENTS
h1("TABLE OF CONTENTS")
p("DECLARATION")
p("DEDICATION")
p("ACKNOWLEDGEMENT")
p("TABLE OF CONTENTS")
p("LIST OF FIGURES")
p("LIST OF TABLES")
p("LIST OF ACRONYMS AND ABBREVIATIONS")
p("OPERATIONAL DEFINITION OF TERMS")
p("ABSTRACT")
p("CHAPTER ONE: INTRODUCTION")
p("CHAPTER TWO: LITERATURE REVIEW")
p("CHAPTER THREE: METHODOLOGY")
p("CHAPTER FOUR: SYSTEM ANALYSIS AND DESIGN")
p("CHAPTER FIVE: IMPLEMENTATION AND TESTING")
p("CHAPTER SIX: CONCLUSION AND RECOMMENDATIONS")
p("REFERENCES")
p("APPENDICES")
pb()

# LIST OF FIGURES
h1("LIST OF FIGURES")
p("Figure 2.1: Conceptual Framework Model")
p("Figure 4.1: Use Case Diagram")
p("Figure 4.2: Context-Level Data Flow Diagram")
p("Figure 4.3: Level 1 Data Flow Diagram")
p("Figure 4.4: Entity Relationship Diagram")
p("Figure 4.5: System Architecture")
pb()

# LIST OF TABLES
h1("LIST OF TABLES")
p("Table 3.1: Development Tools and Technologies")
p("Table 4.1: Users Table")
p("Table 4.2: Books Table")
p("Table 4.3: Members Table")
p("Table 4.4: Borrow Records Table")
p("Table 5.1: Test Results Summary")
pb()

# ACRONYMS
h1("LIST OF ACRONYMS AND ABBREVIATIONS")
p("CSS - Cascading Style Sheets")
p("DFD - Data Flow Diagram")
p("ERD - Entity Relationship Diagram")
p("FR - Functional Requirement")
p("HTML - HyperText Markup Language")
p("LMS - Library Management System")
p("MySQL - My Structured Query Language")
p("NFR - Non-Functional Requirement")
p("SQL - Structured Query Language")
pb()

# DEFINITIONS
h1("OPERATIONAL DEFINITION OF TERMS")
p("Analytics: The process of examining and interpreting library data to identify patterns and trends.")
p("Authentication: The process of verifying the identity of a user before allowing access.")
p("Book Availability: The number of copies of a book currently available for borrowing.")
p("Borrowing Transaction: A recorded activity in which a member is issued a book.")
p("Dashboard: A graphical interface that displays important library statistics.")
p("Database: An organized collection of data stored electronically.")
p("Fine: A monetary amount recorded against a member for failing to return a book on time.")
p("Flask: A lightweight Python-based web framework.")
p("Library Management System: A computerized system for managing library resources.")
p("Member: A registered library user authorized to borrow books.")
p("MySQL: A relational database management system.")
p("Overdue Book: A borrowed book not returned by the due date.")
p("Web-Based System: A software application accessed through a web browser.")
pb()

# ABSTRACT
h1("ABSTRACT")
p("Libraries play an important role in supporting teaching, learning, research, and access to information. However, many libraries continue to rely on manual methods for managing books, members, borrowing, and returning activities. These methods are time-consuming and prone to errors.")
p("This project developed a Web-Based Library Management System using Flask and MySQL to address these challenges. The system provides centralized management of books, members, borrowing and returning transactions, overdue records, fines, inventory, reports, and analytics.")
p("The system was tested using 38 test cases covering all major functions. All 38 test cases passed successfully. The system satisfied all 38 functional requirements and 13 non-functional requirements.")
p("The study concludes that the Web-Based Library Management System significantly improves the efficiency, accuracy, and organization of library management activities. It recommends adoption of the system, training of library personnel, and future enhancements including automated notifications, book reservations, and enhanced security.")
pb()

output_path = os.path.join(os.path.expanduser("~"), "Desktop", "Library_Management_System_Project.docx")
doc.save(output_path)
print("PART 1 DONE - Front matter saved to: " + output_path)