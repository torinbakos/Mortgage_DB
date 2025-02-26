USE mortgage_management_system;

-- Here we define a function to convert our loan duration to decimal years
DELIMITER $$
CREATE FUNCTION ConvertDaysToYears(days INT)
    RETURNS DECIMAL(10, 2)
    DETERMINISTIC
BEGIN
    DECLARE years DECIMAL(10, 2);
    SET years = days / 365.25;
    RETURN years;
END$$
DELIMITER ;

-- We create a temporary table that an actuary might be interested in by aggregating data related to general risk
DROP TEMPORARY TABLE IF EXISTS MortgageRisk_Temp;
CREATE TEMPORARY TABLE MortgageRisk_Temp
(
    LoanID       INT PRIMARY KEY,
    LoanAmount   DECIMAL,
    Valuation    DECIMAL,
    CoverAmount  DECIMAL,
    InterestRate DECIMAL,
    LoanDuration DECIMAL(10, 2)
);

INSERT INTO MortgageRisk_Temp
SELECT ml.LoanID,
       ml.LoanAmount,
       prop.Valuation,
       ins.CoverAmount,
       ml.InterestRate,
       ConvertDaysToYears(DATEDIFF(ml.EndDate, ml.StartDate)) as LoanDuration
FROM MortgageLoans ml
         JOIN Properties prop ON ml.PropertyID = prop.PropertyID
         JOIN Insurance ins ON ml.LoanID = ins.LoanID;


-- Display result
SELECT *
FROM MortgageRisk_Temp;



-- Now we create a procedure to calculate a couple statistics from our temporary table
-- We also create a new temporary table to hold those results and drop any previous results as well
DROP TEMPORARY TABLE IF EXISTS Results;
CREATE TEMPORARY TABLE Results
(
    ColumnName VARCHAR(50),
    Average    DECIMAL(10, 2),
    StdDev     DECIMAL(10, 2)
);

DELIMITER $$
CREATE PROCEDURE Calculate_Stats()
BEGIN
    INSERT INTO Results (ColumnName, Average, StdDev)
    SELECT 'LoanAmount',
           AVG(LoanAmount),
           STDDEV(LoanAmount)
    FROM MortgageRisk_Temp;

    INSERT INTO Results (ColumnName, Average, StdDev)
    SELECT 'Valuation',
           AVG(Valuation),
           STDDEV(Valuation)
    FROM MortgageRisk_Temp;

    INSERT INTO Results (ColumnName, Average, StdDev)
    SELECT 'CoverAmount',
           AVG(CoverAmount),
           STDDEV(CoverAmount)
    FROM MortgageRisk_Temp;

    INSERT INTO Results (ColumnName, Average, StdDev)
    SELECT 'InterestRate',
           AVG(InterestRate),
           STDDEV(InterestRate)
    FROM MortgageRisk_Temp;

    INSERT INTO Results (ColumnName, Average, StdDev)
    SELECT 'LoanDuration',
           AVG(LoanDuration),
           STDDEV(LoanDuration)
    FROM MortgageRisk_Temp;
END$$
DELIMITER ;

-- Let's run our procedure and get the results by selecting all values from our temporary table
CALL Calculate_Stats();

SELECT *
FROM Results;

-- Here we create a trigger that effectively is a cascade delete, mostly to satisfy the trigger requirement
CREATE TRIGGER trg_CascadeDeleteLoan
    AFTER DELETE
    ON MortgageLoans
    FOR EACH ROW
BEGIN
    DELETE FROM Payments WHERE LoanID = OLD.LoanID;
    DELETE FROM Insurance WHERE LoanID = OLD.LoanID;
END;
