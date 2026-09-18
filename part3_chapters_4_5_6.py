from docx import Document
from docx.shared import Pt, Inches
from docx.enum.table import WD_TABLE_ALIGNMENT
import os

output_path = os.path.join(os.path.expanduser("~"), "Desktop", "Library_Management_System_Project.docx")
doc = Document(output_path)

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

def add_table(headers, rows):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = 'Light Grid Accent 1'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = str(val)
    doc.add_paragraph()

# ============ CHAPTER 4 ============
pb()
h1("CHAPTER FOUR: SYSTEM ANALYSIS AND DESIGN")

h2("4.1 Introduction")
p("This chapter presents the analysis and design of the Web-Based Library Management System. It translates the requirements identified during the methodology stage into a structured system design.")

h2("4.2 Analysis of Proposed System")
p("The proposed Web-Based Library Management System was analyzed based on the problems identified in the existing library management approach.")
h3("4.2.1 Main System Processes")
p("The main processes identified during the analysis are:")
bullet("User Authentication")
bullet("Book Management")
bullet("Member Management")
bullet("Book Borrowing")
bullet("Book Returning")
bullet("Overdue and Fine Processing")
bullet("Inventory Monitoring")
bullet("Transaction History")
bullet("Reports and Analytics")
bullet("Book Searching")
bullet("User Profile")
h3("4.2.2 Information Requirements")
p("The main categories of information required by the system include user information, book information, member information, borrowing information, inventory information, overdue and fine information, and reporting information.")

h2("4.3 System Requirements Specification")
h3("4.3.1 Functional Requirements")
p("The implemented system shall:")
numbered("Provide user authentication through login and logout.")
numbered("Allow authenticated users to access protected library functions.")
numbered("Allow users to add, view, update, and search book records.")
numbered("Store book information including title, author, ISBN, category, and quantity.")
numbered("Allow users to register, view, and update member records.")
numbered("Prevent duplicate member registration.")
numbered("Allow users to borrow available books for registered members.")
numbered("Record borrowing dates and due dates.")
numbered("Automatically reduce book quantity after borrowing.")
numbered("Allow users to process returned books.")
numbered("Automatically increase book quantity after return.")
numbered("Identify overdue transactions.")
numbered("Process fine information for overdue transactions.")
numbered("Monitor book quantities and identify low-stock books.")
numbered("Maintain borrowing and return history.")
numbered("Provide a dashboard containing summarized library information.")
numbered("Provide reports for inventory, members, borrowing, overdue, fines, and low-stock.")
numbered("Provide analytics for borrowing trends, book categories, and active members.")
numbered("Provide book searching and search suggestions.")
numbered("Allow authenticated users to access profile information.")
numbered("Store and retrieve library information using MySQL.")
numbered("Provide browser-based access.")
h3("4.3.2 Non-Functional Requirements")
p("The system shall address:")
bullet("Security - protected functions shall require authentication.")
bullet("Usability - the interface shall be clear and understandable.")
bullet("Performance - operations shall be processed within reasonable time.")
bullet("Reliability - the system shall maintain consistent operations.")
bullet("Availability - the deployed system shall be accessible via web browser.")
bullet("Maintainability - the system shall support future modification.")
bullet("Scalability - the system shall accommodate growing data.")
bullet("Compatibility - the system shall operate through modern web browsers.")
bullet("Data Integrity - the system shall maintain accurate records.")
bullet("Responsiveness - the interface shall adapt to different screen sizes.")
h3("4.3.3 Hardware Requirements")
bullet("A computer or compatible device")
bullet("Adequate storage")
bullet("Stable network or Internet connection")
bullet("Server or cloud infrastructure")
h3("4.3.4 Software Requirements")
bullet("Python programming language")
bullet("Flask web framework")
bullet("MySQL database management system")
bullet("MySQL Connector/Python")
bullet("HTML, CSS, Bootstrap, JavaScript")
bullet("MySQL Workbench")
bullet("Modern web browser")

