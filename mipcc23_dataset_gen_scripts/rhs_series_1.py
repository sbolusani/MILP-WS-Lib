#!/usr/bin/python3

# FIXME: getopt does not parse optional arguments. So change to argparse?
import sys, getopt, re, random

def main(argv):
   corefile = ""
   metaofscenfiles = ""
   numservers = 0
   numclients = 0
   numscens = 0
   numscensperinst = 0
   numinsts = 0

   try:
      opts,args=getopt.getopt(argv,"hc:s:i:j:w:n:m:",["help","corefile=","metaofscenfiles=","numservers=","numclients=","numscens=","numscensperinst=","numinsts="])
   except getopt.GetoptError:
      print("parse_sslp_detN.py -c <corefile> -s <metaofscenfiles> -i <numservers> -j <numclients> -w <numscens> -n <numscensperinst> -m <numinsts>")
      sys.exit(2)

   for opt, arg in opts:
      if opt in ["-h", "--help"]:
         print("parse_sslp_detN.py -c <corefile> -s <metaofscenfiles> -i <numservers> -j <numclients> -w <numscens> -n <numscensperinst> -m <numinsts>")
         sys.exit()
      elif opt in ["-c", "--corefile"]:
         corefile = arg
      elif opt in ["-i", "--numservers"]:
         if int(arg) > 0:
            numservers = int(arg)
         else:
            print("Provide valid number of servers!")
            sys.exit()
      elif opt in ["-j", "--numclients"]:
         if int(arg) > 0:
            numclients = int(arg)
         else:
            print("Provide valid number of clients!")
            sys.exit()
      elif opt in ["-w", "--numscens"]:
         if int(arg) > 0:
            numscens = int(arg)
         else:
            print("Provide valid number of scenarios!")
            sys.exit()
      elif opt in ("-s", "--metaofscenfiles"):
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

   scenfilelist = []
   if metaofscenfiles == "":
      scenfilelist.append(corefile.split(".")[0]+".sto")
   else:
      with open(metaofscenfiles) as sfm:
         for line in sfm:
            scenfilelist.append(re.sub("\n", "", line))

   print("Core file: ", corefile)
   print("Scenario files: ", scenfilelist)
   print("Number of servers = ", numservers)
   print("Number of clients = ", numclients)
   print("Number of scenarios = ", numscens)

   obj = ["obj"]
   con2 = []
   for i in range(numservers):
      con2.append("c"+str(i+2))
   cols = 0
   c = [0]*numservers
   q = []
   for i in range(numservers):
      q.append([0]*numclients)
   d = []
   for i in range(numservers):
      d.append([0]*numclients)
   g = [0]*numservers
   t = [0]*numservers
   r = [1]*numclients
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
                  splitvar = splitline[0].split("_")
                  if splitvar[0] == "x" and len(splitvar) == 2:
                     c[int(splitvar[1]) - 1] = int(splitline[2])
                  elif splitvar[0] == "x" and len(splitvar) == 3:
                     g[int(splitvar[1]) - 1] = int(splitline[2])
                  elif splitvar[0] == "y":
                     q[int(splitvar[2])-1][int(splitvar[1])-1] = -int(splitline[2])
               elif splitline[1] in con2:
                  splitvar = splitline[0].split("_")
                  if splitvar[0] == "x" and len(splitvar) == 2:
                     t[int(splitvar[1]) - 1] = int(splitline[2])
                  elif splitvar[0] == "y":
                     d[int(splitvar[2])-1][int(splitvar[1])-1] = -int(splitline[2])
               if len(splitline) == 5:
                  if splitline[3] in obj:
                     splitvar = splitline[0].split("_")
                     if splitvar[0] == "x" and len(splitvar) == 2:
                        c[int(splitvar[1]) - 1] = int(splitline[4])
                     elif splitvar[0] == "x" and len(splitvar) == 3:
                        g[int(splitvar[1]) - 1] = int(splitline[4])
                     elif splitvar[0] == "y":
                        q[int(splitvar[2])-1][int(splitvar[1])-1] = int(splitline[4])
                  elif splitline[3] in con2:
                     splitvar = splitline[0].split("_")
                     if splitvar[0] == "x" and len(splitvar) == 2:
                        t[int(splitvar[1]) - 1] = int(splitline[4])
                     elif splitvar[0] == "y":
                        d[int(splitvar[2])-1][int(splitvar[1])-1] = -int(splitline[4])

   numscen = 0
   scendata = []
   for w in range(numscens):
      scendata.append([0]*numclients)
   for scenfile in scenfilelist:
      with open(scenfile) as sf:
         for line in sf:
            if line.split()[0] == "STOCH":
               instname = line.split()[1]
               if numservers != int(instname.split("_")[1]):
                  print("Mismatched number of servers!")
                  sys.exit()
               if numclients != int(instname.split("_")[2]):
                  print("Mismatched number of clients!")
                  sys.exit()
               continue
            elif line.split()[0] in ["SCENARIOS", "ENDATA"]:
               continue
            elif line.split()[0] == "SC":
               numscen += 1
            else:
               splitline = line.split()
               scendata[numscen-1][int(splitline[1][1:])-numclients-1-1] = int(splitline[2])
   if numscen != numscens:
      print("Mismatched number of scenarios!")
      sys.exit()

   startinstnum = 0
   outputfilebasename = "sslp"
   for instnum in range(numinsts):
      newinstnum = startinstnum + instnum + 1
      outputfile=outputfilebasename+"_"+str(numservers)+"_"+str(numclients)+"_"+str(newinstnum)+".dat"
      print("Writing output file: ", outputfile)

      with open(outputfile, "w") as of:
         of.write("data;\n\n")
         of.write("param numservers := "+str(numservers)+";\n")
         of.write("param numclients := "+str(numclients)+";\n")
         of.write("param numscens := "+str(numscensperinst)+";\n\n")
         of.write("param c :=\n")
         for i in range(numservers):
            of.write("   "+str(i+1)+"   "+str(c[i])+"\n")
         of.write(";\n\n")
         of.write("param q :=\n")
         for i in range(numservers):
            for j in range(numclients):
               of.write("   "+str(i+1)+" "+str(j+1)+"   "+str(q[i][j])+"\n")
         of.write(";\n\n")
         of.write("param g :=\n")
         for i in range(numservers):
            of.write("   "+str(i+1)+" 0   "+str(g[i])+"\n")
         of.write(";\n\n")
         of.write("param t :=\n")
         for i in range(numservers):
            of.write("   "+str(i+1)+"   "+str(t[i])+"\n")
         of.write(";\n\n")
   
         scens2combine = random.sample(range(numscens), numscensperinst)
#         print("Combining scenarios: ", scens2combine)
         of.write("param d :=\n")
         for k in range(len(scens2combine)):
            w = scens2combine[k]
            for i in range(numservers):
               for j in range(numclients):
                  of.write("   "+str(i+1)+" "+str(j+1)+" "+str(k+1)+"   "+str(d[i][j])+"\n")
         of.write(";\n\n")
         of.write("param r :=\n")
         for k in range(len(scens2combine)):
            w = scens2combine[k]
            for i in range(numclients):
               of.write("   "+str(i+1)+" "+str(k+1)+"   "+str(scendata[w][i])+"\n")
         of.write(";")

if __name__ == "__main__":
   main(sys.argv[1:])
