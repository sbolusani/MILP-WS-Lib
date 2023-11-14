#!/usr/bin/python3

import sys, getopt, re, numpy as np, math
from copy import copy

def buildRHSs(origrhs, percentchange, numinstsperprob):
   size2change = len(origrhs)

   newrhss = []
   for i in range(numinstsperprob):
      percentchanges = np.random.uniform(-percentchange/100, percentchange/100, size=size2change)
      boolchanges = np.random.choice([0,1], size2change)
      newrhss.append(np.round(origrhs + np.multiply(origrhs, np.multiply(percentchanges, boolchanges)), 8))
   return newrhss

def buildObjs(origobj, percentchange, numinstsperprob):
   size2change = len(origobj)

   newobjs = []
   for i in range(numinstsperprob):
      percentchanges = np.random.uniform(-percentchange/100, percentchange/100, size=size2change)
      boolchanges = np.random.choice([0,1], size2change)
      newobjs.append(np.round(origobj + np.multiply(origobj, np.multiply(percentchanges, boolchanges)), 2))
   return newobjs

def main(argv):
   metaofprobfiles = ""
   numinstsperprob = 0
   numrows = 0

   try:
      opts,args=getopt.getopt(argv,"hp:i:",["metaofprobfiles=","numinstsperprob="])
   except getopt.GetoptError:
      print("parse_stats_genprob.py -p <metaofprobfiles> -i <numinstsperprob>")
      sys.exit(2)

   for opt, arg in opts:
      if opt == "-h":
         print("parse_stats_genprob.py -p <metaofprobfiles> -i <numinstsperprob>")
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
   objdict = {}
   probfiles = []
   allnumrows = {}
   allnumcols = {}
   with open(metaofprobfiles) as pfm:
      for line in pfm:
         splitline = line.split()
         probfile = splitline[0] #re.sub("\n", "", line)
         probfiles.append(probfile)
         probfilebasename = probfile.split("/")[-1][:-4]
         allnumrows[probfilebasename] = int(splitline[1])
         allnumcols[probfilebasename] = int(splitline[2])
         numrows = allnumrows[probfilebasename]
         numcols = allnumcols[probfilebasename]
         rhsdict[probfilebasename] = np.zeros(numrows)
         objdict[probfilebasename] = np.zeros(numcols)
         with open(probfile) as pf:
            rhs = 0
            cols = 0
            for pline in pf:
               splitline = pline.split()
               if splitline[0] == "COLUMNS":
                  cols = 1
                  rhs = 0
                  continue
               elif splitline[0] == "RHS" and len(splitline) == 1:
                  rhs = 1
                  cols = 0
                  continue
               elif splitline[0] == "BOUNDS":
                  rhs = 0
                  cols = 0
                  break

               if cols == 1:
                  if splitline[0][0]  == "x":
                     if splitline[1]  == "Obj":
                        objdict[probfilebasename][int(splitline[0][1:])] = -float(splitline[2])
                     if len(splitline) > 3:
                        if splitline[3]  == "Obj":
                           objdict[probfilebasename][int(splitline[0][1:])] = -float(splitline[4])
               elif rhs == 1:
                  if splitline[0]  == "RHS":
                     rhsdict[probfilebasename][int(splitline[1][1:])] = float(splitline[2])
                     if len(splitline) > 3:
                        rhsdict[probfilebasename][int(splitline[3][1:])] = float(splitline[4])

   for probfile in probfiles:
      probfilebasename = probfile.split("/")[-1][:-4]
      numrows = allnumrows[probfilebasename]
      numcols = allnumcols[probfilebasename]
      percentchange = 20
      print("Building new rhs for ", probfilebasename)
      newrhss = buildRHSs(rhsdict[probfilebasename], percentchange, numinstsperprob)
      print("Building new obj for ", probfilebasename)
      newobjs = buildObjs(objdict[probfilebasename], percentchange, numinstsperprob)
      temp_counter = 200
      for i in range(numinstsperprob):
         newrhs = newrhss[i].tolist()
         newobj = newobjs[i].tolist()
         assert(len(newrhs) == numrows)
         assert(len(newobj) == numcols)

         outrhsdatfile = probfilebasename+"_"+str(percentchange)+"p_"+str(i + temp_counter)+"_rhs.txt"
         print("Writing dat file ", outrhsdatfile)
         with open(outrhsdatfile, "w") as odf:
            for j in range(numrows):
               odf.write(str(newrhs[j])+"\n")

         outobjdatfile = probfilebasename+"_"+str(percentchange)+"p_"+str(i + temp_counter)+"_obj.txt"
         print("Writing dat file ", outobjdatfile)
         with open(outobjdatfile, "w") as odf:
            for j in range(numcols):
               odf.write(str(newobj[j])+"\n")

         outfile = probfilebasename+"_"+str(percentchange)+"p_"+str(i + temp_counter)+".mps"
         print("Writing MPS file ", outfile)
         rows = 0
         cols = 0
         rhs = 0
         bounds = 0
         with open(probfile) as pf, open(outfile, "w") as of1:
            for line in pf:
               if line.split()[0] in ["*", "OBJSENSE", "MIN", "MAX", "RANGES"]:
                  continue
               elif line.split()[0] == "NAME":
                  of1.write("NAME        "+outfile[:-4]+"\n")
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
               elif rows == 1 or bounds == 1:
                  of1.write(re.sub("\n", "", line)+"\n")
               elif cols == 1:
                  splitline = line.split()
                  numwhitespaces = [len(j) for j in re.findall('\s+', re.sub("\n", "", line))]
                  index = -1
                  if splitline[1] == "Obj":
                     index = 1
                  elif len(splitline) > 3 and splitline[3] == "Obj":
                     index = 3
                  if index > 0:
                     colnum = int(splitline[0][1:])
                     if objdict[probfilebasename][colnum] not in [-0, 0]:
                        if len(splitline[index + 1]) > len(str(newobj[colnum])):
                           numwhitespaces[index+1] += len(splitline[index + 1]) - len(str(newobj[colnum]))
                        elif len(splitline[index + 1]) < len(str(newobj[colnum])):
                           numwhitespaces[index+1] -= len(str(newobj[colnum])) - len(splitline[index + 1])
                        splitline[index + 1] = str(newobj[colnum])
                  newline = ""
                  for ind in range(len(splitline)):
                     newline += " "*numwhitespaces[ind]
                     newline += splitline[ind]
                  of1.write(newline+"\n")
               elif rhs == 1:
                  splitline = line.split()
                  numwhitespaces = [len(j) for j in re.findall('\s+', re.sub("\n", "", line))]
                  index = 1
                  rownum = int(splitline[1][1:])
                  if len(splitline[index + 1]) > len(str(newrhs[rownum])):
                     numwhitespaces[index+1] += len(splitline[index + 1]) - len(str(newrhs[rownum]))
                  elif len(splitline[index + 1]) < len(str(newrhs[rownum])):
                     numwhitespaces[index+1] -= len(str(newrhs[rownum])) - len(splitline[index + 1])
                  splitline[index + 1] = str(newrhs[rownum])
                  if len(splitline) > 3:
                     index = 3
                     rownum = int(splitline[3][1:])
                     if len(splitline[index + 1]) > len(str(newrhs[rownum])):
                        numwhitespaces[index+1] += len(splitline[index + 1]) - len(str(newrhs[rownum]))
                     elif len(splitline[index + 1]) < len(str(newrhs[rownum])):
                        numwhitespaces[index+1] -= len(str(newrhs[rownum])) - len(splitline[index + 1])
                     splitline[index + 1] = str(newrhs[rownum])
                  newline = ""
                  for ind in range(len(splitline)):
                     newline += " "*numwhitespaces[ind]
                     newline += splitline[ind]
                  of1.write(newline+"\n")
               else:
                  print("ALERT: Unknown line in MPS file!!")
                  sys.exit()

if __name__ == "__main__":
   main(sys.argv[1:])
