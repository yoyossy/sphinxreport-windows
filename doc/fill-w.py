import random, os, re

x = len(c.frame.shortFileName())
filePath = c.mRelativeFileName[:-x] + "\\"
g.es(filePath)
g.es(len(c.frame.shortFileName()))
g.es(c.frame.shortFileName())
frw=open(filePath + "fill.sql", 'w')

#frw.write("-- creation de qq categories de partners\n")

for x in range(0,200,2):
    frw.write( "INSERT INTO %s VALUES ('gene%2i', '%s', %f)" % ("experiment1_data", x, "housekeeping", random.gauss( 41, 5)) )
    frw.write( ";\n")
    frw.write( "INSERT INTO %s VALUES ('gene%2i', '%s', %f)" % ("experiment1_data", x+1, "regulation", random.gauss( 11, 5)) )
    frw.write( ";\n")

for x in range(0,200,2):
    frw.write( "INSERT INTO %s VALUES ('gene%2i', '%s', %f)" % ("experiment2_data", x, "housekeeping", random.gauss( 40, 5)) )
    frw.write( ";\n")
    frw.write( "INSERT INTO %s VALUES ('gene%2i', '%s', %f)" % ("experiment2_data", x+1, "regulation", random.gauss( 10, 5)) )
    frw.write( ";\n")