h2("4.4 Functional Requirements")
add_table(
    ["ID", "Requirement"],
    [
        ["FR-01", "Login function verifying credentials"],
        ["FR-02", "Authenticated session management"],
        ["FR-03", "Prevent unauthenticated access"],
        ["FR-04", "Book management (add, view, update, search)"],
        ["FR-05", "Store book information"],
        ["FR-06", "Prevent duplicate ISBN"],
        ["FR-07", "Display book availability"],
        ["FR-08", "Search suggestions"],
        ["FR-09", "Member management (register, view, update)"],
        ["FR-10", "Store member information"],
        ["FR-11", "Prevent duplicate member registration"],
        ["FR-12", "Make member information available for borrowing"],
        ["FR-13", "Initiate borrowing transaction"],
        ["FR-14", "Verify member and book availability"],
        ["FR-15", "Record borrowing details"],
        ["FR-16", "Reduce book quantity after borrowing"],
        ["FR-17", "Process returned books"],
        ["FR-18", "Update transaction and increase quantity"],
        ["FR-19", "Retain transaction history"],
        ["FR-20", "Identify overdue transactions"],
        ["FR-21", "Process fine information"],
        ["FR-22", "Make overdue and fine information available"],
        ["FR-23", "Maintain book quantities"],
        ["FR-24", "Identify low-stock books"],
        ["FR-25", "Maintain borrowing records"],
        ["FR-26", "View historical transactions"],
        ["FR-27", "Make transaction data available for reports"],
        ["FR-28", "Provide authenticated dashboard"],
        ["FR-29", "Dashboard navigation"],
        ["FR-30", "Generate reports"],
        ["FR-31", "Provide analytics"],
        ["FR-32", "Book search"],
        ["FR-33", "Search suggestions"],
        ["FR-34", "User profile access"],
        ["FR-35", "Centralized MySQL database"],
        ["FR-36", "Insert and update records"],
        ["FR-37", "Maintain database relationships"],
        ["FR-38", "Browser-based access"],
    ]
)

h2("4.5 Non-Functional Requirements")
add_table(
    ["ID", "Requirement"],
    [
        ["NFR-01", "Authentication required for protected functions"],
        ["NFR-02", "Input validation and database constraints"],
        ["NFR-03", "Session termination on logout"],
        ["NFR-04", "Clear and consistent interface"],
        ["NFR-05", "Reasonable response time"],
        ["NFR-06", "Consistent operation"],
        ["NFR-07", "Browser-based availability"],
        ["NFR-08", "Structured maintainable design"],
        ["NFR-09", "Scalability"],
        ["NFR-10", "Browser compatibility"],
        ["NFR-11", "Data integrity"],
        ["NFR-12", "Accurate book quantities"],
        ["NFR-13", "Responsive interface"],
    ]
)

h2("4.6 Use Case Analysis")
h3("4.6.1 System Actors")
p("The main actor is the Library User, representing authorized library personnel.")
h3("4.6.2 Major Use Cases")
p("The major use cases include:")
numbered("Login - Access protected system functions")
numbered("Logout - End session")
numbered("Manage Books - Add, view, update, search book records")
numbered("Manage Members - Register, view, update member records")
numbered("Borrow Book - Record borrowing transaction")
numbered("Return Book - Record returned book")
numbered("Manage Overdue Books - Identify overdue transactions")
numbered("Process Fines - Determine and track fines")
numbered("Monitor Inventory - Monitor book quantities")
numbered("View Borrowing History - View previous transactions")
numbered("View Dashboard - Summarized library information")
numbered("Generate Reports - Obtain library reports")
numbered("View Analytics - Examine summarized information")
numbered("Search Books - Search for books")
numbered("View Profile - Access profile information")

h2("4.7 Use Case Diagram")
p("Figure 4.1: Use Case Diagram of the Web-Based Library Management System")
p("The diagram illustrates the main use cases available to an authorized library user: Login, Logout, Manage Books, Manage Members, Borrow Book, Return Book, Manage Overdue Books, Process Fines, Monitor Inventory, View Borrowing History, View Dashboard, Generate Reports, View Analytics, Search Books, and View Profile.")

