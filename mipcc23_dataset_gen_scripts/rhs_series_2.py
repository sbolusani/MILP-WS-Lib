#!/usr/bin/python3

import sys, getopt, csv

def main(argv):
   cfile = ""
   Afile = ""
   bfile = ""
   lfile = ""
   ufile = ""

   try:
      opts, args = getopt.getopt(argv,"hc:A:b:l:u::",["cfile=","Afile=","bfile=","lfile=","ufile="])
   except getopt.GetoptError:
      print("parse_synthetic.py -c <cfile> -A <Afile> -b <bfile> -l <lfile> -u <ufile>")
      sys.exit(2)

   for opt, arg in opts:
      if opt == "-h":
         print("parse_synthetic.py -c <cfile> -A <Afile> -b <bfile> -l <lfile> -u <ufile>")
         sys.exit()
      elif opt in ("-c", "--cfile"):
         cfile = arg
      elif opt in ("-A", "--Afile"):
         Afile = arg
      elif opt in ("-b", "--bfile"):
         bfile = arg
      elif opt in ("-l", "--lfile"):
         lfile = arg
      elif opt in ("-u", "--ufile"):
         ufile = arg

   print("c file: ", cfile)
   print("A file: ", Afile)
   print("b file: ", bfile)
   print("l file: ", lfile)
   print("u file: ", ufile)

   numrows = 250
   numcontcols = 500
   numbincols = 500
   numinsts = 1000

   c = [0.0]*numcontcols
   with open(cfile) as f:
      lines = csv.DictReader(f, delimiter=';')
      for line in lines:
         if len(line) != numcontcols+1:
            print("Incorrect cost vector length!")
            sys.exit()
         for i in range(numcontcols):
            c[i] = float(line[str(i+1)])

   A = []
   rownum = 0
   with open(Afile) as f:
      lines = csv.DictReader(f, delimiter=';')
      for line in lines:
         if len(line) != numcontcols+1:
            print("Incorrect A matrix number of continuous columns!")
            sys.exit()
         newrow = [0.0]*numcontcols
         for i in range(numcontcols):
            newrow[i] = float(line[str(i+1)])
         A.append(newrow)
         rownum += 1
      if rownum != numrows:
         print("Incorrect A matrix number of rows!")
         sys.exit()

   l = [0.0]*numcontcols
   with open(lfile) as f:
      lines = csv.DictReader(f, delimiter=';')
      for line in lines:
         if len(line) != numcontcols+1:
            print("Incorrect lower bounds vector length!")
            sys.exit()
         for i in range(numcontcols):
            l[i] = float(line[str(i+1)])

   u = [0.0]*numcontcols
   with open(ufile) as f:
      lines = csv.DictReader(f, delimiter=';')
      for line in lines:
         if len(line) != numcontcols+1:
            print("Incorrect upper bounds vector length!")
            sys.exit()
         for i in range(numcontcols):
            u[i] = float(line[str(i+1)])

   b = []
   instnum = 0
   with open(bfile) as f:
      lines = csv.DictReader(f, delimiter=';')
      for line in lines:
         if len(line) != numrows+1:
            print("Incorrect RHS vector length!")
            sys.exit()
         newrhs = [0.0]*numrows
         for i in range(numrows):
            newrhs[i] = float(line[str(i+1)])
         b.append(newrhs)
         instnum += 1
      if instnum != numinsts:
         print("Incorrect number of perturbations of RHS vector!")
         sys.exit()

   for i in range(numinsts):
      outputfile = "synthetic_"+str(i+1)+".dat"
      print("Writing data file: ", outputfile)
      of = open(outputfile, "w")
      of.write("data;\n\n")

      of.write("param numrows := "+str(numrows)+";\n")
      of.write("param numcontcols := "+str(numcontcols)+";\n")
      of.write("param numbincols := "+str(numbincols)+";\n\n")

      of.write("param c :=\n")
      for j in range(numcontcols):
         of.write("   "+str(j)+"   "+str(c[j])+"\n")
      of.write(";\n\n")

      of.write("param A :=\n")
      for j in range(numrows):
         for k in range(numcontcols):
            of.write("   "+str(j)+" "+str(k)+"   "+str(A[j][k])+"\n")
      of.write(";\n\n")

      of.write("param b :=\n")
      for j in range(numrows):
         of.write("   "+str(j)+"   "+str(b[i][j])+"\n")
      of.write(";\n\n")

      of.write("param l :=\n")
      for j in range(numcontcols):
         of.write("   "+str(j)+"   "+str(l[j])+"\n")
      of.write(";\n\n")

      of.write("param u :=\n")
      for j in range(numcontcols):
         of.write("   "+str(j)+"   "+str(u[j])+"\n")
      of.write(";")

      of.close()

if __name__ == "__main__":
   main(sys.argv[1:])
