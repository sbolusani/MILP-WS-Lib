#!/usr/bin/python3

import sys, getopt, re, random, numpy as np, math
from copy import copy
from scipy.stats import bernoulli

def readsols(solsfile, numbincols):
   allsols = np.genfromtxt(solsfile, delimiter=',', names=True)

   allsolbinparts = []
   for i in range(len(allsols)):
      allsolbinparts.append(np.flip(np.asarray(allsols[i]).tolist()[1:numbincols+1], axis=0))

   return (allsolbinparts, len(allsols))

def main(argv):
   metaofprobfiles = ""
   solsfile = ""
   numinstsperprob = 0

   try:
      opts,args=getopt.getopt(argv,"hp:s:i:",["metaofprobfiles=","solsfile=","numinstsperprob="])
   except getopt.GetoptError:
      print("parse_ind_insts.py -p <metaofprobfiles> -s <solsfile> -i <numinstsperprob>")
      sys.exit(2)

   for opt, arg in opts:
      if opt == "-h":
         print("parse_ind_insts.py -p <metaofprobfiles> -s <solsfile> -i <numinstsperprob>")
         sys.exit()
      elif opt in ("-p", "--metaofprobfiles"):
         metaofprobfiles = arg
      elif opt in ("-s", "--solsfile"):
         solsfile = arg
      elif opt in ("-i", "--numinstsperprob"):
         if int(arg) > 0:
            numinstsperprob = int(arg)
         else:
            print("Provide valid number of instances to create!")
            sys.exit()

   numbincols = 1457
   (allsolbinparts, numsols) = readsols(solsfile, numbincols)

   with open(metaofprobfiles) as pfm:
      for line in pfm:
         splitline = line.split()
         probfile = splitline[0]
         probfilebasename = probfile.split("/")[-1][:-4]
         numcols = int(splitline[1])
         partialvecfracs = [0.175, 0.225]
         numinstspertype = math.ceil(numinstsperprob/(len(partialvecfracs)))
         filenumoffset = 0
         solnumoffset = 400
         for p in range(len(partialvecfracs)):
            partialvecfrac = partialvecfracs[p]
            print("Building new bounds for ", probfilebasename, " with partialvecfrac = ", partialvecfrac)
            for i in range(numinstspertype):
               currsolbinpart = allsolbinparts[i]  #[numsols - 1 - i - solnumoffset]
               assert(len(currsolbinpart) == numbincols)
#               outlbdatfile = probfilebasename+"_"+str(partialvecfrac)+"p_"+str(i + filenumoffset)+"_lowerbounds.txt"
#               outubdatfile = probfilebasename+"_"+str(partialvecfrac)+"p_"+str(i + filenumoffset)+"_upperbounds.txt"
#
#               print("Writing dat files ", outlbdatfile, " and ", outubdatfile)
#               with open(outlbdatfile, "w") as olbdf, open(outubdatfile, "w") as oubdf:
#                  for j in range(numbincols):
#                     if currsolbinpart[j] == 0:
#                        olbdf.write(str(0)+"\n")
#                        oubdf.write(str(0)+"\n")
#                     elif currsolbinpart[j] == 1:
#                        olbdf.write(str(1)+"\n")
#                        oubdf.write(str(1)+"\n")
#                     else:
#                        print("Unknown value for a binary variable!")
#                        sys.exit()
#

               outfile = probfilebasename+"_"+str(partialvecfrac)+"p_"+str(i + filenumoffset)+".mps"
               print("Writing MPS file ", outfile)
               rows = 0
               cols = 0
               rhs = 0
               bounds = 0
               binchangeind = bernoulli.rvs(partialvecfrac, size=numbincols)
               with open(probfile) as pf, open(outfile, "w") as of1:
                  obj = 0
                  for line in pf:
                     if line.split()[0] in ["*", "OBJSENSE", "MIN", "RANGES"]:
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
                     elif rows == 1 or cols == 1 or rhs == 1:
                        of1.write(re.sub("\n", "", line)+"\n")
                     elif bounds == 1:
                        splitline = line.split()
                        numwhitespaces = [len(j) for j in re.findall('\s+', re.sub("\n", "", line))]
                        colnum = int(splitline[2][1:])
                        if splitline[0] == "BV":
                           assert(colnum < numbincols)
                           if binchangeind[colnum] == 1:
                              of1.write(re.sub("\n", "", line)+"\n")
                              splitline[0] = "FX"
                              splitline.append(str(int(currsolbinpart[colnum])))
                              numwhitespaces[3] -= 2

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