h2("4.8 Data Flow Diagram")
h3("4.8.1 Context-Level Data Flow Diagram")
p("Figure 4.2: Context-Level Data Flow Diagram")
p("At the context level, the entire system is represented as a single process. The Library User is the external entity.")
h3("4.8.2 Level 1 Data Flow Diagram")
p("Figure 4.3: Level 1 Data Flow Diagram")
p("The Level 1 DFD decomposes the main system into major processes and shows the data stores.")
h3("4.8.3 Data Stores")
bullet("D1 - Users: User account and role information")
bullet("D2 - Books: Book details and available quantities")
bullet("D3 - Members: Registered library member information")
bullet("D4 - Borrow Records: Borrowing, due-date, return, and status information")

h2("4.9 Database Design")
h3("4.9.1 Database Schema")
p("Table 4.1: Users")
add_table(
    ["Field", "Data Type", "Key/Constraint"],
    [
        ["id", "INT", "Primary Key"],
        ["username", "VARCHAR", "Unique"],
        ["password", "VARCHAR", "Not Null"],
        ["role", "ENUM", "admin, librarian"],
    ]
)
p("Table 4.2: Books")
add_table(
    ["Field", "Data Type", "Key/Constraint"],
    [
        ["id", "INT", "Primary Key"],
        ["title", "VARCHAR", "Not Null"],
        ["author", "VARCHAR", "Not Null"],
        ["isbn", "VARCHAR", "Unique"],
        ["category", "VARCHAR", "-"],
        ["quantity", "INT", "-"],
    ]
)
p("Table 4.3: Members")
add_table(
    ["Field", "Data Type", "Key/Constraint"],
    [
        ["id", "INT", "Primary Key"],
        ["fullname", "VARCHAR", "Not Null"],
        ["email", "VARCHAR", "-"],
        ["phone", "VARCHAR", "-"],
    ]
)
p("Table 4.4: Borrow Records")
add_table(
    ["Field", "Data Type", "Key/Constraint"],
    [
        ["id", "INT", "Primary Key"],
        ["member_id", "INT", "Foreign Key"],
        ["book_id", "INT", "Foreign Key"],
        ["borrow_date", "DATE", "-"],
        ["due_date", "DATE", "-"],
        ["return_date", "DATE", "-"],
        ["status", "VARCHAR", "-"],
    ]
)
h3("4.9.2 Table Relationships")
bullet("Members -> Borrow Records: One member can have many borrowing records.")
bullet("Books -> Borrow Records: One book can appear in many borrowing records.")

h2("4.10 Entity Relationship Diagram")
p("Figure 4.4: Entity Relationship Diagram")
p("The ERD shows the Users, Books, Members, and Borrow Records tables with their relationships.")

h2("4.11 System Architecture")
h3("4.11.1 Overall System Architecture")
p("Figure 4.5: System Architecture")
p("The architecture consists of the user interface layer, Flask application layer, and MySQL database layer.")
h3("4.11.2 User Interface Layer")
p("Accessed through a web browser, implemented using HTML, CSS, Bootstrap, and JavaScript.")
h3("4.11.3 Flask Application Layer")
p("Handles routes, authentication, business logic, validation, database communication, and calculations.")
h3("4.11.4 MySQL Database Layer")
p("Provides persistent storage for users, books, members, and borrow records.")
h3("4.11.5 Advantages of the System Architecture")
bullet("Separation of responsibilities")
bullet("Centralized data management")
bullet("Data consistency")
bullet("Maintainability")
bullet("Scalability")
bullet("Accessibility")
bullet("Security")

h2("4.12 User Interface Design")
add_table(
    ["Page", "Purpose"],
    [
        ["Login Page", "Authenticate users"],
        ["Dashboard", "Display library statistics"],
        ["Books Page", "Manage book records"],
        ["Members Page", "Manage member records"],
        ["Borrow Page", "Record borrowing transactions"],
        ["Return Page", "Process returned books"],
        ["Overdue Page", "Display overdue transactions"],
        ["Fines Page", "Display fine information"],
        ["Reports Page", "Generate library reports"],
        ["Analytics Page", "Display borrowing trends"],
        ["Profile Page", "Display user profile"],
    ]
)

