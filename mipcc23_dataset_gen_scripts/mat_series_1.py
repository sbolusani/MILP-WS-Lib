#!/usr/bin/python3

# FIXME: getopt does not parse optional arguments. So change to argparse?
import sys, getopt, re, random

def main(argv):
   corefile = ""
   metaofscenfiles = ""
   numcontcols = 0
   numfamilytypes = 0
   numscens = 0
   numscensperinst = 0
   numinsts = 0
   alpha = 0
   outputfilebasename = ""

   try:
      opts,args=getopt.getopt(argv,"hc:s:i:j:w:n:m:a:o:",["help","corefile=","metaofscenfiles=","numcontcols=","numfamilytypes=","numscens=","numscensperinst=","numinsts=","alpha=","outputfilebasename="])
   except getopt.GetoptError:
      print("parse_vaccine_detN.py -c <corefile> -s <metaofscenfiles> -i <numcontcols> -j <numfamilytypes> -w <numscens> -n <numscensperinst> -m <numinsts> -a <alpha> -o <outputfilebasename>")
      sys.exit(2)

   for opt, arg in opts:
      if opt in ["-h", "--help"]:
         print("parse_vaccine_detN.py -c <corefile> -s <metaofscenfiles> -i <numcontcols> -j <numfamilytypes> -w <numscens> -n <numscensperinst> -m <numinsts> -a <alpha> -o <outputfilebasename>")
         sys.exit()
      elif opt in ["-c", "--corefile"]:
         corefile = arg
      elif opt in ["-i", "--numcontcols"]:
         if int(arg) > 0:
            numcontcols = int(arg)
         else:
            print("Provide valid number of continuous columns!")
            sys.exit()
      elif opt in ["-j", "--numfamilytypes"]:
         if int(arg) > 0:
            numfamilytypes = int(arg)
         else:
            print("Provide valid number of family types!")
            sys.exit()
      elif opt in ["-w", "--numscens"]:
         if int(arg) > 0:
            numscens = int(arg)
         else:
            print("Provide valid number of scenarios!")
            sys.exit()
      elif opt in ["-s", "--metaofscenfiles"]:
         metaofscenfiles = arg
      elif opt in ["-n", "--numscensperinst"]:
         if int(arg) > 0:
            numscensperinst = int(arg)
         else:
            print("Provide valid number of scenarios per instance!")
            sys.exit()
      elif opt in ["-m", "--numinsts"]:
         if int(arg) > 0:
            numinsts = int(arg)
         else:
            print("Provide valid number of instances to create!")
            sys.exit()
      elif opt in ["-a", "--alpha"]:
         if float(arg) > 0:
            alpha = float(arg)
         else:
            print("Provide valid number for alpha!")
            sys.exit()
      elif opt in ["-o", "--outputfilebasename"]:
         outputfilebasename = arg

   scenfilelist = []
   if metaofscenfiles == "":
      scenfilelist.append(corefile.split(".")[0]+".sto")
   else:
      with open(metaofscenfiles) as sfm:
         for line in sfm:
            scenfilelist.append(re.sub("\n", "", line))

   print("Core file: ", corefile)
   print("Scenario files: ", scenfilelist)
   print("Number of cont cols = ", numcontcols)
   print("Number of family types = ", numfamilytypes)
   print("Number of scenarios = ", numscens)
   print("Number of scenarios per instance = ", numscensperinst)
   print("Number of instances to create = ", numinsts)
   print("Alpha: ", alpha)

   obj = ["obj"]
   con1 = []
   for i in range(numfamilytypes):
      con1.append("c"+str(i+1))
   con2 = ["c"+str(numfamilytypes+1)]
   cols = 0
   c = [0]*numcontcols
   g = []
   for i in range(numfamilytypes):
      g.append([0]*numcontcols)
   a = []
   for i in range(numcontcols):
      a.append([0]*numscens)
   bigM = [0]*numscens
   with open(corefile) as cf:
      for line in cf:
         if line.split()[0] in ["NAME", "ENDATA", "ROWS", "BOUNDS", "RHS"]:
            cols = 0
            continue
         elif line.split()[0] in ["COLUMNS"]:
            cols = 1
         elif cols == 1:
            if line.split()[0] in ["MARK0000", "MARK0001"]:
               continue
            else:
               splitline = line.split()
               if splitline[1] in obj:
                  c[int(splitline[0][1:]) - 1] = float(splitline[2])
               elif splitline[1] in con1:
                  g[int(splitline[1][1:]) - 1][int(splitline[0][1:]) - 1] = int(splitline[2])
               if len(splitline) == 5:
                  if splitline[3] in obj:
                     c[int(splitline[0][1:]) - 1] = float(splitline[4])
                  elif splitline[3] in con1:
                     g[int(splitline[3][1:]) - 1][int(splitline[0][1:]) - 1] = int(splitline[4])

   numscen = 0
   for scenfile in scenfilelist:
      with open(scenfile) as sf:
         for line in sf:
            if line.split()[0] in ["STOCH", "SCENARIOS", "ENDATA"]:
               continue
            elif line.split()[0] == "SC":
               numscen += 1
            else:
               splitline = line.split()
               if int(splitline[1][1:]) == numfamilytypes+1:
                  a[int(splitline[0][1:])-1][numscen-1] = float(splitline[2])
                  if float(splitline[2]) > 0.0:
                     bigM[numscen-1] += float(splitline[2])
               else:
                  print(line)
                  print("Unknown data in scenario file!")
                  sys.exit()
   if numscen != numscens:
      print("Mismatched number of scenarios!")
      sys.exit()

   startinstnum = 20
   if outputfilebasename == "":
      outputfilebasename = "vaccine_"
   for instnum in range(numinsts):
      newinstnum = startinstnum + instnum + 1
      outputfile=outputfilebasename+"_"+str(newinstnum)+".dat"
      print("Writing output file: ", outputfile)

      with open(outputfile, "w") as of:
         of.write("data;\n\n")
         of.write("param numcontcols := "+str(numcontcols)+";\n")
         of.write("param numfamilytypes := "+str(numfamilytypes)+";\n")
         of.write("param numscens := "+str(numscensperinst)+";\n")
         of.write("param alpha := "+str(alpha)+";\n\n")
         of.write("param c :=\n")
         for i in range(numcontcols):
            of.write("   "+str(i+1)+"   "+str(c[i])+"\n")
         of.write(";\n\n")
         of.write("param g :=\n")
         for i in range(numfamilytypes):
            for j in range(numcontcols):
               of.write("   "+str(i+1)+" "+str(j+1)+"   "+str(g[i][j])+"\n")
         of.write(";\n\n")
         of.write("param a :=\n")
         scens2combine = random.sample(range(numscens), numscensperinst)
         for w in range(numscensperinst):
            for i in range(numcontcols):
               of.write("   "+str(i+1)+" "+str(w+1)+"   "+str(a[i][scens2combine[w]])+"\n")
         of.write(";\n\n")
         of.write("param bigM :=\n")
         for w in range(numscensperinst):
            of.write("   "+str(w+1)+"   "+str(bigM[scens2combine[w]])+"\n")
         of.write(";")
   
if __name__ == "__main__":
   main(sys.argv[1:])
