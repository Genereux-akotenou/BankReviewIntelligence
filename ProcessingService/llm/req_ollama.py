import requests

url = 'http://localhost:11434/api/generate'


schema="""

Departments Table:

DepartmentID: Unique identifier for each department. Primary Key.
DepartmentName: Name of the department.
Location: Mailing address or location of the department.

Employees Table:

EmployeeID: Unique identifier for each employee. Primary Key.
FirstName: First name of the employee.
LastName: Last name of the employee.
DepartmentID: Foreign key referencing the department to which the employee belongs.
Position: Job position or title of the employee.
Salary: Salary of the employee.

"""

sql_schema = """
CREATE SCHEMA RewardsProgram; 
CREATE TABLE Customer ( 
    CustomerID INT NOT NULL AUTO_INCREMENT, 
    FirstName VARCHAR(50) NOT NULL, 
    LastName VARCHAR(50) NOT NULL, 
    Email VARCHAR(100) UNIQUE NOT NULL, 
    Phone VARCHAR(20) UNIQUE, 
    DateOfBirth DATE, 
    PRIMARY KEY (CustomerID)
); 
CREATE TABLE Membership ( 
    MembershipID INT NOT NULL AUTO_INCREMENT, 
    MembershipType VARCHAR(50) NOT NULL, 
    DiscountPercentage DECIMAL(5, 2) NOT NULL, 
    ValidFrom DATETIME, 
    ValidTo DATETIME, 
    CustomerID INT NOT NULL, 
    PRIMARY KEY (MembershipID), 
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID)
);
CREATE TABLE Transaction ( 
    TransactionID INT NOT NULL AUTO_INCREMENT, 
    TransactionDate TIMESTAMP, 
    TotalAmount DECIMAL(10, 2) NOT NULL, 
    CustomerID INT NOT NULL, 
    PRIMARY KEY (TransactionID), 
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID)
);
CREATE TABLE TransactionDetail ( 
    TransactionDetailID INT NOT NULL AUTO_INCREMENT, 
    TransactionID INT NOT NULL, 
    ProductID INT NOT NULL, 
    Quantity INT NOT NULL, 
    UnitPrice DECIMAL(10, 2) NOT NULL, 
    PRIMARY KEY (TransactionDetailID), 
    FOREIGN KEY (TransactionID) REFERENCES Transaction(TransactionID), 
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
);
CREATE TABLE Product ( 
    ProductID INT NOT NULL AUTO_INCREMENT, 
    ProductName VARCHAR(100) NOT NULL, 
    UnitPrice DECIMAL(10, 2) NOT NULL, 
    AvailableQuantity INT NOT NULL, 
    CreatedDate DATETIME, 
    PRIMARY KEY (ProductID)
);
"""

data = {
    "model": "llama3",
    "prompt": "Below are sql tables descriptions paired with instruction that describes a task. Using valid sql, write a response that appropriately completes the request for the provided tables. Give just the query, no explanation, only the sql query. ###Instruction: Can you list the top 3 departments with the highest average salary? ### Input:" + schema,
    "stream": False
}

data2 = {
    "model": "llama3",
    "prompt": "Below are sql tables schemas paired with instruction that describes a task. Using valid sql, write a response that appropriately completes the request for the provided tables. Give just the query, no explanation, only the sql query. ###Instruction: How many transactions were made by a customer named EWINSOU in April? ### Input:" + sql_schema,
    "stream": False
}
data3 = {
    "model": "llama3",
    "prompt": "Extract topic from thhis review 'I hat thiis bank. I wouldnot recommend. Thay offer service online and to create accountwe have to come in their agency. '. And output on this format: " + "{primary_topic: ['xxx', 'xxx'], detailed_topic: ['':[]], 'sentiment':[primary_topic1:Positive, ...:Negative, ...:Neutre]}",
    "stream": False
}

response = requests.post(url, json=data3)

if response.status_code == 200:
    response_data = response.json()
    
    api_response = response_data.get('response', 'No response field found')
    print("SQL Query: ")
    print(api_response)

else:
    print(f"Failed to retrieve data, status code {response.status_code}")