h2("4.13 Chapter Summary")
p("This chapter presented the analysis and design of the Web-Based Library Management System.")

# ============ CHAPTER 5 ============
pb()
h1("CHAPTER FIVE: IMPLEMENTATION AND TESTING")

h2("5.1 Introduction")
p("This chapter presents the implementation and testing of the Web-Based Library Management System. It describes how the requirements and designs presented in Chapter Four were transformed into a working web application.")

h2("5.2 Implementation Overview")
p("The implementation of the Web-Based Library Management System involved transforming the system requirements and design into a functional web application. The system was implemented incrementally using Python and Flask for the application layer, MySQL for data storage, and HTML, CSS, Bootstrap, and JavaScript for the user interface.")
h3("5.2.1 Implementation Objectives")
numbered("Create the MySQL database and tables.")
numbered("Implement the Flask application backend.")
numbered("Implement user authentication and session management.")
numbered("Implement book and member management modules.")
numbered("Implement borrowing and returning modules with automatic stock updates.")
numbered("Implement overdue and fine management.")
numbered("Implement inventory and low-stock monitoring.")
numbered("Implement dashboard, reports, and analytics.")
numbered("Deploy the application to a cloud hosting environment.")
numbered("Test the system against its functional requirements.")

h2("5.3 Development Environment Setup")
h3("5.3.1 Hardware Environment")
add_table(
    ["Component", "Specification"],
    [
        ["Computer", "Windows-based laptop/desktop"],
        ["Processor", "Intel Core i5 or equivalent"],
        ["RAM", "8 GB minimum"],
        ["Storage", "256 GB SSD"],
        ["Network", "Stable internet connection"],
    ]
)
h3("5.3.2 Software Environment")
add_table(
    ["Software", "Purpose"],
    [
        ["Windows 10/11", "Operating system"],
        ["Python 3.x", "Programming language"],
        ["Flask", "Web framework"],
        ["MySQL", "Database management system"],
        ["MySQL Connector/Python", "Database connectivity"],
        ["MySQL Workbench", "Database management"],
        ["VS Code / PyCharm", "Code editor"],
        ["Web Browser", "Testing and accessing the application"],
        ["Command Prompt (CMD)", "Running the Flask application"],
    ]
)

h2("5.4 Database Implementation")
p("The database was implemented using MySQL based on the database design presented in Section 4.9.")
h3("5.4.1 Database Creation")
p("The database was created using SQL statements to define the users, books, members, and borrow_records tables.")
h3("5.4.2 Sample Data")
p("Sample data inserted during testing included books such as Python Programming, Database Systems, and Computer Networks.")

h2("5.5 Flask Application Implementation")
p("The Flask application was implemented as the main processing component of the system.")
h3("5.5.1 Application Routes")
add_table(
    ["Route", "Function"],
    [
        ["/", "Login page"],
        ["/login", "Authenticate user"],
        ["/logout", "Terminate session"],
        ["/dashboard", "Display library statistics"],
        ["/books", "Book management"],
        ["/add_book", "Add new book"],
        ["/members", "Member management"],
        ["/add_member", "Register member"],
        ["/borrow", "Borrow book"],
        ["/return/<id>", "Return book"],
        ["/overdue", "Overdue transactions"],
        ["/fines", "Fine information"],
        ["/history", "Borrowing history"],
        ["/reports", "Library reports"],
        ["/analytics", "Analytics"],
        ["/profile", "User profile"],
    ]
)
h3("5.5.2 User Authentication Implementation")
p("The login route verifies user credentials against the users table. Successful authentication creates a session.")
h3("5.5.3 Book and Member Management Implementation")
p("Book and member management modules allow users to add, view, update, and search records while preventing duplicate entries.")
h3("5.5.4 Borrowing and Returning Implementation")
p("The borrowing module records transactions and reduces book quantity. The returning module updates the transaction and increases book quantity.")
h3("5.5.5 Overdue and Fine Management Implementation")
p("The system identifies overdue transactions by comparing due dates with the current date and calculates fines based on days overdue.")
h3("5.5.6 Dashboard, Reports, and Analytics Implementation")
p("The dashboard displays summary statistics. Reports and analytics are generated from stored transaction data.")

