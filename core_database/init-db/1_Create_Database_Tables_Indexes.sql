-- Here we create our database if it doesn't already exist, and then we activate said DB before creating our tables
CREATE DATABASE IF NOT EXISTS mortgage_management_system;

USE mortgage_management_system;

-- This is a fairly skeletal conceptualization of a Mortgage Management System
-- There are many elements to the mortgage lifecycle and many different players in the space with different requirements
-- This system is closer to what a bank that purchases mortgages for securitization but doesn't write them would need
-- There is no data included related to securitization, as this is intended to be a pool of mortgages which have not yet been bundled

CREATE USER IF NOT EXISTS 'main_user'@'%' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON *.* TO 'main_user'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;

-- Here we create our tables as defined in the Schema
-- We also create the related indexes immediately after to help with clarity
CREATE TABLE Borrowers
(
    BorrowerID  INT AUTO_INCREMENT PRIMARY KEY,
    FirstName   VARCHAR(50)  NOT NULL,
    LastName    VARCHAR(50)  NOT NULL,
    Email       VARCHAR(100) NOT NULL,
    PhoneNumber VARCHAR(15)  NOT NULL,
    Address     VARCHAR(250) NOT NULL
);

CREATE INDEX idx_Borrowers_PhoneNumber ON Borrowers (PhoneNumber);

CREATE TABLE Properties
(
    PropertyID   INT AUTO_INCREMENT PRIMARY KEY,
    Address      VARCHAR(250) NOT NULL UNIQUE,
    Valuation    DECIMAL      NOT NULL,
    Size         DECIMAL      NOT NULL,
    PropertyType VARCHAR(50)  NOT NULL
);

CREATE INDEX idx_Properties_Address ON Properties (Address);


CREATE TABLE MortgageLoans
(
    LoanID       INT AUTO_INCREMENT PRIMARY KEY,
    BorrowerID   INT         NOT NULL,
    PropertyID   INT         NOT NULL,
    LoanAmount   DECIMAL     NOT NULL,
    StartDate    DATE        NOT NULL,
    EndDate      DATE        NOT NULL,
    InterestRate DECIMAL     NOT NULL,
    LoanType     VARCHAR(50) NOT NULL,
    Status       VARCHAR(50) NOT NULL,
    FOREIGN KEY (BorrowerID) REFERENCES Borrowers (BorrowerID) ON DELETE CASCADE,
    FOREIGN KEY (PropertyID) REFERENCES Properties (PropertyID) ON DELETE CASCADE
);
-- This is probably excessive index implementation, but it is also the most important table
CREATE INDEX idx_MortgageLoans_BorrowerID ON MortgageLoans (BorrowerID);
CREATE INDEX idx_MortgageLoans_PropertyID ON MortgageLoans (PropertyID);
CREATE INDEX idx_MortgageLoans_StartDate ON MortgageLoans (StartDate);
CREATE INDEX idx_MortgageLoans_EndDate ON MortgageLoans (EndDate);
CREATE INDEX idx_MortgageLoans_LoanType ON MortgageLoans (LoanType);
CREATE INDEX idx_MortgageLoans_Status ON MortgageLoans (Status);


CREATE TABLE Payments
(
    PaymentID   INT AUTO_INCREMENT PRIMARY KEY,
    LoanID      INT     NOT NULL,
    AmountPaid  DECIMAL NOT NULL,
    PaymentDate DATE    NOT NULL,
    FOREIGN KEY (LoanID) REFERENCES MortgageLoans (LoanID) ON DELETE CASCADE
);
CREATE INDEX idx_Payments_LoanID ON Payments (LoanID);


CREATE TABLE Guarantor_Cosigners
(
    GuarantorID INT AUTO_INCREMENT PRIMARY KEY,
    BorrowerID  INT          NOT NULL,
    FirstName   VARCHAR(50)  NOT NULL,
    LastName    VARCHAR(50)  NOT NULL,
    Email       VARCHAR(100) NOT NULL,
    PhoneNumber VARCHAR(15)  NOT NULL,
    Address     VARCHAR(250) NOT NULL,
    FOREIGN KEY (BorrowerID) REFERENCES Borrowers (BorrowerID) ON DELETE CASCADE
);
CREATE INDEX idx_Guarantor_Cosigners_BorrowerID ON Guarantor_Cosigners (BorrowerID);


CREATE TABLE Insurance
(
    LoanID            INT AUTO_INCREMENT PRIMARY KEY,
    InsuranceProvider VARCHAR(100) NOT NULL,
    PolicyNumber      VARCHAR(100) NOT NULL UNIQUE,
    CoverAmount       DECIMAL      NOT NULL,
    StartDate         DATE         NOT NULL,
    EndDate           DATE         NOT NULL,
    FOREIGN KEY (LoanID) REFERENCES MortgageLoans (LoanID) ON DELETE CASCADE
);
CREATE INDEX idx_Insurance_PolicyNumber ON Insurance (PolicyNumber);


