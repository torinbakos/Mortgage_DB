USE mortgage_management_system;

-- This query retrieves each borrower along with the count of mortgage loans they have
SELECT b.BorrowerID, CONCAT(b.FirstName, ' ', b.LastName) AS FullName, COUNT(m.LoanID) AS TotalLoans
FROM Borrowers b
         LEFT JOIN MortgageLoans m ON b.BorrowerID = m.BorrowerID
GROUP BY b.BorrowerID;


-- This query calculates the average and total loan amounts categorized by the property type
SELECT p.PropertyType, AVG(m.LoanAmount) AS AverageLoanAmount, SUM(m.LoanAmount) AS TotalLoanAmount
FROM MortgageLoans m
         JOIN Properties p ON m.PropertyID = p.PropertyID
GROUP BY p.PropertyType;

-- Utilizes a window function to rank properties based on their valuation within each property type category
SELECT PropertyID,
       Address,
       Valuation,
       PropertyType,
       RANK() OVER (PARTITION BY PropertyType ORDER BY Valuation DESC) AS ValuationRank
FROM Properties;

-- This query displays the most recent payment details for each loan
SELECT m.LoanID, b.FirstName, b.LastName, p.AmountPaid, p.PaymentDate
FROM Payments p
         JOIN MortgageLoans m ON p.LoanID = m.LoanID
         JOIN Borrowers b ON m.BorrowerID = b.BorrowerID
WHERE p.PaymentID IN (SELECT MAX(PaymentID)
                      FROM Payments
                      GROUP BY LoanID);

-- Calculates the current balance for each loan by subtracting the total amount paid from the original loan amount
SELECT m.LoanID,
       m.LoanAmount,
       SUM(p.AmountPaid)                  AS TotalPaid,
       (m.LoanAmount - SUM(p.AmountPaid)) AS CurrentBalance
FROM MortgageLoans m
         JOIN Payments p ON m.LoanID = p.LoanID
GROUP BY m.LoanID, m.LoanAmount;

-- Identifies the top 5 borrowers who have taken the largest sum of loan amounts
SELECT b.BorrowerID, CONCAT(b.FirstName, ' ', b.LastName) AS FullName, SUM(m.LoanAmount) AS TotalLoanAmount
FROM Borrowers b
         JOIN MortgageLoans m ON b.BorrowerID = m.BorrowerID
GROUP BY b.BorrowerID, CONCAT(b.FirstName, ' ', b.LastName)
ORDER BY TotalLoanAmount DESC
LIMIT 5;

-- Analyzes the distribution of mortgage loans over the years, providing insight into the trend of loan disbursement
SELECT YEAR(m.StartDate) AS LoanYear, COUNT(*) AS TotalLoans, SUM(m.LoanAmount) AS TotalLoanAmount
FROM MortgageLoans m
GROUP BY YEAR(m.StartDate);

-- Computes the average valuation of properties grouped by their type to give an overview of property value distribution
SELECT PropertyType, AVG(Valuation) AS AverageValuation
FROM Properties
GROUP BY PropertyType;

-- Provides a count of loans and the average loan amount per borrower
SELECT b.BorrowerID,
       CONCAT(b.FirstName, ' ', b.LastName) AS FullName,
       COUNT(m.LoanID)                      AS LoanCount,
       AVG(m.LoanAmount)                    AS AverageLoanAmount
FROM Borrowers b
         JOIN MortgageLoans m ON b.BorrowerID = m.BorrowerID
GROUP BY b.BorrowerID;

-- Identifies properties that are linked to more than one mortgage loan
SELECT p.PropertyID, p.Address, COUNT(m.LoanID) AS MortgageCount
FROM Properties p
         JOIN MortgageLoans m ON p.PropertyID = m.PropertyID
GROUP BY p.PropertyID, p.Address
HAVING COUNT(m.LoanID) > 1;


-- Analyzes the trend in the number of loans issued and the total loan amount disbursed per year
SELECT YEAR(m.StartDate) AS YearIssued,
       COUNT(m.LoanID)   AS TotalLoansIssued,
       SUM(m.LoanAmount) AS TotalAmountIssued
FROM MortgageLoans m
GROUP BY YEAR(m.StartDate)
ORDER BY YearIssued;


-- Lists the number of loans that have missed payments, categorized by the month of the loan start date
SELECT YEAR(m.StartDate) AS Year, MONTH(m.StartDate) AS Month, COUNT(m.LoanID) AS DelinquentLoans
FROM MortgageLoans m
         JOIN Payments p ON m.LoanID = p.LoanID
WHERE m.LoanAmount > (SELECT SUM(p.AmountPaid) FROM Payments p WHERE p.LoanID = m.LoanID)
GROUP BY YEAR(m.StartDate), MONTH(m.StartDate)
ORDER BY Year, Month;


-- Utilizes a window function to compute the cumulative sum of loan amounts over time
SELECT m.LoanID,
       m.StartDate,
       m.LoanAmount,
       SUM(m.LoanAmount) OVER (ORDER BY m.StartDate ASC) AS CumulativeLoanAmount
FROM MortgageLoans m
ORDER BY m.StartDate;

-- Identifies borrowers whose loan amounts represent a high percentage of their property valuation
SELECT m.BorrowerID,
       b.FirstName,
       b.LastName,
       m.LoanAmount,
       p.Valuation,
       (m.LoanAmount / p.Valuation) AS LoanToValueRatio
FROM MortgageLoans m
         JOIN Properties p ON m.PropertyID = p.PropertyID
         JOIN Borrowers b ON m.BorrowerID = b.BorrowerID
WHERE (m.LoanAmount / p.Valuation) > 0.8
ORDER BY LoanToValueRatio DESC;