h2("5.6 System Integration")
p("After individual modules were developed, they were integrated into one application. The integrated system follows the architecture: User -> Web Browser -> Flask Application -> MySQL Database -> Flask Application -> Web Browser -> User.")

h2("5.7 System Testing Methodology")
p("System testing was conducted to determine whether the Web-Based Library Management System met the functional and non-functional requirements.")
h3("5.7.1 Testing Objectives")
numbered("Verify that system functions operate as required.")
numbered("Identify and correct errors.")
numbered("Verify correct data storage and retrieval.")
numbered("Verify relationships between records.")
numbered("Confirm borrowing and returning update quantities correctly.")
numbered("Verify overdue and fine management.")
numbered("Test reports and analytics.")
numbered("Evaluate usability and responsiveness.")
numbered("Verify authentication for protected functions.")
h3("5.7.2 Testing Levels")
add_table(
    ["Testing Level", "Description"],
    [
        ["Unit Testing", "Individual functions tested"],
        ["Integration Testing", "Combined modules tested"],
        ["Functional Testing", "System functions tested against requirements"],
        ["Database Testing", "Database operations verified"],
        ["Validation Testing", "Input validation tested"],
        ["Security Testing", "Authentication tested"],
        ["Usability Testing", "Interface clarity evaluated"],
        ["Performance Testing", "Response times observed"],
        ["Deployment Testing", "Cloud deployment tested"],
    ]
)

h2("5.8 Test Cases and Results")
h3("5.8.1 Authentication Test Cases")
add_table(
    ["Test ID", "Function", "Expected Result", "Status"],
    [
        ["TC-01", "Login (valid)", "User authenticated", "Pass"],
        ["TC-02", "Login (invalid)", "Error message displayed", "Pass"],
        ["TC-03", "Login (empty)", "Validation message displayed", "Pass"],
        ["TC-04", "Logout", "Session terminated", "Pass"],
        ["TC-05", "Protected page access", "Redirected to login", "Pass"],
    ]
)
h3("5.8.2 Book Management Test Cases")
add_table(
    ["Test ID", "Function", "Expected Result", "Status"],
    [
        ["TC-06", "Add Book", "Book saved and displayed", "Pass"],
        ["TC-07", "Duplicate ISBN", "Error message", "Pass"],
        ["TC-08", "View Books", "Books displayed", "Pass"],
        ["TC-09", "Update Book", "Book updated", "Pass"],
        ["TC-10", "Search Book", "Matching books displayed", "Pass"],
        ["TC-11", "Live Suggestions", "Suggestions appear", "Pass"],
        ["TC-12", "Low Stock", "Books below threshold displayed", "Pass"],
    ]
)
h3("5.8.3 Member Management Test Cases")
add_table(
    ["Test ID", "Function", "Expected Result", "Status"],
    [
        ["TC-13", "Register Member", "Member saved", "Pass"],
        ["TC-14", "Duplicate Member", "Error message", "Pass"],
        ["TC-15", "View Members", "Members displayed", "Pass"],
        ["TC-16", "Update Member", "Member updated", "Pass"],
    ]
)
h3("5.8.4 Borrowing and Returning Test Cases")
add_table(
    ["Test ID", "Function", "Expected Result", "Status"],
    [
        ["TC-17", "Borrow Book", "Record created, quantity reduced", "Pass"],
        ["TC-18", "Borrow (unavailable)", "Error message", "Pass"],
        ["TC-19", "Borrow (invalid member)", "Error message", "Pass"],
        ["TC-20", "Return Book", "Return recorded, quantity increased", "Pass"],
        ["TC-21", "Stock Update", "Quantity reflects transaction", "Pass"],
        ["TC-22", "Borrowing History", "Transactions displayed", "Pass"],
    ]
)
h3("5.8.5 Overdue and Fine Test Cases")
add_table(
    ["Test ID", "Function", "Expected Result", "Status"],
    [
        ["TC-23", "Overdue Detection", "Overdue transactions displayed", "Pass"],
        ["TC-24", "Fine Calculation", "Fines calculated", "Pass"],
        ["TC-25", "No Overdue", "Empty list displayed", "Pass"],
    ]
)
h3("5.8.6 Dashboard, Reports, and Analytics Test Cases")
add_table(
    ["Test ID", "Function", "Expected Result", "Status"],
    [
        ["TC-26", "Dashboard", "Statistics displayed", "Pass"],
        ["TC-27", "Reports", "Report data displayed", "Pass"],
        ["TC-28", "Analytics", "Trends displayed", "Pass"],
        ["TC-29", "Monthly Trends", "Monthly data displayed", "Pass"],
        ["TC-30", "Top Books", "Ranked list displayed", "Pass"],
    ]
)
h3("5.8.7 Database and Deployment Test Cases")
add_table(
    ["Test ID", "Function", "Expected Result", "Status"],
    [
        ["TC-31", "Insert Record", "Record stored in MySQL", "Pass"],
        ["TC-32", "Retrieve Record", "Data matches database", "Pass"],
        ["TC-33", "Update Record", "Database updated", "Pass"],
        ["TC-34", "Foreign Key", "Relationships maintained", "Pass"],
        ["TC-35", "Unique Constraint", "Duplicate rejected", "Pass"],
        ["TC-36", "Cloud Access", "Application loads", "Pass"],
        ["TC-37", "Cloud Login", "User authenticated", "Pass"],
        ["TC-38", "Cloud Database", "Data stored in hosted MySQL", "Pass"],
    ]
)

