#!/usr/bin/awk -f

# only for multiple data types in a single file

BEGIN   {
    hive_ID = " ";
    measurement = " ";
    print "hive\ttype\ttime\tvalue"
}

# if the second field is a slash then this is a header line 
# identifying a certain measurement from a certain hive
$2 == "/" {
    hive_ID = $1;
    measurement = $3;
    if ("Hint" == measurement)
        measurement = "Humidity";
}

# if there are 4 fields then this is a data row
NF == 4 {
    out_line = sprintf("%s\t%s\t%s\t%s", hive_ID, measurement, $2, $3)
    print out_line
}