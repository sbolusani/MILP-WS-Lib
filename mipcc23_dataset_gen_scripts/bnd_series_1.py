#!/usr/bin/python3

import sys, getopt, re, random, numpy as np, math
from scipy.stats import bernoulli

def buildbounds(origbounds, partialvecfrac, percentchange, numinstsperprob):
   size2change = len(origbounds)

   newboundslist = []
   for i in range(numinstsperprob):
      percentchanges = np.random.uniform(-percentchange/100, -percentchange/100, size=size2change)
      boolchanges = bernoulli.rvs(partialvecfrac, size=size2change)
      newboundslist.append(np.round(origbounds + np.multiply(origbounds, np.multiply(percentchanges, boolchanges)), 0).astype(int))
   return newboundslist


def main(argv):
   metaofprobfiles = ""
   numinstsperprob = 0

   try:
      opts,args=getopt.getopt(argv,"hp:i:",["metaofprobfiles=","numinstsperprob="])
   except getopt.GetoptError:
      print("parse_ind_insts.py -p <metaofprobfiles> -i <numinstsperprob>")
      sys.exit(2)

   for opt, arg in opts:
      if opt == "-h":
         print("parse_ind_insts.py -p <metaofprobfiles> -i <numinstsperprob>")
         sys.exit()
      elif opt in ("-p", "--metaofprobfiles"):
         metaofprobfiles = arg
      elif opt in ("-i", "--numinstsperprob"):
         if int(arg) > 0:
            numinstsperprob = int(arg)
         else:
            print("Provide valid number of instances to create!")
            sys.exit()

   boundsdict = {}
   bounds2change = {}
   uselastcolbound = {}
   probfiles = []
   allnumcols = {}
   colindstart = 2993
   specialcol = 3115
   acolnum = 2995
   bcolnum = 3113
   ccolnum = 3116
   with open(metaofprobfiles) as pfm:
      for line in pfm:
         splitline = line.split()
         probfile = splitline[0] #re.sub("\n", "", line)
         probfiles.append(probfile)
         probfilebasename = probfile.split("/")[-1][:-4]
         allnumcols[probfilebasename] = int(splitline[1])
         numcols = allnumcols[probfilebasename]
         boundsdict[probfilebasename] = np.ones(numcols).astype(int)
         bounds2change[probfilebasename] = np.zeros(numcols)
         uselastcolbound[probfilebasename] = np.zeros(numcols)
         with open(probfile) as pf:
            bounds = 0
            for pline in pf:
               splitline = pline.split()
               if splitline[0] == "BOUNDS":
                  bounds = 1
                  continue
               elif splitline[0] == "ENDATA":
                  bounds = 0
                  break

               if bounds == 1:
                  colind = int(splitline[2][1:])
                  if colind >= colindstart:
                     assert(splitline[0] == "UP")
                     boundsdict[probfilebasename][colind] = float(splitline[3])
                     if boundsdict[probfilebasename][colind] == boundsdict[probfilebasename][colind - 1]:
                        uselastcolbound[probfilebasename][colind] = 1
                        bounds2change[probfilebasename][colind] = 0
                     else:
                        bounds2change[probfilebasename][colind] = boundsdict[probfilebasename][colind]
         tempsum = 0
         for i in range(acolnum, bcolnum, 3):
            tempsum += boundsdict[probfilebasename][i]
         tempsum += boundsdict[probfilebasename][ccolnum]
         assert(tempsum == bounds2change[probfilebasename][specialcol])
         bounds2change[probfilebasename][specialcol] = 0

   for probfile in probfiles:
      probfilebasename = probfile.split("/")[-1][:-4]
      numcols = allnumcols[probfilebasename]
      partialvecfracs = [0.2, 0.4]
      percentchanges = [100]
      numinstspertype = math.ceil(numinstsperprob/(len(partialvecfracs)*len(percentchanges)))
      filenumoffset = 0
      for partialvecfrac in partialvecfracs:
         for percentchange in percentchanges:
            print("Building new bounds for ", probfilebasename, "with partialvecfrac = ", partialvecfrac, " and percentchange = ", percentchange)
            newboundslist = buildbounds(bounds2change[probfilebasename], partialvecfrac, percentchange, numinstspertype)
            for i in range(numinstspertype):
               newbounds = newboundslist[i].tolist()
               assert(newbounds[specialcol] == 0)
               for j in range(acolnum, bcolnum, 3):
                  newbounds[specialcol] += newbounds[j]
               newbounds[specialcol] += newbounds[ccolnum]
               assert(len(newbounds) == numcols)
               outdatfile = probfilebasename+"_"+str(partialvecfrac)+"f_"+str(percentchange)+"p_"+str(i + filenumoffset)+"_bounds.txt"

               print("Writing dat file ", outdatfile)
               with open(outdatfile, "w") as odf:
                  for j in range(numcols):
                     if newbounds[j] != 0:
                        odf.write(str(newbounds[j])+"\n")
                     elif uselastcolbound[probfilebasename][j] == 1:
                        odf.write(str(newbounds[j - 1])+"\n")
                     else:
                        odf.write(str(boundsdict[probfilebasename][j])+"\n")

               outfile1 = probfilebasename+"_"+str(partialvecfrac)+"f_"+str(percentchange)+"p_"+str(i + filenumoffset)+".mps"
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
                     elif rows == 1 or cols == 1 or rhs == 1:
                        of1.write(re.sub("\n", "", line)+"\n")
                     elif bounds == 1:
                        splitline = line.split()
                        numwhitespaces = [len(j) for j in re.findall('\s+', re.sub("\n", "", line))]
                        index = 2
                        colnum = int(splitline[2][1:])
                        if colnum >= colindstart:
                           assert(splitline[0] == "UP")
                           bound2compare = -1
                           if newbounds[colnum] != 0:
                              bound2compare = newbounds[colnum]
                           elif uselastcolbound[probfilebasename][colnum] == 1:
                              bound2compare = newbounds[colnum - 1]
                           if bound2compare >= 0:
                              if len(splitline[index + 1]) > len(str(bound2compare)):
                                 numwhitespaces[index+1] += len(splitline[index + 1]) - len(str(bound2compare))
                              elif len(splitline[index + 1]) < len(str(bound2compare)):
                                 numwhitespaces[index+1] -= len(str(bound2compare)) - len(splitline[index + 1])
                              splitline[index + 1] = str(bound2compare)
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
