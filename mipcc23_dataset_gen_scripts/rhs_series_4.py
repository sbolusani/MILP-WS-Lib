#!/usr/bin/python3

import sys, getopt, re, numpy as np

def main(argv):
   rhs1datfile = ""
   rhs2datfile = ""
   numinsts = 0
   outputfilebasename = ""

   try:
      opts, args = getopt.getopt(argv,"hf:g:n:o:",["rhs1datfile=","rhs2datfile=","numinsts=","outputfilebasename="])
   except getopt.GetoptError:
      print("sweep_build_synthetic_v2.py -f <rhs1datfile> -g <rhs2datfile> -n <numinsts> -o <outputfilebasename>")
      sys.exit(2)

   for opt, arg in opts:
      if opt == "-h":
         print("sweep_build_synthetic_v2.py -f <rhs1datfile> -g <rhs2datfile> -n <numinsts> -o <outputfilebasename>")
         sys.exit()
      elif opt in ("-f", "--rhs1datfile"):
         rhs1datfile = arg
      elif opt in ("-g", "--rhs2datfile"):
         rhs2datfile = arg
      elif opt in ["-n", "--numinsts"]:
         if int(arg) > 0:
            numinsts = int(arg)
         else:
            print("Provide valid number of instances to create!")
            sys.exit()
      elif opt in ["-o", "--outputfilebasename"]:
         outputfilebasename = arg

   if outputfilebasename == "":
      outputfilebasename = "synthetic"

   print("RHS1 dat file: ", rhs1datfile)
   print("RHS2 dat file: ", rhs2datfile)
   print("Number of instances to create: ", numinsts)
   print("Output file base name: ", outputfilebasename)

   rhs1 = []
   print("Parsing RHS1 file")
   rhs = 0
   with open(rhs1datfile) as df:
      for line in df:
         splitline = line.split()
         if len(splitline) in [0, 1] and rhs == 0:
            continue
         elif splitline[0] == ";" and rhs == 1:
            break
         elif splitline[0] == "param" and splitline[1] == "b":
            rhs = 1
         elif rhs == 1:
            rhs1.append(float(splitline[1]))
   rhs1array = np.array(rhs1)
   if rhs2datfile == "":
      rhs2array = -rhs1array
   else:
      rhs2 = []
      print("Parsing RHS2 file")
      rhs = 0
      with open(rhs2datfile) as df:
         for line in df:
            splitline = line.split()
            if len(splitline) in [0, 1] and rhs == 0:
               continue
            elif splitline[0] == ";" and rhs == 1:
               break
            elif splitline[0] == "param" and splitline[1] == "b":
               rhs = 1
            elif rhs == 1:
               rhs2.append(float(splitline[1]))
      rhs2array = np.array(rhs2)

   alpha = 0 
   rhs1fileID = int(rhs1datfile.split("/")[-1].split("_")[1].split(".")[0])
   if rhs2datfile == "":
      rhs2fileID = rhs1fileID
   else:
      rhs2fileID = int(rhs2datfile.split("/")[-1].split("_")[1].split(".")[0])
   for i in range(numinsts):
      newrhs = rhs1array*(1-alpha) + rhs2array*alpha
      newrhs = np.round(newrhs, 2)
      outputfile = outputfilebasename+"_"+str(rhs1fileID)+"_"+str(rhs2fileID)+"_"+str(i+1)+".dat"
      print("Writing data file: ", outputfile)
      of = open(outputfile, "w")
      prerhs = 1
      rhs = 0
      postrhs = 0
      with open(rhs1datfile) as df:
         for line in df:
            splitline = line.split()
            if prerhs == 1:
               of.write(re.sub("\n", "", line)+"\n")
               if len(splitline) >= 2:
                  if splitline[0] == "param" and splitline[1] == "b":
                     rhs = 1
                     prerhs = 0
            elif rhs == 1:
               if splitline[0] == ";":
                  rhs = 0
                  postrhs = 1
                  of.write(re.sub("\n", "", line)+"\n")
                  continue
               splitline[1] = str(newrhs[int(splitline[0])])
               newline = "   "+splitline[0]+"   "+splitline[1]
               of.write(newline+"\n")
            elif postrhs == 1:
               of.write(re.sub("\n", "", line)+"\n")
            else:
               print("Unknown line in the dat file!")
               sys.exit()
      of.close()
      alpha += 0.01

if __name__ == "__main__":
   main(sys.argv[1:])
