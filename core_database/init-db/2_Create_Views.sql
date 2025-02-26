USE mortgage_management_system;

-- View for Mortgage Analyst
CREATE VIEW MortgageAnalystView AS
SELECT m.LoanID,
       m.BorrowerID,
       m.PropertyID,
       m.LoanAmount,
       m.StartDate,
       m.EndDate,
       m.InterestRate,
       m.LoanType,
       m.Status,
       b.FirstName,
       b.LastName,
       b.Email,
       p.Address          AS PropertyAddress,
       p.Valuation,
       SUM(pa.AmountPaid) AS TotalPaid
FROM MortgageLoans m
         JOIN Borrowers b ON m.BorrowerID = b.BorrowerID
         JOIN Properties p ON m.PropertyID = p.PropertyID
         LEFT JOIN Payments pa ON m.LoanID = pa.LoanID
GROUP BY m.LoanID;

-- View for Loan Officer
CREATE VIEW LoanOfficerView AS
SELECT m.LoanID,
       m.BorrowerID,
       m.LoanAmount,
       m.InterestRate,
       m.LoanType,
       b.FirstName,
       b.LastName,
       b.Email,
       b.PhoneNumber,
       -- Keep in mind not all loans need a Guarantor so there will null data in this view
       g.GuarantorID,
       g.FirstName AS GuarantorFirstName,
       g.LastName  AS GuarantorLastName
FROM MortgageLoans m
         JOIN Borrowers b ON m.BorrowerID = b.BorrowerID
         LEFT JOIN Guarantor_Cosigners g ON b.BorrowerID = g.BorrowerID;
