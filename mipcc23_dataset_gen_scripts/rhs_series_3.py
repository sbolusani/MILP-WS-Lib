#!/usr/bin/python3

import sys, getopt, re, random, numpy as np, math
from copy import copy

def buildRHSs(origdenserhs, percentchange, numinstsperprob):
   size2change = len(origdenserhs)

   newrhss = []
   for i in range(numinstsperprob):
      percentchanges = np.random.uniform(-percentchange/100, percentchange/100, size=size2change)
      newrhss.append(np.round(origdenserhs + np.multiply(origdenserhs, percentchanges)))
   return newrhss


def main(argv):
   metaofprobfiles = ""
   numinstsperprob = 0
   numrows = 0

   try:
      opts,args=getopt.getopt(argv,"hp:i:",["metaofprobfiles=","numinstsperprob="])
   except getopt.GetoptError:
      print("parse_glass4.py -p <metaofprobfiles> -i <numinstsperprob>")
      sys.exit(2)

   for opt, arg in opts:
      if opt == "-h":
         print("parse_glass4.py -p <metaofprobfiles> -i <numinstsperprob>")
         sys.exit()
      elif opt in ("-p", "--metaofprobfiles"):
         metaofprobfiles = arg
      elif opt in ("-i", "--numinstsperprob"):
         if int(arg) > 0:
            numinstsperprob = int(arg)
         else:
            print("Provide valid number of instances to create!")
            sys.exit()

   rhsdict = {}
   probfiles = []
   allnumrows = {}
   with open(metaofprobfiles) as pfm:
      for line in pfm:
         splitline = line.split()
         probfile = splitline[0] #re.sub("\n", "", line)
         probfiles.append(probfile)
         probfilebasename = probfile.split("/")[-1][:-4]
         allnumrows[probfilebasename] = int(splitline[1])
         numrows = allnumrows[probfilebasename]
         rhsdict[probfilebasename] = np.zeros(numrows)
         with open(probfile) as pf:
            rhs = 0
            for pline in pf:
               splitline = pline.split()
               if splitline[0] == "RHS" and len(splitline) == 1:
                  rhs = 1
                  continue
               elif splitline[0] == "BOUNDS":
                  rhs = 0
                  break

               if rhs == 1:
                  if splitline[0]  == "RHS":
                     rhsdict[probfilebasename][int(splitline[1][1:])] = float(splitline[2])
                     if len(splitline) > 3:
                        rhsdict[probfilebasename][int(splitline[3][1:])] = float(splitline[4])

   for probfile in probfiles:
      probfilebasename = probfile.split("/")[-1][:-4]
      numrows = allnumrows[probfilebasename]
      print("Building new rhs for ", probfilebasename)
      modrhs = np.copy(rhsdict[probfilebasename])
      for i in range(numrows):
         if modrhs[i] <= 0:
            modrhs[i] = 0
         if modrhs[i] == 1:
            modrhs[1] = 5
      percentchange = 20
      newrhss = buildRHSs(modrhs, percentchange, numinstsperprob)
      temp_counter = 0
      for i in range(numinstsperprob):
         newrhs = newrhss[i].tolist()
         assert(len(newrhs) == numrows)
         outdatfile = probfilebasename+"_"+str(percentchange)+"p_"+str(i + temp_counter)+"_rhs.txt"

         print("Writing dat file ", outdatfile)
         with open(outdatfile, "w") as odf:
            for j in range(numrows):
               if modrhs[j] == 0:
                  odf.write(str(rhsdict[probfilebasename][j])+"\n")
               else:
                  odf.write(str(newrhs[j])+"\n")

         outfile1 = probfilebasename+"_"+str(percentchange)+"p_"+str(i + temp_counter)+".mps"
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
               elif line.split()[0] == "RHS" and len(line.split()) == 1:
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
               elif rows == 1 or cols == 1 or bounds == 1:
                  of1.write(re.sub("\n", "", line)+"\n")
               elif rhs == 1:
                  splitline = line.split()
                  numwhitespaces = [len(j) for j in re.findall('\s+', re.sub("\n", "", line))]
                  index = 1
                  rownum = int(splitline[1][1:])
                  if modrhs[rownum] != 0:
                     if len(splitline[index + 1]) > len(str(newrhs[rownum])):
                        numwhitespaces[index+1] += len(splitline[index + 1]) - len(str(newrhs[rownum]))
                     elif len(splitline[index + 1]) < len(str(newrhs[rownum])):
                        numwhitespaces[index+1] -= len(str(newrhs[rownum])) - len(splitline[index + 1])
                     splitline[index + 1] = str(newrhs[rownum])
                  if len(splitline) > 3:
                     index = 3
                     rownum = int(splitline[3][1:])
                     if modrhs[rownum] != 0:
                        if len(splitline[index + 1]) > len(str(newrhs[rownum])):
                           numwhitespaces[index+1] += len(splitline[index + 1]) - len(str(newrhs[rownum]))
                        elif len(splitline[index + 1]) < len(str(newrhs[rownum])):
                           numwhitespaces[index+1] -= len(str(newrhs[rownum])) - len(splitline[index + 1])
                        splitline[index + 1] = str(newrhs[rownum])
                  newline1 = ""
                  for ind in range(len(splitline)):
                     newline1 += " "*numwhitespaces[ind]
                     newline1 += splitline[ind]
                  of1.write(newline1+"\n")
               else:
                  print("ALERT: Unknown line in MPS file!!")
                  sys.exit()

if __name__ == "__main__":
   main(sys.argv[1:])
