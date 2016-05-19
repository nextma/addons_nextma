FUNCTIONAL DETAILS / USER GUIDE
===============================

The aim of this module is to automaticly create third parts accounts number from partner creation or update.
As the partner is flag as customer or supplier, it generate the appropriate account number.
This is based on sequences to have benefits of prefix (E.g. root of account number), suffix and increments.
It uses ir.properties (witch already exist and are setted by default) as originals accounts numbers and duplicate it (keeping same parameters).

The sequence is a kind of parameter value. You can use partner fields (between {}) witch will be replaced bu corresponding values.
E.g. {ref} will be replaced by partner.ref (the code of partner)

You can also use modificators between pipes (|) modify the above replaced value.
Modificators are : 
 * rmspace : remove all spaces
 * rmponct : remove special characters
 * rmaccent : convert characters with accent in characeters with no accent
 * rmspe : keep only letters
 * truncate1 : keep first character
 * truncate2 : cut after second character
 * truncate4 : four first characters
 * truncate6 : six first characters
 * charnum : return number of alphabetic character (Eg: G is 07)
 * capitalize : transforme in upper case
 * lower : transforme in lower case
 * zfill2 : padding left with 0
 * zfill4 : padding left with 0 (until length = four)
 * zfill6 : padding left with 0 (until length = four)

Modificators can be joined.
E.g. {name|truncate4|capitalize}