h2("5.9 Test Results Summary")
add_table(
    ["Test Category", "Total Tests", "Passed", "Failed", "Pass Rate"],
    [
        ["Authentication", "5", "5", "0", "100%"],
        ["Book Management", "7", "7", "0", "100%"],
        ["Member Management", "4", "4", "0", "100%"],
        ["Borrowing/Returning", "6", "6", "0", "100%"],
        ["Overdue/Fines", "3", "3", "0", "100%"],
        ["Dashboard/Reports/Analytics", "5", "5", "0", "100%"],
        ["Database", "5", "5", "0", "100%"],
        ["Deployment", "3", "3", "0", "100%"],
        ["TOTAL", "38", "38", "0", "100%"],
    ]
)

h2("5.10 System Evaluation")
p("The system evaluation confirmed that all 38 functional requirements (FR-01 to FR-38) and all 13 non-functional requirements (NFR-01 to NFR-13) were implemented and satisfied.")

h2("5.11 Implementation Challenges and Solutions")
add_table(
    ["Challenge", "Solution"],
    [
        ["Database connection errors", "Verified credentials and used error handling"],
        ["Session management issues", "Used Flask session with secret key"],
        ["Duplicate member registration", "Implemented validation before insert"],
        ["Stock inconsistency", "Used transactional updates"],
        ["Overdue date calculation", "Used SQL DATEDIFF and Python datetime"],
        ["Cloud deployment issues", "Configured environment variables"],
        ["Responsive design", "Used Bootstrap grid"],
    ]
)

h2("5.12 Chapter Summary")
p("This chapter presented the implementation and testing of the Web-Based Library Management System. A total of 38 test cases were executed across all major system functions, with a 100% pass rate.")

# ============ CHAPTER 6 ============
pb()
h1("CHAPTER SIX: CONCLUSION AND RECOMMENDATIONS")

h2("6.1 Introduction")
p("This chapter presents the conclusion and recommendations of the study on the development of a Web-Based Library Management System using Flask and MySQL.")

h2("6.2 Summary of the Study")
p("The study set out to develop and implement a web-based Library Management System that automates the management of library books, members, borrowing and returning transactions, and book inventory, while providing secure access to authorized library personnel.")

