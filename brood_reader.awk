#!/usr/bin/awk -f

# for a file w/ a single data type

BEGIN   {
    hive_ID = " ";
    print "hive\ttime\tvalue"
}

# if the second field is a slash then this is a header line 
# identifying a certain measurement from a certain hive
$2 == "|" {
    hive_ID = $1;
}

# if there are 4 fields then this is a data row
NF == 4 {
    out_line = sprintf("%s\t%s\t%s", hive_ID, $2, $3)
    print out_line
}