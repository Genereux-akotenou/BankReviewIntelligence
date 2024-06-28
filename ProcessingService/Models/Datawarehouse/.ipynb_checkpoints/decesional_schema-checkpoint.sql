-- Création des tables de dimensions

-- Table Dimension Region
CREATE TABLE Dimension_Region (
    Region_ID SERIAL PRIMARY KEY,
    Country VARCHAR(255) NOT NULL,
    Town VARCHAR(255) NOT NULL,
    CONSTRAINT region_unique UNIQUE (Country, Town)
);

-- Table Dimension Bank
CREATE TABLE Dimension_Bank (
    Bank_ID SERIAL PRIMARY KEY,
    Bank_Name VARCHAR(255),
    Bank_Phone_number VARCHAR(255),
    Bank_Address TEXT,
    Bank_Website VARCHAR(255),
    CONSTRAINT bank_unique UNIQUE (Bank_Name, Bank_Phone_number, Bank_Address, Bank_Website)
);

-- Table Dimension Reviewer
CREATE TABLE Dimension_Reviewer (
    Reviewer_ID SERIAL PRIMARY KEY,
    Reviewer_Name VARCHAR(255),
    Reviewer_Profil_Link TEXT,
    CONSTRAINT reviewer_unique UNIQUE (Reviewer_Name, Reviewer_Profil_Link)
);

-- Table Dimension Time
CREATE TABLE Dimension_Time (
    Time_ID SERIAL PRIMARY KEY,
    Week INT,
    Month INT,
    Year INT,
    CONSTRAINT time_unique UNIQUE (Week, Month, Year)
);

-- Table Dimension Topic
CREATE TABLE Dimension_Topic (
    Topic_ID SERIAL PRIMARY KEY,
    Label VARCHAR(255),
    CONSTRAINT topic_unique UNIQUE (Label)
);

-- Table Dimension SubTopic
CREATE TABLE Dimension_SubTopic (
    SubTopic_ID SERIAL PRIMARY KEY,
    Label VARCHAR(255),
    CONSTRAINT subtopic_unique UNIQUE (Label)
);

-- Table Dimension Sentiment
CREATE TABLE Dimension_Sentiment (
    Sentiment_ID SERIAL PRIMARY KEY,
    Type VARCHAR(255),
    CONSTRAINT sentiment_unique UNIQUE (Type)
);
-- Création de la table de faits

-- Table Fact Reviews
CREATE TABLE Fact_Reviews (
    Review_ID SERIAL PRIMARY KEY,
    Region_ID INT,
    Bank_ID INT,
    Reviewer_ID INT,
    Time_ID INT,
    Topic_ID INT,
    Sentiment_ID INT,
    SubTopic_ID INT,
    Count_Review INT,
    FOREIGN KEY (Bank_ID) REFERENCES Dimension_Bank(Bank_ID),
    FOREIGN KEY (Region_ID) REFERENCES Dimension_Region(Region_ID),
    FOREIGN KEY (Reviewer_ID) REFERENCES Dimension_Reviewer(Reviewer_ID),
    FOREIGN KEY (Time_ID) REFERENCES Dimension_Time(Time_ID),
    FOREIGN KEY (Topic_ID) REFERENCES Dimension_Topic(Topic_ID),
    FOREIGN KEY (Sentiment_ID) REFERENCES Dimension_Sentiment(Sentiment_ID),
    FOREIGN KEY (SubTopic_ID) REFERENCES Dimension_SubTopic(SubTopic_ID)
);
