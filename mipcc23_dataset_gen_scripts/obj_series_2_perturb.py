#!/usr/bin/python3

import sys, getopt, re, random, numpy as np, math
from copy import copy

def perturbObj(origobj, percentchange, numinstsperprob):
   newobjs = []
   size2change = len(origobj)

   for i in range(numinstsperprob):
      percentchanges = np.random.uniform(-percentchange/100, percentchange/100, size=size2change)
      boolchanges = np.random.choice([1,1], size2change)
      newobjs.append(np.round(origobj + np.multiply(origobj, np.multiply(percentchanges, boolchanges)), 15))

   return newobjs


def main(argv):
   metaofprobfiles = ""
   numinstsperprob = 0
   numcols = 0

   try:
      opts,args=getopt.getopt(argv,"hp:i:",["metaofprobfiles=","numinstsperprob="])
   except getopt.GetoptError:
      print("parse_perturb.py -p <metaofprobfiles> -i <numinstsperprob>")
      sys.exit(2)

   for opt, arg in opts:
      if opt == "-h":
         print("parse_perturb.py -p <metaofprobfiles> -i <numinstsperprob>")
         sys.exit()
      elif opt in ("-p", "--metaofprobfiles"):
         metaofprobfiles = arg
      elif opt in ("-i", "--numinstsperprob"):
         if int(arg) > 0:
            numinstsperprob = int(arg)
         else:
            print("Provide valid number of instances to create!")
            sys.exit()

   objdict = {}
   probfiles = []
   allnumcols = {}
   with open(metaofprobfiles) as pfm:
      for line in pfm:
         splitline = line.split()
         probfile = splitline[0] #re.sub("\n", "", line)
         probfiles.append(probfile)
         probfilebasename = probfile.split("/")[-1][:-4]
         allnumcols[probfilebasename] = int(splitline[1])
         numcols = allnumcols[probfilebasename]
         with open(probfile) as pf:
            obj = 0
            for pline in pf:
               splitline = pline.split()
               if splitline[0] in ["*", "OBJSENSE", "MIN", "RANGES"]:
                  continue
               elif splitline[0] == "NAME":
                  objdict[probfilebasename] = np.zeros(numcols)
                  continue
               elif splitline[0] == "COLUMNS":
                  obj = 1
                  continue
               elif splitline[0] == "RHS":
                  break

               if obj == 1:
                  if splitline[1]  == "Obj":
                     objdict[probfilebasename][int(splitline[0][1:])] = float(splitline[2])
                  if len(splitline) > 3 and splitline[3] == "Obj":
                     objdict[probfilebasename][int(splitline[0][1:])] = float(splitline[4])

   for probfile in probfiles:
      probfilebasename = probfile.split("/")[-1][:-4]
      numcols = allnumcols[probfilebasename]
      print("Building new objs for ", probfilebasename)
      percentchange = 250
      newobjs = perturbObj(objdict[probfilebasename], percentchange, numinstsperprob)
      filenumoffset = 100
      for i in range(numinstsperprob):
         newobj1 = np.round(newobjs[i], 15).tolist()
         assert(len(newobj1) == numcols)
         outdatfile = probfilebasename+"_"+str(percentchange)+"p_"+str(i+filenumoffset)+"_obj.txt"

         print("Writing dat file ", outdatfile)
         with open(outdatfile, "w") as odf:
            for j in range(numcols):
               if objdict[probfilebasename][j] == 0:
                  odf.write(str(0.00)+"\n")
               else:
                  odf.write(str(newobj1[j])+"\n")

         outfile1 = probfilebasename+"_"+str(percentchange)+"p_"+str(i+filenumoffset)+".mps"
         print("Writing MPS file ", outfile1)
         rows = 0
         cols = 0
         rhs = 0
         bounds = 0
         with open(probfile) as pf, open(outfile1, "w") as of1:
            obj = 0
            for line in pf:
               if line.split()[0] in ["*", "OBJSENSE", "MIN", "RANGES"]:
                  continue
               elif line.split()[0] == "NAME":
                  of1.write("NAME        "+outfile1[:-4]+"\n")
               elif line.split()[0] == "ROWS":
                  rows = 1
                  cols = 0
                  rhs = 0
                  bounds = 0
                  of1.write(re.sub("\n", "", line)+"\n")
               elif line.split()[0] == "COLUMNS":
                  rows = 0
                  cols = 1
                  rhs = 0
                  bounds = 0
                  of1.write(re.sub("\n", "", line)+"\n")
               elif line.split()[0] == "RHS":
                  rows = 0
                  cols = 0
                  rhs = 1
                  bounds = 0
                  of1.write(re.sub("\n", "", line)+"\n")
               elif line.split()[0] == "BOUNDS":
                  rows = 0
                  cols = 0
                  rhs = 0
                  bounds = 1
                  of1.write(re.sub("\n", "", line)+"\n")
               elif line.split()[0] == "ENDATA":
                  rows = 0
                  cols = 0
                  rhs = 0
                  bounds = 0
                  of1.write(re.sub("\n", "", line)+"\n")
               elif rows == 1 or rhs == 1 or bounds == 1:
                  of1.write(re.sub("\n", "", line)+"\n")
               elif cols == 1:
                  splitline = line.split()
                  splitline1 = line.split()
                  numwhitespaces1 = [len(j) for j in re.findall('\s+', re.sub("\n", "", line))]
                  index = -1
                  if splitline[1] == "Obj":
                     index = 1
                  elif len(splitline) == 5 and splitline[3] == "Obj":
                     index = 3
                  if index > 0:
                     colnum = int(splitline[0][1:])
                     if objdict[probfilebasename][colnum] != 0:
                        if len(splitline[index + 1]) > len(str(newobj1[colnum])):
                           numwhitespaces1[index+1] += len(splitline[index + 1]) - len(str(newobj1[colnum]))
                        elif len(splitline[index + 1]) < len(str(newobj1[colnum])):
                           numwhitespaces1[index+1] -= len(str(newobj1[colnum])) - len(splitline[index + 1])
                        splitline1[index + 1] = str(newobj1[colnum])
                  newline1 = ""
                  for ind in range(len(splitline)):
                     newline1 += " "*numwhitespaces1[ind]
                     newline1 += splitline1[ind]
                  of1.write(newline1+"\n")
               else:
                  print("ALERT: Unknown line in MPS file!!")
                  sys.exit()

if __name__ == "__main__":
   main(sys.argv[1:])
