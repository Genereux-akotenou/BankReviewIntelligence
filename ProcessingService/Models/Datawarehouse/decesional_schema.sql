-- Création des tables de dimensions

-- Table Dimension Region
CREATE TABLE Dimension_Region (
    Region_ID INT PRIMARY KEY AUTO_INCREMENT,
    Country VARCHAR(255) NOT NULL,
    Town VARCHAR(255) NOT NULL
    UNIQUE (Country, Town)
);

-- Table Dimension Bank
CREATE TABLE Dimension_Bank (
    Bank_ID INT PRIMARY KEY AUTO_INCREMENT,
    Bank_Name VARCHAR(255) NOT NULL,
    Bank_Phone_number VARCHAR(50),
    Bank_Address VARCHAR(255),
    Bank_Website VARCHAR(255)
);

-- Table Dimension Reviewer
CREATE TABLE Dimension_Reviewer (
    Reviewer_ID INT PRIMARY KEY AUTO_INCREMENT,
    Reviewer_Name VARCHAR(255) NOT NULL,
    Reviewer_Profil_Link VARCHAR(255)
);

-- Table Dimension Time
CREATE TABLE Dimension_Time (
    Time_ID INT PRIMARY KEY AUTO_INCREMENT,
    Week INT,
    Month INT,
    Year INT
);

-- Table Dimension Topic
CREATE TABLE Dimension_Topic (
    Topic_ID INT PRIMARY KEY AUTO_INCREMENT,
    Label VARCHAR(255) NOT NULL
);

-- Table Dimension SubTopic
CREATE TABLE Dimension_SubTopic (
    SubTopic_ID INT PRIMARY KEY AUTO_INCREMENT,
    Label VARCHAR(255) NOT NULL
);

-- Table Dimension Sentiment
CREATE TABLE Dimension_Sentiment (
    Sentiment_ID INT PRIMARY KEY AUTO_INCREMENT,
    Positive_Sentiment VARCHAR(255),
    Negative_Sentiment VARCHAR(255),
    Neutral_Sentiment VARCHAR(255)
);

-- Création de la table de faits

-- Table Fact Reviews
CREATE TABLE Fact_Reviews (
    Review_ID INT PRIMARY KEY AUTO_INCREMENT,
    Bank_ID INT,
    Reviewer_ID INT,
    Time_ID INT,
    Topic_ID INT,
    Sentiment_ID INT,
    SubTopic_ID INT,
    Count_Review INT,
    FOREIGN KEY (Bank_ID) REFERENCES Dimension_Bank(Bank_ID),
    FOREIGN KEY (Reviewer_ID) REFERENCES Dimension_Reviewer(Reviewer_ID),
    FOREIGN KEY (Time_ID) REFERENCES Dimension_Time(Time_ID),
    FOREIGN KEY (Topic_ID) REFERENCES Dimension_Topic(Topic_ID),
    FOREIGN KEY (Sentiment_ID) REFERENCES Dimension_Sentiment(Sentiment_ID),
    FOREIGN KEY (SubTopic_ID) REFERENCES Dimension_SubTopic(SubTopic_ID)
);