h2("6.3 Achievement of Objectives")
h3("6.3.1 Objective One: Centralized Database")
p("A centralized MySQL database was successfully designed and implemented with four main tables: users, books, members, and borrow_records.")
h3("6.3.2 Objective Two: Secure Authentication")
p("A login and logout mechanism was successfully implemented using Flask sessions.")
h3("6.3.3 Objective Three: Book and Member Management")
p("Book and member management modules were successfully implemented, allowing users to add, view, update, and search records while preventing duplicate registrations.")
h3("6.3.4 Objective Four: Borrowing, Returning, Overdue, and Fine Management")
p("The borrowing and returning modules were successfully implemented with automatic stock updates, overdue identification, and fine calculation.")
h3("6.3.5 Objective Five: Dashboard, Reports, Analytics, and Testing")
p("Dashboard, reporting, analytics, and low-stock monitoring features were implemented. A total of 38 test cases were executed with a 100% pass rate.")

h2("6.4 Summary of Findings")
numbered("Manual library management is inefficient.")
numbered("Computerized systems improve efficiency.")
numbered("Centralized data management is effective.")
numbered("Automated stock management works.")
numbered("Overdue and fine management can be automated.")
numbered("Reporting and analytics add value.")
numbered("Web-based access is practical.")
numbered("Security is important.")

h2("6.5 Conclusions")
numbered("The Web-Based Library Management System successfully addresses the identified problems.")
numbered("All five specific objectives were achieved.")
numbered("The system satisfies its functional and non-functional requirements.")
numbered("The Agile development approach was effective.")
numbered("The Flask and MySQL technology stack is suitable for web-based library management systems.")
numbered("Computerized library management improves efficiency, accuracy, and organization.")

h2("6.6 Recommendations")
h3("6.6.1 Recommendations for the Library")
numbered("Adopt the system for daily library operations.")
numbered("Train library personnel.")
numbered("Establish data management procedures.")
numbered("Provide reliable internet and hardware.")
numbered("Assign system administrators.")
h3("6.6.2 Recommendations for Future Development")
numbered("Implement automated email or SMS notifications.")
numbered("Add book reservation and hold management.")
numbered("Implement more detailed role-based permissions.")
numbered("Add audit logging.")
numbered("Implement automated database backups.")
numbered("Enhance security features.")
numbered("Add report export functionality.")
numbered("Integrate with other institutional systems.")
numbered("Develop a mobile application.")
numbered("Implement advanced analytics.")
h3("6.6.3 Recommendations for Further Research")
numbered("Conduct comparative studies.")
numbered("Investigate user satisfaction.")
numbered("Explore integration with digital libraries.")
numbered("Study scalability in larger environments.")
numbered("Examine security in cloud environments.")

h2("6.7 Contribution of the Study")
p("The study makes practical, academic, methodological, reference, and institutional contributions.")

h2("6.8 Limitations of the Study")
p("The study had limitations including internet dependency, hosting dependency, data accuracy, user training, security limitations, integration limitations, notification limitations, and infrastructure dependency.")

h2("6.9 Final Conclusion")
p("The Web-Based Library Management System developed in this project successfully addresses the challenges associated with manual and less-integrated library management approaches. All five specific objectives were achieved, all 38 functional requirements and 13 non-functional requirements were satisfied, and all 38 test cases passed successfully.")
p("The study recommends that the library adopt the system, train personnel, establish data management procedures, and provide reliable infrastructure.")

# ============ REFERENCES ============
pb()
h1("REFERENCES")
refs = [
    "Armstrong, M. (2020). Armstrong's handbook of performance management (7th ed.). Kogan Page.",
    "Barney, J. (1991). Firm resources and sustained competitive advantage. Journal of Management, 17(1), 99-120.",
    "Creswell, J. W., & Creswell, J. D. (2022). Research design (6th ed.). SAGE Publications.",
    "Dessler, G. (2020). Human resource management (16th ed.). Pearson.",
    "Kothari, C. R. (2004). Research methodology (2nd ed.). New Age International.",
    "Otoo, F. N. K. (2023). Human resource management practices and employee performance. Journal of Human Resource Management, 11(2), 45-58.",
    "Taherdoost, H. (2022). Sampling methods in research methodology. International Journal of Academic Research in Management, 11(1), 18-27.",
]
for ref in refs:
    para = doc.add_paragraph()
    para.paragraph_format.left_indent = Inches(0.5)
    para.paragraph_format.first_line_indent = Inches(-0.5)
    para.add_run(ref)

