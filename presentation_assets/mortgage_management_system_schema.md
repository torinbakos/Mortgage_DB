classDiagram
direction BT
class Borrowers {
   varchar(50) FirstName
   varchar(50) LastName
   varchar(100) Email
   varchar(15) PhoneNumber
   varchar(250) Address
   int BorrowerID
}
class Guarantor_Cosigners {
   int BorrowerID
   varchar(50) FirstName
   varchar(50) LastName
   varchar(100) Email
   varchar(15) PhoneNumber
   varchar(250) Address
   int GuarantorID
}
class Insurance {
   varchar(100) InsuranceProvider
   varchar(100) PolicyNumber
   decimal(10) CoverAmount
   date StartDate
   date EndDate
   int LoanID
}
class MortgageLoans {
   int BorrowerID
   int PropertyID
   decimal(10) LoanAmount
   date StartDate
   date EndDate
   decimal(10) InterestRate
   varchar(50) LoanType
   varchar(50) Status
   int LoanID
}
class Payments {
   int LoanID
   decimal(10) AmountPaid
   date PaymentDate
   int PaymentID
}
class Properties {
   varchar(250) Address
   decimal(10) Valuation
   decimal(10) Size
   varchar(50) PropertyType
   int PropertyID
}

Guarantor_Cosigners  -->  Borrowers : BorrowerID
Insurance  -->  MortgageLoans : LoanID
MortgageLoans  -->  Borrowers : BorrowerID
MortgageLoans  -->  Properties : PropertyID
Payments  -->  MortgageLoans : LoanID