# ============ APPENDICES ============
pb()
h1("APPENDICES")

h2("Appendix A: User Interface Wireframes")
p("[Insert wireframe images here: Login, Dashboard, Books, Members, Borrow, Return, Overdue, Analytics]")

h2("Appendix B: Sample Database Records")
h3("B.1 Users Table")
add_table(
    ["id", "username", "password", "role"],
    [
        ["1", "admin", "admin123", "admin"],
        ["2", "librarian1", "lib123", "librarian"],
    ]
)
h3("B.2 Books Table")
add_table(
    ["id", "title", "author", "isbn", "category", "quantity"],
    [
        ["1", "Python Programming", "John Smith", "978-001", "Programming", "5"],
        ["2", "Database Systems", "Jane Doe", "978-002", "Computing", "3"],
        ["3", "Computer Networks", "Robert Brown", "978-003", "Networking", "4"],
    ]
)
h3("B.3 Members Table")
add_table(
    ["id", "fullname", "email", "phone"],
    [
        ["1", "Alice Wanjiru", "alice@example.com", "0712345678"],
        ["2", "Brian Otieno", "brian@example.com", "0723456789"],
    ]
)
h3("B.4 Borrow Records Table")
add_table(
    ["id", "member_id", "book_id", "borrow_date", "due_date", "return_date", "status"],
    [
        ["1", "1", "1", "2026-06-01", "2026-06-15", "NULL", "borrowed"],
        ["2", "2", "2", "2026-06-05", "2026-06-19", "2026-06-18", "returned"],
    ]
)

h2("Appendix C: Test Case Summary")
add_table(
    ["Test ID", "Function", "Status"],
    [
        ["TC-01", "Login (valid)", "Pass"],
        ["TC-02", "Login (invalid)", "Pass"],
        ["TC-03", "Login (empty)", "Pass"],
        ["TC-04", "Logout", "Pass"],
        ["TC-05", "Protected page access", "Pass"],
        ["TC-06", "Add Book", "Pass"],
        ["TC-07", "Duplicate ISBN", "Pass"],
        ["TC-08", "View Books", "Pass"],
        ["TC-09", "Update Book", "Pass"],
        ["TC-10", "Search Book", "Pass"],
        ["TC-11", "Live Suggestions", "Pass"],
        ["TC-12", "Low Stock", "Pass"],
        ["TC-13", "Register Member", "Pass"],
        ["TC-14", "Duplicate Member", "Pass"],
        ["TC-15", "View Members", "Pass"],
        ["TC-16", "Update Member", "Pass"],
        ["TC-17", "Borrow Book", "Pass"],
        ["TC-18", "Borrow Unavailable", "Pass"],
        ["TC-19", "Borrow Invalid Member", "Pass"],
        ["TC-20", "Return Book", "Pass"],
        ["TC-21", "Stock Update", "Pass"],
        ["TC-22", "Borrowing History", "Pass"],
        ["TC-23", "Overdue Detection", "Pass"],
        ["TC-24", "Fine Calculation", "Pass"],
        ["TC-25", "No Overdue", "Pass"],
        ["TC-26", "Dashboard", "Pass"],
        ["TC-27", "Reports", "Pass"],
        ["TC-28", "Analytics", "Pass"],
        ["TC-29", "Monthly Trends", "Pass"],
        ["TC-30", "Top Books", "Pass"],
        ["TC-31", "Insert Record", "Pass"],
        ["TC-32", "Retrieve Record", "Pass"],
        ["TC-33", "Update Record", "Pass"],
        ["TC-34", "Foreign Key", "Pass"],
        ["TC-35", "Unique Constraint", "Pass"],
        ["TC-36", "Cloud Access", "Pass"],
        ["TC-37", "Cloud Login", "Pass"],
        ["TC-38", "Cloud Database", "Pass"],
    ]
)

doc.save(output_path)
print("PART 3 DONE - Chapters 4, 5, 6, References, Appendices saved!")
print("")
print("=" * 60)
print("COMPLETE DOCUMENT CREATED!")
print("=" * 60)
print("Location: " + output_path)